# Livro Descodificado — `.dbook`

**Descodificar uma vez. Partilhar para sempre.**

Um formato universal e uma ferramenta de referência para guardar livros já
"descodificados" — texto limpo, estruturado e (opcionalmente) já transformado em
vetores — para que nenhuma AI tenha de re-descodificar do zero o mesmo livro.

Nascido de uma ideia de **Gustavo de Urzêda Abreu** (a partir do descodificador da
assistente Aurora), este projeto é **autónomo e neutro de propósito**: não pertence
a nenhuma app nem a nenhum fornecedor de modelos. É um bem comum com dono do
*formato* e da *ferramenta*, não dos livros dos outros.

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

## Licença e autoria

- **Código** (`dbook/`): Apache License 2.0 — ver `dbook/LICENSE`.
- **Documentos** (`docs/`): Creative Commons Atribuição 4.0 (CC BY 4.0).
- **Autoria e origem:** Gustavo de Urzêda Abreu, 2026. A `prova_de_origem/` data e
  ancora esta publicação (prior art). A atribuição é o único pedido.

> Os **juramentos** do Título III da constituição são pedra: neutralidade,
> atribuição, honestidade, comum legítimo (só conteúdo livre), e a guarda que falha
> alto. Quem pegar neste projeto herda-os com o nome.
