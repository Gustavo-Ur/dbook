# Especificação `.dbook` v1 (normativa)

> Estatuto: **v1 — estável.** Esta é a referência canónica do formato.
> O `dbook_format.md` (irmão) é o **explicador** (visão, motivação, a imagem dos
> dois armazéns); este ficheiro é o **contrato**: o que um `.dbook` válido contém
> e o que um leitor/escritor conforme deve fazer.
>
> © 2026 Gustavo de Urzêda Abreu. Documento sob CC BY 4.0; a implementação de
> referência (`dbook/`) sob Apache 2.0. Implementar o formato é livre e encorajado.

## 0. Termos normativos

As palavras **DEVE** / **NÃO DEVE** (MUST / MUST NOT), **DEVERIA** (SHOULD) e
**PODE** (MAY) seguem o sentido habitual (RFC 2119): obrigação, recomendação,
permissão. Tudo o que não for "DEVE" é, no mínimo, opcional.

## 1. Âmbito — a linha de neutralidade

Um `.dbook` descreve uma **obra**, nunca **quem a pode ler**. Esta fronteira é a
regra de desenho mais importante do formato: é o que o mantém neutro, e a
neutralidade é o que o torna adotável por qualquer aplicação.

**DENTRO do formato** (camada durável, neutra, partilhável):

- texto limpo, partido em pedaços (`chunks`) com **IDs estáveis**;
- paginação / secção, para **citação** exata;
- **hashes** de integridade (do texto e da fonte);
- a **etiqueta factual** de licença da obra (ver §8);
- **vetores opcionais**, um conjunto por modelo, com guarda de compatibilidade.

**FORA do formato** (camada do *produto* / da *instalação* — NUNCA dentro de um `.dbook`):

- motores de política e controlo de acesso (`ALLOW` / `DENY` / `REDACT` / `LIMIT`);
- identidade de utilizador, *tier*, jurisdição, propósito do pedido;
- conhecimento extraído por modelo — grafos de entidades, relações, resumos,
  perguntas-frequentes, palavras-chave (é perecível, opinativo e derivado: vive,
  se necessário, na mesma posição opcional dos vetores, **nunca** no `structure.jsonl`);
- *logs* de auditoria, orquestração de RAG, e o próprio LLM;
- "direito ao esquecimento" com propagação de remoção — **incompatível** com um
  artefacto durável e distribuível (uma cópia partilhada não se recupera).

**Regra de conformidade (§1):** um leitor ou escritor conforme **NÃO DEVE**
exigir nenhum dos elementos "FORA do formato" para ler ou escrever um `.dbook`
válido. Tudo o que dependa do *contexto de quem consulta* pertence à aplicação,
acima desta linha.

## 2. Estrutura de ficheiros

Um `.dbook` é uma **pasta** com esta árvore:

```
livro.dbook/
├── manifest.json        DEVE existir — identidade + integridade (§3)
├── structure.jsonl      DEVE existir — camada DURÁVEL, 1 chunk por linha (§4)
└── vectors/             PODE existir — camada PERECÍVEL, opcional (§5)
    ├── <modelo>.npz
    └── ...
```

A forma **`.zip`** (a mesma árvore comprimida) é permitida; os leitores
**DEVERIAM** aceitá-la. (A ferramenta de referência lê a forma em pasta hoje.)

A camada durável (§3, §4) usa apenas **JSON / JSONL + SHA-256** — deliberadamente
neutra à linguagem. Só a camada opcional de vetores (§5) usa um contentor
específico (`.npz`).

## 3. `manifest.json` — identidade e integridade

Objeto JSON (UTF-8). Campos:

| campo | tipo | obrig. | significado |
|---|---|---|---|
| `format` | string | **DEVE** | identifica a versão do formato. Em v1: `"dbook/1.0"`. |
| `title` | string | **DEVE** | título da obra. |
| `chunks` | inteiro | **DEVE** | número de linhas de `structure.jsonl`. |
| `structure_sha256` | string | **DEVE** | SHA-256 da camada durável (§6). |
| `vectors_available` | lista de string | **DEVE** | etiquetas `"modelo@versão/dim"`; pode estar vazia (`[]`). |
| `author` | string \| null | DEVERIA | autoria da obra. |
| `language` | string \| null | DEVERIA | código de língua (BCP-47 / ISO 639), ex.: `"pt"`. |
| `license` | string \| null | DEVERIA | **etiqueta factual** de licença da obra (ver §8). |
| `source` | string \| null | PODE | nome do ficheiro de origem (PDF/EPUB/TXT…). |
| `source_sha256` | string \| null | PODE | SHA-256 do ficheiro de origem. |
| `pages` | inteiro \| null | PODE | nº de páginas/secções de topo da obra. |
| `chunking` | objeto | PODE | como o texto foi partido (ex.: `{"method":"stanza","unit":"estrofe"}`). |
| `cleaned` | booleano | PODE | se o texto passou por limpeza. |
| `created` | string | PODE | data ISO-8601 (`AAAA-MM-DD`). |
| `tool` | string | PODE | ferramenta que escreveu o `.dbook`. |

