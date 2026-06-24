# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Gustavo de Urzêda Abreu

"""Quickstart — pergunta a um livro descodificado, em linguagem natural.

Faz uma pergunta a *Os Lusíadas* (Camões, 1572) e recebe a estrofe exata, com a
citação (Canto + estrofe). O livro já vem descodificado e estruturado no `.dbook`;
isto só recupera — a inteligência do raciocínio é tua (ou do teu modelo).

Requer:
  • Ollama a correr com um modelo de embeddings (aqui: bge-m3).
  • Os vetores do livro. Gera-os UMA vez (a "fatura paga uma vez"):
        python -m dbook embed biblioteca/os_lusiadas.dbook --model bge-m3
"""

import os
import sys
import unicodedata

# Correr direto da raiz do repo, sem instalar: põe a raiz no path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")  # consola Windows → acentos certos
except (AttributeError, ValueError):
    pass

import numpy as np
import requests

from dbook import format as fmt

DBOOK = "biblioteca/os_lusiadas.dbook"
MODEL = "bge-m3"
OLLAMA = "http://localhost:11434/api/embed"


def embed(texto):
    """Vetor da pergunta (mesmo pré-processamento dos chunks: sem acentos)."""
    limpo = "".join(c for c in unicodedata.normalize("NFKD", texto)
                    if not unicodedata.combining(c))
    r = requests.post(OLLAMA, json={"model": MODEL, "input": [limpo]}, timeout=60)
    r.raise_for_status()
    return np.asarray(r.json()["embeddings"][0], dtype=np.float32)


def main():
    # A REGRA DE USO: vetores já prontos (custo de embedding = ZERO).
    units, vectors, info = fmt.load_for_model(DBOOK, MODEL)
    if vectors is None:
        print("Sem vetores para", MODEL, "— gera-os uma vez com:")
        print(f"    python -m dbook embed {DBOOK} --model {MODEL}")
        return

    V = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
    print(f"📖 Os Lusíadas — {len(units)} estrofes descodificadas, prontas.\n")

    perguntas = [
        "Quem comanda a viagem dos portugueses à Índia?",
        "Quem é o velho que critica a partida dos navegadores?",
    ]
    for pergunta in perguntas:
        q = embed(pergunta)
        q /= np.linalg.norm(q)
        i = int(np.argmax(V @ q))
        u = units[i]
        verso = " ".join(u["text"].split())
        # tira a etiqueta de secção do início do texto, se lá estiver
        print(f"❓ {pergunta}")
        print(f"   → {u['section']}")
        print(f"     «{verso[:120]}…»\n")


if __name__ == "__main__":
    main()
