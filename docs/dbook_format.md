# `.dbook` — o livro descodificado portátil

> Nasceu de uma ideia do Gustavo na conversa "PA_1" (23 Jun 2026), a partir do
> descodificador da Aurora (`services/decoder_service.py`).
>
> **Implementação de referência: `dbook/`** (CLI `python -m dbook`). Já produz e
> lê `.dbook` reais — ver `dbook/README.md`. Detalhes que diferem deste esboço:
> o chunking é por **frases** (`method: "sentences"`, não "words"), e a camada de
> vetores guarda também `preprocess` (ex.: `nfkd-deaccent`) para quem a usar
> embeber as perguntas da mesma forma.
>
> **A especificação NORMATIVA é [`spec_dbook_v1.md`](spec_dbook_v1.md)** — o
> contrato a que um leitor/escritor conforme obedece (campos, forma canónica do
> hash, a regra de uso, a linha de neutralidade). Este documento é o *explicador*:
> a visão e a intuição. Em caso de divergência, vale a spec.

## A visão

No futuro, um livro publicado vem já **descodificado**: com o seu conhecimento
pronto a ser consultado por uma AI, em vez de ser enfiado inteiro no *prompt*.

Hoje, se quatro pessoas põem o mesmo livro no prompt para uma AI o analisar,
estão as quatro a gastar tokens, computação, tempo e energia a repetir o **mesmo**
trabalho. Embeber **uma vez** e partilhar amortiza esse custo — à escala de uma
biblioteca mundial, a poupança é enorme.

Levado ao limite: um repositório partilhado de livros descodificados — *"tudo o
que há no mundo, já descodificado; é só aceder."*

## O que resolve

Imagina uma editora que, ao lançar um livro novo, lança também a sua parte
descodificada (oficial). Isto resolve quatro problemas ao mesmo tempo — raro
numa só ideia:

**1. Desperdício (computação · energia · tokens).** Hoje cada pessoa/app que
quer AI sobre um livro re-processa-o do zero (extrair, OCR, partir, embeber).
Milhões de utilizadores × o mesmo livro = desperdício colossal. Descodificar
**uma vez** na origem elimina-o. E ninguém enfia o livro inteiro no prompt —
recupera-se só o relevante (mais barato, mais rápido, cabe na janela).

**2. Alucinação (fidelidade na fonte).** A AI lê o texto **canónico e correto**
da editora — não um OCR mau nem uma cópia trôpega/pirata. As citações tornam-se
exatas (página certa). Erratas corrigidas → a editora relança; a AI nunca fica
com a versão errada.

**3. A guerra dos direitos de autor.** Hoje os modelos treinam em cópias piratas
e as editoras processam-nos. Um livro descodificado **oficial** é um canal
**licenciado, pago e controlado** para a AI aceder ao conteúdo. A editora deixa
de só *perder* para a AI e passa a **vender à AI** — produto novo, receita nova,
com metadados de licença, controlo de uso e atribuição garantida. Isto eleva a
ideia de truque técnico a **modelo de negócio** (e provável motor de adoção).

**4. Acesso (offline · privado · equitativo).** Uma biblioteca de AI que funciona
**sem internet e sem mandar perguntas para a nuvem** (escolas, sítios remotos,
contextos sensíveis). Livros "cegos" (scans, livros antigos) deixam de o ser — o
OCR é feito bem, uma vez, na origem. E um professor ou uma ferramenta pequena
**não precisa de computação enorme**: o trabalho pesado vem feito e partilhado.
Democratiza o acesso ao conhecimento por AI.

## O nó que o formato resolve

Um *embedding* só faz sentido no espaço vetorial do modelo **exato** que o
produziu. (É por isso que o descodificador da Aurora tem uma guarda de
modelo/dimensão.) Logo:

- os vetores **não são portáteis** entre modelos (nomic ≠ OpenAI ≠ Google);
- os vetores **envelhecem** — um modelo novo embebe melhor.

O **texto é durável; os vetores são perecíveis.** O formato separa as duas coisas.

### A imagem dos dois armazéns

Um *embedding* é uma lista de números — as **coordenadas** do significado de um
pedaço de texto. Mas essas coordenadas só valem no "mapa" que **aquele modelo**
desenhou.

Imagina cada modelo de AI como um bibliotecário que arruma todas as ideias do
mundo num armazém gigante, cada ideia numa prateleira `(corredor, coluna, altura)`:

- O **Modelo A** põe "Teorema de Norton" em `[3.2, −1.7, 0.9]`.
- O **Modelo B** constrói o **seu próprio** armazém, com outra arrumação. Para
  ele, a mesma ideia está em `[−0.4, 2.1, 5.5]`.

O **texto** é o mesmo; as **coordenadas** são diferentes. Entregar as coordenadas
do A ao B faz o B apontar para uma prateleira ao calhas — lixo. Por isso os
vetores não se traduzem entre modelos: **um vetor são coordenadas no armazém
privado de um modelo.**

A resposta do formato: enviar também o **texto já arrumado** (`structure.jsonl`),
que é independente do armazém. Quem tiver as coordenadas do seu modelo usa-as
(custo zero); quem não tiver, deixa o seu próprio bibliotecário arrumar o texto —
barato, porque o trabalho pesado (OCR, limpeza, partição) já vem feito.

