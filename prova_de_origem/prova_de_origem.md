# Prova de Origem — Livro Descodificado (`.dbook`)

**Autor:** Gustavo de Urzêda Abreu
**Data de publicação:** 24 de junho de 2026
**Contacto:** via GitHub — github.com/Gustavo-Ur

Este documento é a **prova de origem** (publicação defensiva) do formato
"Livro Descodificado" — `.dbook` — e dos seus artefactos fundadores. A sua
existência datada estabelece *prior art*: prova de que estes documentos e este
código existiam, nesta forma exata, nesta data — para que ninguém possa, mais
tarde, reclamar como invenção própria aquilo que aqui se publica.

---

## Hash raiz (selo atual)

```
427cd6769efa36f2dee153be92fac88242d45cec932b628cef42452985bfde7f
```

Esta é a impressão digital SHA-256 do ficheiro `SHA256SUMS`, que por sua vez
contém o SHA-256 de cada artefacto. Alterar um único byte de qualquer ficheiro
muda a sua linha em `SHA256SUMS`, e isso muda a hash raiz. Uma só linha sela tudo.

### Dois selos (ambos de 24 de junho de 2026)

- **Selo #1 — `77b96dd0…45738a4`** — a primeira versão dos documentos, antes das
  notas de licença CC BY 4.0. Preservado em [`selo_1_inicial/`](selo_1_inicial/)
  (com o seu próprio `SHA256SUMS.ots`); continua verificável.
- **Selo #2 — `427cd676…85bfde7f`** — a versão **canónica**, com as licenças
  CC BY 4.0 já incluídas nos documentos. É este o selo de referência (os ficheiros
  `SHA256SUMS` e `SHA256SUMS.ots` na raiz desta pasta).

O selo #1 prova que a obra já existia mais cedo nesse dia; o selo #2 sela a forma
final. Ambos têm o mesmo autor e a mesma data.

## Artefactos selados

| Ficheiro | Papel |
|---|---|
| `docs/manifesto.md` | A visão — a bandeira |
| `docs/dbook_format.md` | A especificação técnica do formato |
| `docs/constituicao.md` | A carta fundadora (livre / guardado / juramentos) |
| `dbook/__init__.py` … `__main__.py` | O descodificador de referência (6 ficheiros) |
| `dbook/LICENSE` | Apache License 2.0 (inclui a cláusula de patentes) |
| `dbook/NOTICE` | Aviso de atribuição |

Os hashes individuais estão em [`SHA256SUMS`](SHA256SUMS).

## Como verificar (qualquer pessoa, a qualquer momento)

A partir da raiz do projeto:

```sh
cd prova_de_origem
sha256sum -c SHA256SUMS     # confirma que cada ficheiro bate com a sua hash
sha256sum SHA256SUMS        # deve dar a hash raiz acima
```

Se todas as linhas disserem `OK` e a hash raiz coincidir, os artefactos são
exatamente os que foram selados nesta data.

## Carimbo temporal por terceiro — FEITO (OpenTimestamps)

A hash raiz foi ancorada via **OpenTimestamps** em **24 de junho de 2026**, sem
revelar qualquer conteúdo (só a hash viajou). A prova está em
[`SHA256SUMS.ots`](SHA256SUMS.ots).

Três servidores de calendário independentes comprometeram-se a gravar a hash na
blockchain do Bitcoin:

- `alice.btc.calendar.opentimestamps.org`
- `bob.btc.calendar.opentimestamps.org`
- `finney.calendar.eternitywall.com`

**Estado:** *pendente de confirmação no Bitcoin* — o compromisso já existe (a data
já está estabelecida); a inclusão no bloco completa-se sozinha em poucas horas.

### Como completar e verificar (mais tarde)

A forma mais simples, sem instalar nada e sem o bug do OpenSSL no Windows:

1. Abrir <https://opentimestamps.org>.
2. Arrastar para lá o `SHA256SUMS` (o original) **e** o `SHA256SUMS.ots`.
3. Ao fim de algumas horas, o site mostra a data e o bloco Bitcoin que a prova —
   isso "atualiza" o `.ots` para uma prova completa e definitiva.

> Nota técnica: o comando local `ots upgrade`/`ots verify` falha neste Windows
> porque a `python-bitcoinlib` choca com o OpenSSL 3.x (`BN_add not found`). O
> carimbo em si foi criado com a biblioteca-base `opentimestamps`, que não tem
> esse problema. Para verificação local em vez do site, usar essa via.

---

*Documento de prova de origem. © 2026 Gustavo de Urzêda Abreu. O código em
`dbook/` é licenciado sob Apache 2.0; os documentos em `docs/` são da autoria de
Gustavo de Urzêda Abreu e devem manter a atribuição.*
