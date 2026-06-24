# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Gustavo de Urzêda Abreu

"""Loader de `.dbook` para a LangChain.

Faz qualquer app de RAG construída em LangChain ler o formato `.dbook`. Lê a
camada DURÁVEL (`structure.jsonl`) e devolve um `Document` por chunk, com
metadados ricos (título, autor, página, secção, hash do texto).

E, de bónus, expõe a **regra de uso** do `.dbook`: se o livro já trouxer
vetores para o teu modelo, reutiliza-os com custo de embedding ZERO — em vez
de re-embeber o livro outra vez.

Uso:

    from dbook.integrations.langchain import DbookLoader

    docs = DbookLoader("livro.dbook").load()      # → List[Document]
    # ... mete `docs` no teu vectorstore como qualquer outro loader.

Requer `langchain-core` (extra: ``pip install "dbook[langchain]"``).
"""

from pathlib import Path

from .. import format as fmt

try:  # caminho moderno (langchain-core) e recuo para a langchain antiga
    from langchain_core.documents import Document
    from langchain_core.document_loaders import BaseLoader
except ImportError:  # pragma: no cover
    try:
        from langchain.docstore.document import Document
        from langchain.document_loaders.base import BaseLoader
    except ImportError as e:
        raise ImportError(
            "O loader .dbook precisa da langchain-core. Instala com:\n"
            '    pip install "dbook[langchain]"'
        ) from e


def _base_meta(path, manifest):
    return {
        "source": manifest.get("title") or Path(path).stem,
        "title": manifest.get("title"),
        "author": manifest.get("author"),
        "language": manifest.get("language"),
        "dbook": str(path),
        "structure_sha256": manifest.get("structure_sha256"),
    }


def _chunk_meta(base, unit):
    meta = dict(base)
    meta["chunk_id"] = unit.get("id")
    if unit.get("page"):
        meta["page"] = unit["page"]
    if unit.get("section"):
        meta["section"] = unit["section"]
    return meta


class DbookLoader(BaseLoader):
    """Carrega um `.dbook` como documentos da LangChain (camada durável)."""

    def __init__(self, path):
        self.path = Path(path)

    def lazy_load(self):
        manifest = fmt.read_manifest(self.path)
        base = _base_meta(self.path, manifest)
        for unit in fmt.read_structure(self.path):
            yield Document(page_content=unit["text"],
                           metadata=_chunk_meta(base, unit))

    def load(self):
        return list(self.lazy_load())

    def precomputed_embeddings(self, model, version=None):
        """A REGRA DE USO. Se o `.dbook` tiver uma camada de vetores para
        `model` (e versão, se dada) que case com o texto, devolve
        ``(textos, vetores, metadados)`` prontos a meter num vectorstore **sem
        re-embeber** (custo zero). Devolve ``None`` se não houver vetores
        compatíveis — aí usas o `.load()` e embebes com o teu modelo.

        Ex.: alimentar um FAISS sem recalcular um único embedding —

            res = DbookLoader(p).precomputed_embeddings("nomic-embed-text")
            if res:
                textos, vetores, metas = res
                store = FAISS.from_embeddings(
                    text_embeddings=list(zip(textos, vetores)),
                    embedding=meu_embedder, metadatas=metas)
        """
        units, vectors, _info = fmt.load_for_model(self.path, model, version)
        if vectors is None:
            return None
        base = _base_meta(self.path, fmt.read_manifest(self.path))
        textos = [u["text"] for u in units]
        metas = [_chunk_meta(base, u) for u in units]
        return textos, [v.tolist() for v in vectors], metas
