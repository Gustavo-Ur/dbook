# Livro Descodificado — Manifesto

> *"Cada salto da civilização foi alguém a dizer: isto já foi feito — vamos
> guardá-lo e partilhá-lo, não repeti-lo."*

Nascido de uma ideia do Gustavo (conversa "PA_1", 23 de junho de 2026), a partir
do descodificador da assistente Aurora. Este documento é a bandeira: a visão em
palavras que qualquer pessoa possa pegar.

---

## 1. O problema — repetir o que já foi feito

Quando uma AI precisa de "ler" um livro hoje, alguém tem de o **descodificar**:
extrair o texto, corrigir o OCR de um scan, limpar, partir em pedaços, transformar
cada pedaço em números (embeddings). É trabalho caro — minutos a horas por livro,
energia, computação.

E aqui está o desperdício: **toda a gente repete esse trabalho.** Quatro pessoas,
quatro empresas, quatro modelos diferentes a descodificar o **mesmo** livro, cada
um por sua conta. Multiplica por milhões de utilizadores e milhões de livros: o
mundo a queimar energia a redescobrir, vezes sem conta, a mesma roda.

O desperdício não é a computação. **É a repetição da computação.**

## 2. O princípio — descodificar uma vez, partilhar para sempre

É o gesto mais humano que há, e o que sempre nos fez avançar:

- inventámos a **escrita** para não termos de re-memorizar tudo;
- a **imprensa** para não re-copiar à mão;
- as **bibliotecas** para não re-descobrir o que já se sabia.

Cada salto foi guardar o trabalho feito e partilhá-lo, em vez de o repetir. O
**Livro Descodificado** é esse mesmo gesto, dado um passo mais à frente — mas com
uma assinatura nova na história: os anteriores guardaram conhecimento **para
humanos lerem**; este guarda conhecimento **para máquinas pensarem com ele.**

Descodificar uma vez, na origem, bem feito. Partilhar. Nunca mais repetir.

## 3. O nó que torna isto difícil (e a chave que o abre)

Não basta partilhar os números. Um embedding são **coordenadas no mapa privado de
um modelo** — o "Teorema de Norton" que o Modelo A guarda em `[3.2, −1.7, 0.9]`
está, para o Modelo B, num sítio completamente diferente. Entregar as coordenadas
de um ao outro é apontar para uma prateleira ao calhas. Lixo.

Logo: **os vetores não são portáteis entre modelos, e envelhecem.** Mas o **texto
é durável.** Esta é a descoberta que tudo sustenta — não a inventámos, encontrámo-la.

A chave é separar as duas coisas:

- a camada **durável** — o texto limpo, estruturado, paginado — serve toda a gente,
  para sempre, independente de qualquer modelo;
- a camada **perecível** — os vetores — é opcional e existe **uma por modelo**.

Quem tem os vetores do seu modelo usa-os (custo zero). Quem não tem, embebe o texto
limpo — barato, porque o trabalho pesado (OCR, limpeza, partição) **já vem feito**.

## 4. O formato — `.dbook`

Um livro descodificado é uma pasta (ou um zip):

```
livro.dbook/
├── manifest.json     identidade + integridade (hashes, licença)
├── structure.jsonl   DURÁVEL · o texto limpo, 1 pedaço por linha {id, página, secção, texto}
└── vectors/          PERECÍVEL · opcional · 1 ficheiro por modelo, com a guarda dentro
```

A **guarda** (modelo, dimensão, pré-processamento, hash do texto) impede — e nunca
em silêncio — que se misturem espaços incompatíveis ou se usem vetores desalinhados
do texto.
Detalhe técnico completo em [`dbook_format.md`](dbook_format.md).

## 5. Porque é o próximo degrau da AI

Hoje, uma AI "sabe" de um livro de duas formas: **treinada nele** (conhecimento
congelado, opaco, não-citável, legalmente problemático) ou com o **texto enfiado no
prompt** (caro, repetido a cada uso). O `.dbook` é uma terceira via — conhecimento
**pré-descodificado, pronto a consultar** — e muda o que a AI pode fazer:

- **Combate a alucinação na raiz:** a AI consulta o texto canónico, com página
  exata, em vez de "se lembrar mal".
- **Modelos pequenos jogam acima do seu peso:** o "saber" vive fora do modelo, num
  substrato partilhado. Um modelo local modesto + boa biblioteca rivaliza com um
  gigante em tarefas factuais.
- **Conhecimento sempre atual sem re-treino:** corrige-se o `.dbook`, não o modelo.
- **Offline, privado, equitativo:** funciona sem nuvem; uma escola ou ferramenta
  pequena recebe o trabalho pesado já feito.
- **Um canal licenciado para o copyright:** a editora deixa de só *perder* para a
  AI e passa a **vender-lhe** uma edição-AI, com atribuição e licença.

No fundo, empurra a AI numa direção: **separar saber de raciocinar.** Em vez de
memorizar tudo nos pesos, o modelo apoia-se num conhecimento consultável — mais
pequeno, mais barato, mais auditável. Saber deixa de ser memória congelada e
torna-se um bem comum.

## 6. O que isto NÃO é (a honestidade faz parte do projeto)

- **Não é magia que torna a AI mais inteligente.** É recuperação: traz o trecho
  certo, fiel. Quem raciocina continua a ser o modelo.
- **Não resolve o copyright sozinho.** Cria um canal limpo, mas os direitos têm de
  ser dados — um repositório mundial só é legítimo sobre conteúdo livre, de domínio
  público, próprio ou licenciado.
- **Os vetores não são o tesouro.** Fragmentam-se por modelo e envelhecem. O bem
  comum real é o **texto descodificado**.
- **O difícil não é a tecnologia — é a adoção.** É preciso um standard que muita
  gente aceite. Como o ePub, o RSS, os sitemaps: o valor vem da convenção partilhada.

## 7. Onde estamos

Isto não é só um sonho escrito. Existe um **descodificador de referência** que já
produz e lê `.dbook` reais — extração e OCR, limpeza de boilerplate, chunking por
frases, embeddings em lote, integridade por hash, e a regra de uso que reaproveita
vetores ou cai para "embebe-te a ti mesmo". Provado ponta-a-ponta num livro real.
Ver [`../dbook/README.md`](../dbook/README.md).

A semente funciona.

## 8. O convite

As grandes mudanças não começam grandes. Começam com alguém a olhar para uma tarefa
miúda — um livro, uma máquina pequena — e a perguntar:

**"Porque é que estamos todos a fazer isto outra vez?"**

Se daqui a uns anos um modelo de AI voltar a descodificar, do zero, um livro que já
foi descodificado uma vez, então ainda não chegámos lá. O objetivo é simples e
imenso: que **nenhum livro precise de ser descodificado duas vezes.**

Descodificar uma vez. Partilhar para sempre.

---

## Licença

Este documento (`manifesto.md`) © 2026 **Gustavo de Urzêda Abreu** está licenciado
sob [Creative Commons Atribuição 4.0 Internacional (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.pt).

És livre de **partilhar** e **adaptar** este material, para qualquer fim, mesmo
comercial — desde que dês o devido **crédito** a Gustavo de Urzêda Abreu, indiques
se foram feitas alterações e ligues à licença. A camada técnica do projeto (o
código em `dbook/`) é licenciada à parte, sob Apache 2.0.
