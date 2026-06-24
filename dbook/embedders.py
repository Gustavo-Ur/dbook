# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Gustavo de Urzêda Abreu

"""Camada perecível: embebedores. Cada um produz vetores no espaço de UM modelo.

O formato é agnóstico ao fornecedor — qualquer embebedor que cumpra a interface
(name, version, dim, preprocess, embed) serve. Aqui vem o do Ollama (local), mas
acrescentar OpenAI/Google/etc. é só mais uma classe.
"""

import time
import unicodedata

import requests


def deaccent(text):
    """Tira acentos (NFKD). O OCR de scans come acentos; normalizar aqui faz
    chunks e perguntas casarem. Registado nos metadados como 'nfkd-deaccent'
    para quem usar os vetores embeber as perguntas da MESMA forma."""
    return "".join(
        c for c in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(c)
    )


class OllamaEmbedder:
    """Embebedor via Ollama /api/embed (em lote — ~14x mais rápido que um-a-um)."""

    def __init__(self, model="nomic-embed-text", version="unknown",
                 url="http://localhost:11434/api/embed", batch=32,
                 keep_alive="30m", preprocess="nfkd-deaccent",
                 timeout=120, retries=3):
        self.model = model
        self.version = version
        self.url = url
        self.batch = batch
        self.keep_alive = keep_alive
        self.preprocess = preprocess
        self.timeout = timeout
        self.retries = retries
        self._dim = None

    @property
    def name(self):
        return self.model

    @property
    def dim(self):
        return self._dim

    def _prep(self, text):
        return deaccent(text) if self.preprocess == "nfkd-deaccent" else text

    def embed(self, texts, progress=None):
        """Lista de textos → lista de vetores (em sub-lotes, com retentativas)."""
        if not texts:
            return []
        vetores, total = [], len(texts)
        for inicio in range(0, total, self.batch):
            lote = [self._prep(t) for t in texts[inicio:inicio + self.batch]]
            payload = {"model": self.model, "input": lote, "keep_alive": self.keep_alive}
            ultimo = None
            for tentativa in range(self.retries):
                try:
                    r = requests.post(self.url, json=payload, timeout=self.timeout)
                    r.raise_for_status()
                    vetores.extend(r.json()["embeddings"])
                    break
                except (requests.exceptions.Timeout,
                        requests.exceptions.ConnectionError) as e:
                    ultimo = e
                    time.sleep(2 * (tentativa + 1))
            else:
                raise ultimo
            if progress:
                progress(min(inicio + self.batch, total), total)
        if vetores:
            self._dim = len(vetores[0])
        return vetores
