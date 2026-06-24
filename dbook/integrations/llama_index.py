# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Gustavo de Urzêda Abreu

"""Reader de `.dbook` para o LlamaIndex.

Faz qualquer app de RAG construída em LlamaIndex ler o formato `.dbook`. Lê a
camada DURÁVEL (`structure.jsonl`) e devolve um `Document` por chunk, com
metadados ricos (título, autor, página, secção, hash do texto).

E, de bónus, a **regra de uso** do `.dbook`: se o livro já trouxer vetores para
o teu modelo, reutiliza-os com custo de embedding ZERO.

Uso:

    from dbook.integrations.llama_index import DbookReader

    docs = DbookReader().load_data("livro.dbook")   # → List[Document]
    # ... entrega `docs` ao teu VectorStoreIndex como qualquer outro reader.

Requer `llama-index-core` (extra: ``pip install "dbook[llama-index]"``).
"""

from pathlib import Path

from .. import format as fmt

try:  # caminho moderno (llama-index-core) e recuo para o antigo
    from llama_index.core import Document
    from llama_index.core.readers.base import BaseReader
except ImportError:  # pragma: no cover
    try:
        from llama_index import Document
        from llama_index.readers.base import BaseReader
    except ImportError as e:
        raise ImportError(
            "O reader .dbook precisa do llama-index-core. Instala com:\n"
            '    pip install "dbook[llama-index]"'
        ) from e


def _base_meta(path, manifest):
    return {k: v for k, v in {
        "source": manifest.get("title") or Path(path).stem,
        "title": manifest.get("title"),
        "author": manifest.get("author"),
        "language": manifest.get("language"),
        "dbook": str(path),
        "structure_sha256": manifest.get("structure_sha256"),
    }.items() if v is not None}


def _chunk_meta(base, unit):
    meta = dict(base)
    meta["chunk_id"] = unit.get("id")
    if unit.get("page"):
        meta["page"] = unit["page"]
    if unit.get("section"):
        meta["section"] = unit["section"]
    return meta


class DbookReader(BaseReader):
    """Lê um `.dbook` como documentos do LlamaIndex (camada durável)."""

    def load_data(self, dbook_path):
        path = Path(dbook_path)
        base = _base_meta(path, fmt.read_manifest(path))
        return [
            Document(text=unit["text"], metadata=_chunk_meta(base, unit))
            for unit in fmt.read_structure(path)
        ]

    def precomputed_embeddings(self, dbook_path, model, version=None):
        """A REGRA DE USO. Se o `.dbook` tiver vetores para `model`, devolve
        ``(textos, vetores, metadados)`` prontos a meter num índice **sem
        re-embeber** (custo zero). Devolve ``None`` se não houver vetores
        compatíveis — aí usas o `.load_data()` e embebes com o teu modelo.
        """
        path = Path(dbook_path)
        units, vectors, _info = fmt.load_for_model(path, model, version)
        if vectors is None:
            return None
        base = _base_meta(path, fmt.read_manifest(path))
        textos = [u["text"] for u in units]
        metas = [_chunk_meta(base, u) for u in units]
        return textos, [v.tolist() for v in vectors], metas
