# Biblioteca livre `.dbook` — Procedência

Esta pasta é a semente local da **biblioteca mundial** do projeto Livro
Descodificado: livros de **domínio público** descodificados em `.dbook`, livres de
partilhar. Cada entrada regista aqui a sua origem, em cumprimento dos juramentos da
constituição (*atribuição* e *comum legítimo* — só conteúdo livre).

---

## 1. Os Lusíadas — Luís de Camões (1572)

- **Ficheiro:** `os_lusiadas.dbook/` (camada durável: 340 chunks)
- **Estatuto:** domínio público. A obra de Luís Vaz de Camões (m. 1580) está em
  domínio público em todo o mundo há séculos.
- **Fonte do texto:** Project Gutenberg, eBook **#3333**
  (<https://www.gutenberg.org/ebooks/3333>), língua portuguesa.
- **Transcrição creditada a:** Maria Helena Moreira Rodrigues e Victor Calha
  (produtores da edição Project Gutenberg).
- **Preparação:** removida a moldura legal do Project Gutenberg (cabeçalho/rodapé
  entre os marcadores `*** START/END OF THE PROJECT GUTENBERG EBOOK ***`); guardado
  apenas o texto da obra. A marca "Project Gutenberg" **não** é usada nem
  redistribuída — apenas o texto de domínio público subjacente.
- **Descodificado em:** 24 de junho de 2026, com o descodificador de referência
  `dbook/` (formato `dbook/1.0`).
- **Nota:** sendo a fonte um `.txt` sem páginas, o `.dbook` tem 1 "página". Um
  refinamento futuro é paginar por Canto/estrofe e preencher o campo `section`.

---

## 2. Frankenstein; or, The Modern Prometheus — Mary Shelley (1818)

- **Ficheiro:** `frankenstein.dbook/` (28 secções Carta/Capítulo, 428 chunks;
  camada de vetores: `bge-m3` multilingue)
- **Estatuto:** domínio público. Mary Wollstonecraft Shelley (m. 1851); obra de
  1818 (rev. 1831).
- **Fonte do texto:** Project Gutenberg, eBook **#84**
  (<https://www.gutenberg.org/ebooks/84>), língua inglesa.
- **Preparação:** removida a moldura legal do Project Gutenberg e o Índice (que
  duplicava os cabeçalhos); seccionado por `Carta N` / `Capítulo N`, com cada
  estrofe/parágrafo empacotado em chunks de ~250 palavras por frases.
- **Descodificado em:** 24 de junho de 2026 (formato `dbook/1.0`).
- **Porquê esta:** a **segunda pedra**, e a primeira em inglês. Prova a busca
  **translingue**: perguntas em português recuperam passagens inglesas com citação
  por capítulo (ex.: "Victor dá vida à criatura" → Capítulo 5), via `bge-m3`.

---

## 3. A Bíblia — em três línguas (1818… texto antigo, domínio público)

A mesma obra em três línguas, para provar a biblioteca multilingue. Fonte comum:
**`scrollmapper/bible_databases`** (GitHub), coleção de domínio público em JSON
estruturado (`books[].chapters[].verses[]`). Um só analisador para as três.

- **`biblia_pt_livre.dbook`** — **Bíblia Livre** (Português), 66 livros, 4156
  passagens. *Nota:* não é a Almeida moderna (ACF, protegida) — é a Bíblia Livre,
  de domínio público, da tradição Almeida.
- **`biblia_en_kjv.dbook`** — **King James Version (1769)** (Inglês), 66 livros,
  4567 passagens. Domínio público.
- **`biblia_la_vulgata.dbook`** — **Vulgata Clementina** (Latim), 78 livros (inclui
  deuterocanónicos), 4012 passagens. Domínio público.

- **Estrutura:** versículos empacotados em passagens de ~180 palavras, citadas pelo
  versículo inicial (`Livro Cap:Versículo`), `page` = nº do livro. Nomes dos livros
  em inglês (da fonte) — mapear para PT é um retoque futuro.
- **Limitação honesta:** sendo passagens (não versículos), a citação é à passagem;
  o mesmo versículo pode cair em passagens de número diferente entre versões. Uma
  camada ao versículo (citação exata, alinhada) é o próximo refinamento.
- **Descodificadas em:** 24 de junho de 2026 (formato `dbook/1.0`).

---

## Modelos de embeddings usados

- **`nomic-embed-text`** (768-dim) — rápido, mas anglófono; tropeça em PT arcaico.
- **`bge-m3`** (1024-dim) — multilingue, **recomendado** para a biblioteca;
  superior em PT e capaz de busca translingue. Os `.dbook` podem ter vários `.npz`
  lado a lado (um por modelo) sobre o mesmo texto, sem re-descodificar.

> Nota de investigação (24 Jun): testou-se o pré-processamento `nfkd-deaccent`
> (feito para OCR) com vs sem, no bge-m3 — diferença **negligenciável**. O que mais
> afeta a recuperação translingue é o **fraseado da pergunta**, não os acentos.

---

*Cinco pedras assentes (Os Lusíadas, Frankenstein, e a Bíblia em PT/EN/Latim).
"Por mares nunca de antes navegados."*