Campos extra **PODEM** ser acrescentados; um leitor conforme **DEVE** ignorar os
que não conhecer (extensibilidade para a frente). Campos extra **NÃO DEVEM**
codificar regras de acesso (§1, §8).

**O `manifest.json` não é coberto pelo `structure_sha256`** e é mutável por
desenho: muda, por exemplo, quando se acrescenta uma camada de vetores (o campo
`vectors_available`). Um implementador **NÃO DEVE** tratá-lo como imutável nem
incluí-lo em hashes de integridade — o âncora imutável é a camada durável (§4).

## 4. `structure.jsonl` — a camada durável

Um objeto JSON por linha (JSONL). Cada objeto é um **chunk** com este esquema:

| campo | tipo | significado |
|---|---|---|
| `id` | inteiro | posição 0-based; **DEVE** ser contígua a começar em `0`. |
| `page` | inteiro | página/secção de topo para citação (`0` se não aplicável). |
| `section` | string \| null | rótulo legível da secção (ex.: `"Canto V, est. 50"`). |
| `text` | string | o texto do chunk (limpo). |

### 4.1 Forma canónica e `structure_sha256` (normativo)

Para que duas implementações independentes produzam o **mesmo** hash, a camada
durável tem uma serialização canónica. Para cada chunk, por ordem de `id`:

1. construir um objeto com as chaves **exatamente nesta ordem**:
   `id` (inteiro), `page` (inteiro), `section` (string ou `null`), `text` (string);
2. serializar em JSON **UTF-8**, **sem espaços insignificantes** (separador de
   itens `","`, separador de chave `":"`), e **sem escapar** caracteres não-ASCII
   (UTF-8 cru);
3. juntar as linhas com `"\n"` (LF) e acrescentar **um** `"\n"` final.

`structure_sha256` é o SHA-256 (hex minúsculo) desses bytes. O ficheiro
`structure.jsonl` em disco **DEVE** ser idêntico, byte a byte, a esta
serialização canónica — assim os próprios bytes do ficheiro fazem hash para
`structure_sha256`.

### 4.2 Âmbito do `structure_sha256` (honesto)

`structure_sha256` identifica uma **descodificação**, não a **obra**. Duas
descodificações do mesmo livro (chunking ou limpeza diferentes) são `.dbook`s
diferentes, com hashes diferentes. Logo o lema "nenhum livro descodificado duas
vezes" só se cumpre se as pessoas **partilharem a mesma descodificação** — o que
exige um decodificador canónico ou um registo, **fora do âmbito da v1**. A v1
garante apenas que, dada uma descodificação, os vetores se ligam a ela sem erro.

## 5. `vectors/<modelo>.npz` — a camada perecível (opcional)

Um *embedding* só vale no espaço vetorial do modelo exato que o produziu: os
vetores **não são portáteis** entre modelos e **envelhecem**. Por isso são
opcionais, um ficheiro por modelo, e trazem a guarda dentro.

Cada camada é um arquivo NumPy `.npz` (um *zip* de arrays `.npy`) com:

| array | conteúdo |
|---|---|
| `vectors` | matriz `float32` de forma `[n_chunks × dim]`; a linha `i` corresponde ao chunk `id = i`. |
| `model` | nome do modelo (string). |
| `model_version` | versão do modelo (string). |
| `dim` | dimensão dos vetores (inteiro). |
| `preprocess` | normalização aplicada ao texto antes de embeber (ex.: `"nfkd-deaccent"`, `"none"`). |
| `structure_sha256` | liga estes vetores a **este** texto (§6). |

**Nome do ficheiro:** `{model}@{model_version}__{dim}.npz`, com qualquer
caractere fora de `[\w.@+-]` substituído por `_`.

**`preprocess` é normativo para quem consulta:** ao embeber uma pergunta para
comparar com estes vetores, o cliente **DEVE** aplicar o mesmo `preprocess`. Se o
leitor **não souber reproduzir** o `preprocess` indicado, **NÃO DEVE** usar essa
camada — cai para embeber a `structure` com o seu próprio modelo (§7). Os valores
de `preprocess` são um vocabulário pequeno e controlado; a v1 define `"none"` e
`"nfkd-deaccent"` (decomposição NFKD com remoção de diacríticos).

