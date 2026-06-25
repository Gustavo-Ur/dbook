# Livro Descodificado — `.dbook`

**Descodificar uma vez. Partilhar para sempre.**

Um formato universal e uma ferramenta de referência para guardar livros já
"descodificados" — texto limpo, estruturado e (opcionalmente) já transformado em
vetores — para que nenhuma AI tenha de re-descodificar do zero o mesmo livro.

Nascido de uma ideia de **Gustavo de Urzêda Abreu** (a partir do descodificador da
assistente Aurora), este projeto é **autónomo e neutro de propósito**: não pertence
a nenhuma app nem a nenhum fornecedor de modelos. É um bem comum com dono do
*formato* e da *ferramenta*, não dos livros dos outros.

## ✨ Vê funcionar

Pergunta a *Os Lusíadas* (Camões, 1572) em **linguagem natural** — e recebe a
estrofe exata, com a citação. O livro já vem descodificado; isto só *recupera*.

```text
📖 Os Lusíadas — 1102 estrofes descodificadas, prontas.

❓ Quem comanda a viagem dos portugueses à Índia?
   → Canto II, est. 70
     «E como o Gama muito desejasse Piloto para a Índia que buscava…»

❓ Quem é o velho que critica a partida dos navegadores?
   → Canto IV, est. 94
     «Mas um velho d'aspeito venerando, Que ficava nas praias, entre a gente…»
```

Um poema de **450 anos**, a responder a perguntas de hoje, com a fonte exata.
Corre tu mesmo (precisa do [Ollama](https://ollama.com)):

```sh
python -m dbook embed biblioteca/os_lusiadas.dbook --model bge-m3   # descodificar uma vez
python examples/quickstart.py                                       # ...consultar para sempre
```

## Estrutura

```
dbook/
├── dbook/              A FERRAMENTA — descodificador de referência (pacote Python + CLI)
│                       extract · embedders · format · cli   + LICENSE (Apache 2.0) + NOTICE
├── docs/               A VISÃO E A LEI
│   ├── manifesto.md        a bandeira — porquê
│   ├── dbook_format.md     a especificação técnica do formato
│   └── constituicao.md     a carta fundadora (livre / guardado / juramentos)
├── biblioteca/         OS LIVROS — `.dbook` reais (Os Lusíadas, Frankenstein, Bíblias…)
│   ├── PROCEDENCIA.md      origem e licença de cada livro (domínio público)
│   └── METRICAS.md         o custo de descodificar — a "fatura paga uma vez"
└── prova_de_origem/    PUBLICAÇÃO DEFENSIVA — hashes + carimbo OpenTimestamps (Bitcoin)
```

## Início rápido

**A forma mais simples** — largas ficheiros numa pasta e descodificas tudo de uma vez:

```sh
python -m dbook sync     # cria entrada/, descodifica tudo para biblioteca/, salta o já feito
```

Pões os teus PDFs/textos em `entrada/`, corres `dbook sync`, e os `.dbook` aparecem
em `biblioteca/`. Volta a correr quando acrescentares ficheiros — só toca no que é
novo ou mudou (deteção por hash).

Ou ficheiro a ficheiro:

```sh
python -m dbook encode "livro.pdf" --embed --model nomic-embed-text   # livro → .dbook
python -m dbook info   "livro.dbook"                                   # ver o manifesto
python -m dbook verify "livro.dbook"                                   # conferir integridade
python -m dbook embed  "livro.dbook" --model bge-m3                    # juntar vetores de outro modelo
```

Um `.dbook` é uma pasta: `manifest.json` (identidade+integridade) + `structure.jsonl`
(camada **durável**: texto por chunk, agnóstica ao modelo) + `vectors/<modelo>.npz`
(camada **perecível**: opcional, uma por modelo, com a guarda). A **regra de uso**:
quem tem os vetores do seu modelo usa-os (custo zero); quem não tem, embebe a
estrutura barata — porque o trabalho caro (OCR, limpeza, partição) já vem feito.

## Integrações

Faz qualquer app de RAG ler o `.dbook` — sem mudar o teu fluxo.

**LangChain** (`pip install "dbook[langchain]"`):

```python
from dbook.integrations.langchain import DbookLoader

docs = DbookLoader("livro.dbook").load()   # → List[Document], pronto p/ o teu vectorstore

# Bónus — a regra de uso: reutilizar os vetores já prontos, 0 re-embed
res = DbookLoader("livro.dbook").precomputed_embeddings("nomic-embed-text")
if res:
    textos, vetores, metas = res           # mete-os num FAISS sem recalcular nada
```

**LlamaIndex** (`pip install "dbook[llama-index]"`):

```python
from dbook.integrations.llama_index import DbookReader

docs = DbookReader().load_data("livro.dbook")   # → List[Document], p/ o teu VectorStoreIndex
```

Cada documento traz o texto + metadados ricos (título, autor, página, secção,
hash), e ambos os loaders têm `precomputed_embeddings(model)` para a regra de
uso (reutilizar vetores prontos, 0 re-embed). Outras frameworks: o mesmo
padrão — contribuições bem-vindas (ver `CONTRIBUTING.md`).

## Licença e autoria

- **Código** (`dbook/`): Apache License 2.0 — ver `dbook/LICENSE`.
- **Documentos** (`docs/`): Creative Commons Atribuição 4.0 (CC BY 4.0).
- **Autoria e origem:** Gustavo de Urzêda Abreu, 2026. A `prova_de_origem/` data e
  ancora esta publicação (prior art). A atribuição é o único pedido.

> Os **juramentos** do Título III da constituição são pedra: neutralidade,
> atribuição, honestidade, comum legítimo (só conteúdo livre), e a guarda que falha
> alto. Quem pegar neste projeto herda-os com o nome.