**Quão sério é este nó?** Depende do contexto:
- Num **ecossistema fechado** (quem controla o modelo, como a Aurora hoje) — não
  é problema nenhum; a guarda só evita misturar dois armazéns por acidente.
- Na **visão universal** — é o obstáculo central, a razão por que não se pode
  "mandar um conjunto de vetores que serve toda a gente". Não é um bug: é quase
  uma lei (modelos diferentes aprendem mesmo representações diferentes, e não há
  tradução sem perda). Desenha-se à volta — que é o que este formato faz.

## A estrutura

```
livro.dbook/                         (uma pasta ou um zip)
├── manifest.json        →  identidade do livro + integridade
├── structure.jsonl      →  DURÁVEL · agnóstico ao modelo (1 pedaço por linha)
└── vectors/             →  PERECÍVEL · opcional · um ficheiro por modelo
    ├── nomic-embed-text@v1.5.npz
    └── openai-text-embedding-3@small.npz
```

### 1. `manifest.json` — o bilhete de identidade

```json
{
  "format": "dbook/1.0",
  "title": "Princípios de Eletrónica",
  "author": "Albert Malvino",
  "language": "es",
  "source": "malvino.pdf",
  "source_sha256": "<hash do PDF/EPUB original>",
  "pages": 1124,
  "chunks": 2100,
  "structure_sha256": "<hash da camada durável — liga os vetores a este texto>",
  "chunking": { "method": "sentences", "size": 250, "overlap": 40 },
  "cleaned": true,
  "vectors_available": [
    "nomic-embed-text@v1.5/768",
    "text-embedding-3@small/1536"
  ],
  "license": null,
  "created": "2026-06-23",
  "tool": "dbook/decoder"
}
```

> Campos como `isbn` não fazem parte da v1 (podem entrar como campos extra, que um
> leitor conforme ignora). O conjunto canónico de campos é o da
> [spec](spec_dbook_v1.md) §3.

### 2. `structure.jsonl` — a camada durável

O livro já partido, limpo e paginado. **Nunca envelhece.** Qualquer AI, de
qualquer modelo, embebe-o de forma barata — sem voltar a processar o PDF nem a
correr OCR.

```jsonl
{"id":0,"page":19,"section":"Teorema de Norton","text":"La resistencia de Norton..."}
{"id":1,"page":19,"section":"Teorema de Norton","text":"..."}
```

### 3. `vectors/<modelo>.npz` — a camada perecível

Os vetores, com a guarda de compatibilidade lá dentro:

| campo | papel |
|---|---|
| `vectors` | matriz `[n_chunks × dim]`, alinhada por `id` |
| `model`, `model_version`, `dim` | guarda: impede misturar espaços vetoriais diferentes |
| `structure_sha256` | garante que estes vetores correspondem a *este* texto |

## A regra de uso (resolve o nó dos modelos)

1. A AI lê o `manifest`.
2. **Há vetores para o seu modelo?** → usa-os direto. **Custo de embedding = zero.**
3. **Não há?** → embebe a `structure.jsonl` com o seu próprio modelo. Barato,
   porque o trabalho pesado (partir, limpar, OCR, paginar) **já está feito e é
   partilhado**.
4. A guarda `model/dim` + `structure_sha256` impede, **em silêncio nunca**,
   misturar espaços incompatíveis ou texto desalinhado.

## Porque é que isto realiza a visão

- **De-duplica o caro à escala mundial:** mesmo quem tem de re-embeber nunca
  repete o OCR, a limpeza nem a paginação.
- **Sobrevive à evolução dos modelos:** sai um embedder melhor? Adiciona-se só
  mais um ficheiro em `vectors/`. O livro não se re-descodifica todo.
- **É a base mundial, possível:** um repositório de `*.dbook` é exatamente
  "tudo já descodificado, é só aceder" — e cada AI escolhe a camada de vetores
  que fala a sua língua.

## Relação com a Aurora

O `.npz` por livro que a Aurora já gera (`data/processed/<livro>__<id>.npz`,
com `vectors` + `chunks` + `pages` + `embed_model` + `dim` + `confidential`) é,
na prática, **um `.dbook` com as três camadas fundidas num só ficheiro**. O
formato universal não é uma reinvenção — é o que já existe, *desmontado* em
peças partilháveis.

Caminho de evolução possível, sem partir nada:

1. `decode_book` passa a escrever também `structure.jsonl` (a partir dos `chunks`
   + `pages` que já tem).
2. A matriz de vetores migra para `vectors/<modelo>.npz` com `structure_sha256`.
3. Adiciona-se o `manifest.json`.

O resultado continua a funcionar como a réplica atual, mas torna-se partilhável.

---

## Licença

Este documento (`dbook_format.md`) © 2026 **Gustavo de Urzêda Abreu** está licenciado
sob [Creative Commons Atribuição 4.0 Internacional (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.pt).

És livre de **partilhar** e **adaptar** esta especificação, para qualquer fim, mesmo
comercial — desde que dês o devido **crédito** a Gustavo de Urzêda Abreu, indiques se
foram feitas alterações e ligues à licença. Implementar o formato `.dbook` é livre e
encorajado; a atribuição da origem é o único pedido. A camada técnica (o código em
`dbook/`) é licenciada à parte, sob Apache 2.0.