**A fonte de verdade da guarda está *dentro* de cada `.npz`, não no manifest.** O
campo `vectors_available` (§3) é descritivo — conveniência para quem inspeciona.
Um leitor conforme determina a disponibilidade lendo `model` / `model_version` /
`dim` / `structure_sha256` de cada `.npz`, não a etiqueta. Uma etiqueta em falta
ou desatualizada **não** é fatal.

A camada de vetores usa `.npz` (um *zip* de arrays `.npy`), que é específico do
NumPy. Uma versão `v1.x` futura **PODE** definir um contentor de vetores neutro à
linguagem; a camada durável (§4), essa, já é neutra.

## 6. Integridade

- `structure_sha256` — SHA-256 da camada durável (§4.1). Liga os vetores ao texto.
- `source_sha256` — SHA-256 do ficheiro de origem, quando incluído.

Uma camada de vetores cujo `structure_sha256` **não** case com o do `manifest`
**NÃO DEVE** ser usada. A guarda **DEVE falhar alto** (recusar/avisar), nunca em
silêncio — é a mesma exigência da constituição (Título III).

Quando `model_version` é `"unknown"` (o modelo não reportou versão), a guarda
degrada-se para nome-do-modelo + `dim`: um modelo futuro com o mesmo nome e a
mesma `dim` poderia ser confundido com o atual. Um escritor **DEVERIA** registar
uma versão real sempre que a tiver.

### 6.1 `verify` — verificação mínima de conformidade

Um verificador conforme **DEVE** confirmar:

1. `sha256(structure.jsonl)` == `manifest.structure_sha256`;
2. nº de linhas não-vazias de `structure.jsonl` == `manifest.chunks`;
3. para cada `vectors/*.npz`: `structure_sha256` igual ao do manifest; `dim` igual
   a `vectors.shape[1]`; `vectors.shape[0]` igual ao nº de chunks.

`verify` confirma que o `.dbook` **não foi alterado** desde a escrita
(integridade), **não** que o escritor produziu a forma canónica (§4.1) — essa é
responsabilidade do escritor.

## 7. A regra de uso (resolve o nó dos modelos)

Quem consome um `.dbook`:

1. lê o `manifest`;
2. **há uma camada de vetores para o seu modelo** (e versão, se exigida) cujo
   `structure_sha256` casa com o texto atual? → usa-a. **Custo de embedding = zero.**
3. **não há?** → embebe a `structure.jsonl` com o seu próprio modelo. Barato: o
   trabalho caro (OCR, limpeza, partição, paginação) já vem feito e partilhado.

A guarda (`model` / `dim` / `structure_sha256`) impede misturar espaços vetoriais
incompatíveis ou usar vetores desalinhados do texto.

## 8. A etiqueta `license` é um FACTO, não uma política

`license` regista um **facto sobre a obra** — ex.: `"public_domain"`, `"CC-BY-4.0"`,
`"© 2026 Titular, todos os direitos reservados"`.

- **NÃO** é uma autorização: não concede nem nega acesso a ninguém.
- A decisão de servir, redigir ou recusar um chunk pertence à **camada do
  produto** (§1), que se funda — entre outras coisas — neste facto, mais o
  contexto (utilizador, propósito, jurisdição) que o `.dbook` **não** conhece.
- Um produtor **NÃO DEVE** codificar regras de acesso, *tiers* ou condições de
  uso dentro do `.dbook`. O formato diz **o que a obra é**, não **quem a pode ler**.

Corolário honesto: ter um chunk protegido num `.dbook` que se distribui não se
torna legítimo por se "redigir para uns e mostrar a outros". Ou se detém a licença
da obra (e se serve segundo os termos dela), ou não se deveria distribuir o chunk —
o controlo por *tier* é da aplicação e não cura a falta de direitos.

## 9. Conformidade

- **Escritor conforme:** produz a árvore §2 com `manifest.json` (§3) e
  `structure.jsonl` na forma canónica (§4.1); se incluir vetores, segue §5; não
  inclui nada da lista "FORA do formato" (§1).
- **Leitor conforme:** lê §3–§5, aplica a regra de uso (§7) e a guarda (§6),
  ignora campos desconhecidos, e não exige elementos fora de âmbito (§1).
- **Verificador conforme:** cumpre §6.1.

## 10. Versão do formato

O campo `format` carrega a versão (`"dbook/1.0"`). Mudanças compatíveis para a
frente (campos novos opcionais) **NÃO** sobem a versão *major*. Mudanças que
quebrem leitores antigos (alterar a forma canónica, remover um campo obrigatório)
**DEVEM** subir a versão *major* (`dbook/2.0`).

---

## Licença

Este documento © 2026 **Gustavo de Urzêda Abreu**, sob
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.pt). Implementar o
formato `.dbook` é livre; a atribuição da origem é o único pedido. O código de
referência (`dbook/`) é licenciado à parte, sob Apache 2.0.
