# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Gustavo de Urzêda Abreu

"""Leitura/escrita do formato `.dbook` + integridade, guarda e regra de uso.

Três camadas (ver docs/dbook_format.md):
  manifest.json     identidade + integridade
  structure.jsonl   DURÁVEL · 1 chunk por linha {id, page, section, text}
  vectors/*.npz     PERECÍVEL · opcional · 1 por modelo, com a guarda lá dentro
"""

import hashlib
import json
import re
from datetime import date
from pathlib import Path

import numpy as np

FORMAT_VERSION = "dbook/1.0"
MANIFEST = "manifest.json"
STRUCTURE = "structure.jsonl"
VECTORS_DIR = "vectors"


# ---------------------------------------------------------------- integridade
def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(caminho):
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


def _structure_bytes(units):
    """Bytes CANÓNICOS do structure.jsonl — base do structure_sha256. Ordem de
    campos fixa e separadores compactos para o hash ser estável e reproduzível."""
    linhas = []
    for i, u in enumerate(units):
        rec = {"id": i, "page": int(u.get("page", 0)),
               "section": u.get("section"), "text": u["text"]}
        linhas.append(json.dumps(rec, ensure_ascii=False, separators=(",", ":")))
    return ("\n".join(linhas) + "\n").encode("utf-8")


def _layer_filename(model, version, dim):
    nome = f"{model}@{version}__{dim}"
    return re.sub(r"[^\w.@+-]", "_", nome) + ".npz"


# ------------------------------------------------------------------- escrita
def write_dbook(out_dir, units, *, source=None, title=None, author=None,
                language=None, npages=None, chunking=None, cleaned=True,
                license=None, extra=None):
    """Escreve a camada durável (manifest + structure.jsonl). Devolve o caminho
    do .dbook e o structure_sha256 (que liga futuros vetores a ESTE texto)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    corpo = _structure_bytes(units)
    (out_dir / STRUCTURE).write_bytes(corpo)
    structure_sha256 = sha256_bytes(corpo)

    manifest = {
        "format": FORMAT_VERSION,
        "title": title or (Path(source).stem if source else out_dir.stem),
        "author": author,
        "language": language,
        "source": Path(source).name if source else None,
        "source_sha256": sha256_file(source) if source and Path(source).exists() else None,
        "pages": npages,
        "chunks": len(units),
        "structure_sha256": structure_sha256,
        "chunking": chunking or {},
        "cleaned": bool(cleaned),
        "vectors_available": [],
        "license": license,
        "created": date.today().isoformat(),
        "tool": "dbook/decoder",
    }
    if extra:
        manifest.update(extra)
    _write_manifest(out_dir, manifest)
    return out_dir, structure_sha256


def _write_manifest(out_dir, manifest):
    (Path(out_dir) / MANIFEST).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def add_vectors(dbook_dir, embedder, *, units=None, progress=None):
    """Embebe a camada durável com `embedder` e grava vectors/<modelo>.npz com a
    guarda (model/version/dim/preprocess + structure_sha256). Atualiza o manifest."""
    dbook_dir = Path(dbook_dir)
    manifest = read_manifest(dbook_dir)
    if units is None:
        units = read_structure(dbook_dir)
    textos = [u["text"] for u in units]

    vetores = embedder.embed(textos, progress=progress)
    matriz = np.asarray(vetores, dtype=np.float32)
    dim = matriz.shape[1] if matriz.ndim == 2 else 0

    (dbook_dir / VECTORS_DIR).mkdir(exist_ok=True)
    nome = _layer_filename(embedder.name, embedder.version, dim)
    np.savez(
        dbook_dir / VECTORS_DIR / nome,
        vectors=matriz,
        model=embedder.name,
        model_version=embedder.version,
        dim=dim,
        preprocess=getattr(embedder, "preprocess", "none"),
        structure_sha256=manifest["structure_sha256"],  # liga a ESTE texto
    )

    etiqueta = f"{embedder.name}@{embedder.version}/{dim}"
    if etiqueta not in manifest["vectors_available"]:
        manifest["vectors_available"].append(etiqueta)
    _write_manifest(dbook_dir, manifest)
    return nome, dim


# ------------------------------------------------------------------- leitura
def read_manifest(dbook_dir):
    return json.loads((Path(dbook_dir) / MANIFEST).read_text(encoding="utf-8"))


def read_structure(dbook_dir):
    """Lista de {id, page, section, text} a partir do structure.jsonl."""
    units = []
    with open(Path(dbook_dir) / STRUCTURE, encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha:
                units.append(json.loads(linha))
    return units


def load_for_model(dbook_dir, model, version=None):
    """A REGRA DE USO. Devolve (units, vectors|None, info).

    Se houver uma camada de vetores para `model` (e versão, se dada) que case com
    o texto atual → devolve-a (custo de embedding = ZERO). Senão, vectors=None: o
    chamador embebe a `structure` com o seu próprio modelo (barato — o caro já
    está feito). Nunca devolve vetores desalinhados (guarda structure_sha256).
    """
    dbook_dir = Path(dbook_dir)
    manifest = read_manifest(dbook_dir)
    units = read_structure(dbook_dir)
    vdir = dbook_dir / VECTORS_DIR

    if vdir.exists():
        for npz in sorted(vdir.glob("*.npz")):
            with np.load(npz, allow_pickle=True) as d:
                if str(d["model"]) != model:
                    continue
                if version and str(d["model_version"]) != version:
                    continue
                if str(d["structure_sha256"]) != manifest["structure_sha256"]:
                    continue  # vetores não correspondem a este texto → ignora
                info = {"layer": npz.name, "model": str(d["model"]),
                        "version": str(d["model_version"]), "dim": int(d["dim"]),
                        "preprocess": str(d["preprocess"])}
                return units, d["vectors"].astype(np.float32), info

    return units, None, {"layer": None, "reason": "sem vetores para este modelo"}


# ------------------------------------------------------------------- verificar
def verify(dbook_dir):
    """Confere integridade. Devolve (ok, [problemas])."""
    dbook_dir = Path(dbook_dir)
    problemas = []
    try:
        manifest = read_manifest(dbook_dir)
    except Exception as e:
        return False, [f"manifest ilegível: {e}"]

    corpo = (dbook_dir / STRUCTURE).read_bytes()
    sha = sha256_bytes(corpo)
    if sha != manifest.get("structure_sha256"):
        problemas.append("structure.jsonl não corresponde ao structure_sha256 do manifest")

    n = sum(1 for l in corpo.decode("utf-8").splitlines() if l.strip())
    if n != manifest.get("chunks"):
        problemas.append(f"nº de chunks: structure={n} vs manifest={manifest.get('chunks')}")

    vdir = dbook_dir / VECTORS_DIR
    if vdir.exists():
        for npz in sorted(vdir.glob("*.npz")):
            with np.load(npz, allow_pickle=True) as d:
                if str(d["structure_sha256"]) != sha:
                    problemas.append(f"{npz.name}: vetores não casam com o texto atual")
                if int(d["dim"]) != d["vectors"].shape[1]:
                    problemas.append(f"{npz.name}: dim do manifest ≠ dim real")
                if d["vectors"].shape[0] != n:
                    problemas.append(f"{npz.name}: {d['vectors'].shape[0]} vetores ≠ {n} chunks")
    return (not problemas), problemas
