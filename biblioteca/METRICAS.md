# Métricas de Descodificação — a fatura paga uma só vez

> O custo de descodificar cada livro para `.dbook`. **Cada reutilização futura
> destes vetores custa zero segundos e zero energia.** Esta folha é a prova viva da
> tese do projeto: o desperdício não é a computação — é a *repetição* da computação.

**Contexto:** descodificado em 24 de junho de 2026, numa GPU **RTX 3050 (4 GB VRAM)**,
via Ollama. Embebedores: **nomic-embed-text** (768-dim) e **bge-m3** (1024-dim,
multilingue). Medições: tempos por `time` e por mtimes dos ficheiros; palavras por
separação em espaços; energia **estimada** (ver fim).

---

## Por livro

| Livro | Fonte (bytes) | Palavras | Versíc./Estrofes | Chunks | Durável (bytes) | Vetores (modelo · bytes) | Tempo embed | Ritmo |
|---|--:|--:|--:|--:|--:|---|--:|--:|
| **Os Lusíadas** (PT) | 325 133 | 56 372 | 1 102 estr. | 1 102 | 386 537 | nomic · 3 387 274 | **122,7 s** | 9,0 c/s |
| | | | | | | bge-m3 · 4 515 682 | **203,4 s** | 5,4 c/s |
| **Frankenstein** (EN) | 421 541 | 75 042 | — | 428 | 570 649 | bge-m3 · 1 754 978 | **124,1 s** | 3,4 c/s |
| **Bíblia Livre** (PT) | 8 159 153 | 696 423 | 31 104 v. | 4 156 | 4 111 231 | bge-m3 · 17 024 866 | **~1 074 s** | 3,9 c/s |
| **King James** (EN) | 8 395 929 | 789 814 | 31 102 v. | 4 567 | 4 401 691 | bge-m3 · 18 708 322 | **1 061 s** | 4,3 c/s |
| **Vulgata** (LA) | 9 226 278 | 642 303 | 37 255 v. | 4 012 | 4 314 966 | bge-m3 · 16 435 042 | **979 s** | 4,1 c/s |

*(Tempo de Os Lusíadas com nomic inclui também uma 1.ª embebição de 340 chunks =
62,5 s, antes de re-seccionar por Canto/estrofe — gasta, mas substituída.)*

## Totais (artefactos finais)

- **Palavras descodificadas:** 2 259 954 (~2,26 milhões)
- **Versículos + estrofes:** 100 563 (99 461 versículos bíblicos + 1 102 estrofes)
- **Chunks (camada durável):** 14 265
- **Tempo de embebição (bge-m3 + nomic):** **~59 min** de GPU (≈ 3 564 s, medido)
- **Armazenamento de vetores:** ~61,8 MB (todos os `.npz` somados)
- **Camada durável (texto estruturado):** ~13,8 MB (a parte partilhável com *todos* os modelos)

## A poupança (o que isto compra para sempre)

- **Reutilizar** qualquer destes vetores (modelo que fale a língua do bge-m3 ou do
  nomic): **0 s, 0 J.** É a regra de uso do `.dbook` — vetores grátis se existirem.
- **Um modelo futuro** com outro espaço vetorial **não re-descodifica** o livro: lê
  a camada durável (já pronta) e embebe só ela. O trabalho caro (extrair, limpar,
  seccionar, OCR) fez-se uma vez, para todos os modelos presentes e futuros.

## Duas naturezas de custo

1. **Custo durável (descodificação real):** download + limpeza + partição. Para
   estas fontes digitais limpas foi **rápido (segundos)**. Mas para um **scan** é o
   passo verdadeiramente caro: o OCR. *Referência: o Malvino (1124 págs) custou
   horas de OCR.* É esse custo — horas, irreproduzível — que o comum mais poupa.
2. **Custo perecível (vetores):** a embebição acima (~58 min), por-modelo.

## Energia (estimativa grosseira — não medida)

