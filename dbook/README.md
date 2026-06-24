# dbook — descodificador do formato "livro descodificado"

Ferramenta autónoma que transforma um livro num `.dbook` portátil. Implementa a
spec em [`../docs/dbook_format.md`](../docs/dbook_format.md).

A descodificação produz **sempre** a camada durável (texto limpo + estrutura,
agnóstica ao modelo) — o *commons* partilhável. Os vetores são uma camada
**opcional e por-modelo**, adicionada à parte. É essa separação que resolve o
"nó" da não-portabilidade dos embeddings entre modelos.

## O que produz

```
livro.dbook/
├── manifest.json     identidade + integridade (inclui structure_sha256, source_sha256)
├── structure.jsonl   DURÁVEL · 1 chunk por linha {id, page, section, text}
└── vectors/          PERECÍVEL · opcional · 1 .npz por modelo (com a guarda dentro)
    └── nomic-embed-text@unknown__768.npz
```

## Uso (a partir da raiz do projeto, com o venv)

```bash
# livro → .dbook (só a camada durável, partilhável e leve)
python -m dbook encode "Malvino.pdf" --ocr --title "Princípios de Eletrónica" --language es

# adicionar a camada de vetores de um modelo (custo caro, paga-se uma vez)
python -m dbook embed "Malvino.dbook" --model nomic-embed-text --model-version v1.5

# ou tudo de uma vez
python -m dbook encode "livro.txt" --embed

python -m dbook info   "livro.dbook"     # mostra o manifest
python -m dbook verify "livro.dbook"     # confere integridade (texto ↔ vetores)
```

`--ocr` liga o OCR (PyMuPDF @300 DPI + RapidOCR) para PDFs só-imagem.
`--no-clean` desliga a remoção de cabeçalhos/rodapés. `--zip` empacota no fim.

## A regra de uso (em código)

```python
from dbook import load_for_model

units, vectors, info = load_for_model("livro.dbook", "nomic-embed-text")
if vectors is not None:
    ...  # vetores reutilizados — custo de embedding ZERO
else:
    ...  # embebe [u["text"] for u in units] com o teu modelo (o caro já está feito)
```

A guarda (`model` / `dim` / `preprocess` / `structure_sha256`) impede, em silêncio
nunca, misturar espaços vetoriais incompatíveis ou vetores desalinhados do texto.

## Estado

- ✅ Camada durável: extração (.txt/.pdf), OCR opcional, limpeza de boilerplate,
  chunking por frases (nunca corta a meio), página e secção.
- ✅ Camada perecível: embeddings em lote (Ollama `/api/embed`), guarda completa.
- ✅ Integridade: `structure_sha256` + `source_sha256`; `verify`.
- ⏳ A fazer: deteção de secção mais robusta; mais embebedores (OpenAI/Google);
  metadados de licença/atribuição; ler de `.dbook.zip` sem descompactar.
