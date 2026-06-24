# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Gustavo de Urzêda Abreu

"""dbook — o descodificador do formato universal "livro descodificado".

Transforma um livro (.pdf/.txt) num `.dbook`: uma pasta (ou zip) com
  • manifest.json     → identidade + integridade
  • structure.jsonl   → camada DURÁVEL (texto limpo + página + secção), agnóstica ao modelo
  • vectors/<modelo>.npz → camada PERECÍVEL, opcional, uma por modelo de embeddings

A descodificação produz SEMPRE a camada durável (o commons partilhável). Os
vetores são um extra por-modelo, adicionados à parte — é essa separação que
resolve o "nó" da não-portabilidade dos embeddings entre modelos.

Spec: docs/dbook_format.md
"""

from .format import (
    FORMAT_VERSION,
    add_vectors,
    load_for_model,
    read_manifest,
    read_structure,
    verify,
    write_dbook,
)

__all__ = [
    "FORMAT_VERSION",
    "write_dbook",
    "add_vectors",
    "load_for_model",
    "read_manifest",
    "read_structure",
    "verify",
]