Não tenho um wattímetro no processo. Assumindo a RTX 3050 (4 GB) a consumir
~45–75 W sob carga de inferência, durante ~0,98 h de embebição:

- **≈ 0,05–0,07 kWh** no total das cinco obras (três Bíblias + dois livros).

Para dar escala: equivale, grosso modo, a **4–6 cargas de telemóvel**, ou a uma
lâmpada LED de 10 W acesa ~5–7 horas. Trivial — e, mais importante, **pago uma só
vez.** Multiplica isto por milhões de utilizadores a re-fazerem o mesmo livro e vê-se
o desperdício que o `.dbook` elimina.

---

## Como foi medido (honestidade)

- **Tempos:** os de Os Lusíadas e Frankenstein por `time` (precisos); os das Bíblias
  por diferença de mtimes dos `.npz` (a Bíblia PT tem uma pequena margem por o
  arranque do processo em segundo plano não estar cronometrado ao segundo).
- **Palavras:** contagem por espaços (crua; o latim, sem artigos e com enclíticos,
  conta um pouco abaixo do "real").
- **Energia:** estimada por potência típica × tempo, **não** medida diretamente.
- **Latim:** linha a terminar no momento da escrita; a finalizar.

---

# Projeção à escala (ESTIMATIVA — não medida)

> Tudo abaixo é **estimativa**, separada dos números medidos acima. A matemática é
> simples: como só **uma** descodificação é precisa, recomputá-la N vezes
> desperdiça (N−1) cópias. O `.dbook` baixa o nº de descodificações de "uma por
> pessoa" para "uma, e nunca mais".

## Custo por pessoa (as 5 obras) — porque o desperdício é invisível

- Energia: ~0,06 kWh → **~€0,013 / ~$0,010** (cerca de **1 cêntimo**).
- É trivial por pessoa. Esconde-se um cêntimo de cada vez — só pesa multiplicado.

## Recomputar as 5 obras × N pessoas

| Pessoas | GPU desperdiçada | Energia | Eletricidade (€ / $) | Em nuvem (€ / $) |
|---|--:|--:|--:|--:|
| 1 000 | 41 dias | 60 kWh | €13 / $10 | €360 / $390 |
| **1 milhão** | **111 anos-GPU** | **60 MWh** | **€13 200 / $10 200** | **€362k / $391k** |
| 10 milhões | 1 115 anos-GPU | 600 MWh | €132k / $102k | €3,6M / $3,9M |

*(Eletricidade = só a conta da luz se a máquina for tua. "Em nuvem" = alugar GPU ou
usar uma API de embeddings — o que a maioria faz.)*

## Os multiplicadores que tornam isto sério (em dinheiro)

- **OCR de um único livro digitalizado × 1 milhão** (~2h cada): ~228 anos-GPU →
  **~€20k–800k** (luz vs nuvem). Num só livro.
- **Enfiar o livro no prompt** (1 livro, 1M pessoas, 10 perguntas cada ≈ 10¹²
  tokens): **~$300k a $3M** — e **a cada pergunta, para sempre.** Com `.dbook`
  (recuperar 1 trecho ≈ 250 tokens): **~400× mais barato**, ~$750.
- E não são 5 livros: é a **biblioteca do mundo** (milhões). O custo escala com
  (livros × pessoas).

## Pressupostos (para poderes contestar)

- Potência GPU sob carga: **60 W** (RTX 3050 4 GB; faixa 45–75 W).
- Eletricidade: **€0,22/kWh** (Portugal/UE), **$0,17/kWh** (EUA residencial).
- Nuvem: GPU alugada **~$0,40/GPU-hora**; API de embeddings **$0,02–0,13 / 1M tokens**.
- LLM (prompt-stuffing): input **$0,30–3 / 1M tokens**.
- Conversões: **1,33 tokens/palavra**; câmbio **€1 ≈ $1,08**.
- Energia e custos **estimados**, não medidos com wattímetro nem faturados.

---

*Documento de métricas. © 2026 Gustavo de Urzêda Abreu.*
