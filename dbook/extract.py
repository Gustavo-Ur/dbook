# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Gustavo de Urzêda Abreu

"""Camada durável: livro → unidades de texto limpas, com página e secção.

Tudo aqui é AGNÓSTICO ao modelo de AI — é o trabalho caro (extrair, OCR, limpar,
partir) que se faz uma vez e se partilha. Portado e afinado a partir do
descodificador da Aurora (services/decoder_service.py), mas sem dependências do
Django, para a ferramenta ser autónoma.
"""

import os
import re
from collections import Counter

# Limiar de "só-imagem": abaixo disto o PDF não tem texto extraível (é um scan).
_MIN_TEXT = 30

# Chunks pequenos: recuperação mais precisa e prompt menor. Por frases (nunca
# cortadas a meio), empacotadas até ~CHUNK_WORDS com sobreposição.
CHUNK_WORDS = 250
OVERLAP_WORDS = 40


def extract_pages(caminho, ocr=False, dpi=300, progress=None):
    """Lista de (nº_página, texto). Para .txt, uma só 'página' (nº 1).

    PDF só-imagem (scan) só passa por OCR se `ocr=True` — OCR de um livro custa
    minutos a horas e não deve disparar por acidente.
    """
    suf = caminho.suffix.lower()
    if suf == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(caminho))
        paginas = [(i + 1, (p.extract_text() or "")) for i, p in enumerate(reader.pages)]
        tem_texto = sum(len(t.strip()) for _, t in paginas) >= _MIN_TEXT
        if tem_texto:
            return paginas
        if not ocr:
            raise ValueError(
                "PDF só-imagem (sem texto extraível). Re-corre com ocr=True / --ocr."
            )
        return _ocr_pdf(caminho, dpi=dpi, progress=progress)

    if suf in (".txt", ".md"):
        return [(1, caminho.read_text(encoding="utf-8", errors="ignore"))]

    raise ValueError(f"Extensão não suportada: {suf} (usa .pdf/.txt/.md)")


def _ocr_pdf(caminho, dpi=300, progress=None):
    """OCR offline: rasteriza cada página (PyMuPDF @300 DPI) e lê com RapidOCR.

    300 DPI foi o lever decisivo na validação da Aurora (a 150 as palavras
    colavam). Requer `pymupdf` + `rapidocr-onnxruntime`.
    """
    import fitz  # PyMuPDF
    from rapidocr_onnxruntime import RapidOCR

    motor = RapidOCR()
    doc = fitz.open(str(caminho))
    total = doc.page_count
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    paginas = []
    for i in range(total):
        pix = doc.load_page(i).get_pixmap(matrix=mat)
        png = pix.tobytes("png")
        resultado, _ = motor(png)
        texto = "\n".join(linha[1] for linha in resultado) if resultado else ""
        paginas.append((i + 1, texto))
        if progress and (i == 0 or (i + 1) % 50 == 0 or i + 1 == total):
            progress(i + 1, total)
    doc.close()
    return paginas


def strip_boilerplate(pages):
    """Remove cabeçalhos/rodapés repetidos (título corrido, nº de página).

    Deteta-os por FREQUÊNCIA DE PÁGINAS DISTINTAS (linha normalizada, ≥5 chars,
    presente em ≥25% das páginas) — assim apanha o cabeçalho mesmo quando o OCR
    o enfia no meio do texto, sem tocar em conteúdo curto repetido ("a)", "(b)")
    nem em conteúdo de média frequência. Números de página soltos no topo/fundo
    são cortados à parte.
    """
    if len(pages) < 8:
        return pages  # poucas páginas (ou .txt) → não há repetição para inferir

    def norm(s):
        s = re.sub(r"\d+", "", s)
        return re.sub(r"\s+", " ", s).strip().upper()

    linhas, paginas_de = [], {}
    for idx, (_, texto) in enumerate(pages):
        ls = [l.strip() for l in texto.splitlines() if l.strip()]
        linhas.append(ls)
        for t in {norm(l) for l in ls if l}:
            if t:
                paginas_de.setdefault(t, set()).add(idx)

    limiar = max(5, int(0.25 * len(pages)))
    boiler = {t for t, ps in paginas_de.items() if len(t) >= 5 and len(ps) >= limiar}

    out = []
    for (num, _), ls in zip(pages, linhas):
        ls = [l for l in ls if norm(l) not in boiler]
        if ls and ls[0].isdigit():
            ls = ls[1:]
        if ls and ls[-1].isdigit():
            ls = ls[:-1]
        out.append((num, "\n".join(ls)))
    return out


def _is_header(linha):
    """Heurística conservadora de título de secção: linha curta, sem pontuação
    final, ou numerada (ex.: '15-4. Control de fase') ou quase toda em maiúsculas."""
    s = linha.strip()
    if not s or len(s.split()) > 8:
        return False
    if re.match(r"^\d+([.\-]\d+)+\.?\s+\w", s):
        return True
    letras = [c for c in s if c.isalpha()]
    if (len(letras) >= 3
            and sum(c.isupper() for c in letras) / len(letras) > 0.8
            and not s.endswith((".", "!", "?", ",", ";", ":"))):
        return True
    return False


def _iter_units(pages):
    """Frases (texto, página, secção). Junta linhas partidas pelo wrap do OCR,
    deteta títulos de secção (carregados para a frente) e corta em frases."""
    units, seccao, buf = [], None, []

    def flush(page):
        if not buf:
            return
        corrido = re.sub(r"\s+", " ", " ".join(buf)).strip()
        for frase in re.split(r"(?<=[.!?])\s+", corrido):
            frase = frase.strip()
            if frase:
                units.append((frase, page, seccao))
        buf.clear()

    for page, texto in pages:
        for linha in texto.splitlines():
            if _is_header(linha):
                flush(page)
                seccao = linha.strip()
            elif linha.strip():
                buf.append(linha.strip())
        flush(page)
    return units


def chunk_units(pages):
    """Empacota frases inteiras em chunks de ~CHUNK_WORDS (nunca parte uma frase).
    Devolve [{"text","page","section"}]. Sobreposição arrasta as últimas frases."""
    seq = _iter_units(pages)
    if not seq:
        return []

    chunks, atual, palavras = [], [], 0

    def fecha():
        texto = " ".join(s for s, _, _ in atual)
        chunks.append({"text": texto, "page": atual[0][1], "section": atual[0][2]})

    for frase, page, sec in seq:
        w = len(frase.split())
        if w >= CHUNK_WORDS:
            if atual:
                fecha()
                atual, palavras = [], 0
            chunks.append({"text": frase, "page": page, "section": sec})
            continue
        if palavras + w > CHUNK_WORDS and atual:
            fecha()
            sobrepor, sw = [], 0
            for item in reversed(atual):
                if sw >= OVERLAP_WORDS:
                    break
                sobrepor.insert(0, item)
                sw += len(item[0].split())
            atual, palavras = sobrepor, sw
        atual.append((frase, page, sec))
        palavras += w
    if atual:
        fecha()
    return chunks


def book_to_units(caminho, clean=True, ocr=False, progress=None):
    """Livro → (unidades, nº_páginas). Unidade = {"text","page","section"}."""
    pages = extract_pages(caminho, ocr=ocr, progress=progress)
    npags = len(pages)
    if clean:
        pages = strip_boilerplate(pages)
    return chunk_units(pages), npags
