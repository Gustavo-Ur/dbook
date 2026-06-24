# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Gustavo de Urzêda Abreu

"""CLI do descodificador .dbook.

    python -m dbook encode "livro.pdf" [--ocr] [--embed] [--model nomic-embed-text]
    python -m dbook embed  "livro.dbook" --model nomic-embed-text
    python -m dbook info   "livro.dbook"
    python -m dbook verify "livro.dbook"
"""

import argparse
import sys
from pathlib import Path

from . import format as fmt
from .embedders import OllamaEmbedder
from .extract import CHUNK_WORDS, OVERLAP_WORDS, book_to_units


def _embedder(args):
    return OllamaEmbedder(
        model=args.model, version=args.model_version,
        url=args.url, batch=args.batch,
    )


def cmd_encode(args):
    livro = Path(args.book)
    if not livro.exists():
        print(f"não existe: {livro}")
        return 1
    out = Path(args.out) if args.out else livro.with_suffix(".dbook")

    print(f"descodificar: {livro.name}")

    def prog_ocr(i, total):
        print(f"  OCR {i}/{total} págs", flush=True)

    units, npags = book_to_units(
        livro, clean=not args.no_clean, ocr=args.ocr, progress=prog_ocr)
    if not units:
        print("sem texto (PDF só-imagem? tenta --ocr)")
        return 1

    fmt.write_dbook(
        out, units,
        source=str(livro), title=args.title, author=args.author,
        language=args.language, npages=npags, cleaned=not args.no_clean,
        chunking={"method": "sentences", "target_words": CHUNK_WORDS,
                  "overlap_words": OVERLAP_WORDS},
    )
    print(f"  camada durável: {len(units)} chunks, {npags} págs → {out}")

    if args.embed:
        _do_embed(out, args)

    print("feito.")
    if args.zip:
        _zip(out)
    return 0


def _do_embed(dbook_dir, args):
    emb = _embedder(args)
    print(f"  embeber com {emb.name}@{emb.version} (lote={emb.batch})…")

    def prog(i, total):
        if i == total or i % (emb.batch * 5) == 0:
            print(f"    {i}/{total} chunks", flush=True)

    nome, dim = fmt.add_vectors(dbook_dir, emb, progress=prog)
    print(f"  camada de vetores: {nome} (dim {dim})")


def cmd_embed(args):
    dbook_dir = Path(args.dbook)
    if not (dbook_dir / fmt.MANIFEST).exists():
        print(f"não é um .dbook: {dbook_dir}")
        return 1
    _do_embed(dbook_dir, args)
    print("feito.")
    return 0


def cmd_info(args):
    m = fmt.read_manifest(args.dbook)
    print(f"{m['title']}  ({m.get('author') or 's/ autor'})")
    print(f"  formato : {m['format']}")
    print(f"  língua  : {m.get('language')}   páginas: {m.get('pages')}   chunks: {m['chunks']}")
    print(f"  fonte   : {m.get('source')}")
    print(f"  texto sha256: {m['structure_sha256'][:16]}…   limpo: {m.get('cleaned')}")
    va = m.get("vectors_available") or []
    print(f"  vetores : {', '.join(va) if va else '(nenhum — camada durável apenas)'}")
    return 0


def cmd_verify(args):
    ok, problemas = fmt.verify(args.dbook)
    if ok:
        print("OK — íntegro (texto e vetores consistentes).")
        return 0
    print("PROBLEMAS:")
    for p in problemas:
        print(f"  - {p}")
    return 1


def _zip(dbook_dir):
    import shutil
    dbook_dir = Path(dbook_dir)
    base = dbook_dir.with_suffix("")  # remove .dbook
    z = shutil.make_archive(str(base), "zip", root_dir=dbook_dir)
    destino = dbook_dir.with_suffix(".dbook.zip")
    Path(z).replace(destino)
    print(f"  zip: {destino}")


def main(argv=None):
    # Consola Windows é cp1252 por defeito → acentos/setas rebentam. Força UTF-8.
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    p = argparse.ArgumentParser(prog="dbook", description="Descodificador do formato .dbook")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_embed_opts(sp):
        sp.add_argument("--model", default="nomic-embed-text")
        sp.add_argument("--model-version", default="unknown")
        sp.add_argument("--url", default="http://localhost:11434/api/embed")
        sp.add_argument("--batch", type=int, default=32)

    e = sub.add_parser("encode", help="livro → .dbook (camada durável)")
    e.add_argument("book")
    e.add_argument("--out")
    e.add_argument("--title")
    e.add_argument("--author")
    e.add_argument("--language")
    e.add_argument("--no-clean", action="store_true", help="não remover boilerplate")
    e.add_argument("--ocr", action="store_true", help="OCR para PDFs só-imagem")
    e.add_argument("--embed", action="store_true", help="adicionar logo a camada de vetores")
    e.add_argument("--zip", action="store_true", help="empacotar em .dbook.zip no fim")
    add_embed_opts(e)
    e.set_defaults(func=cmd_encode)

    m = sub.add_parser("embed", help="adicionar camada de vetores a um .dbook")
    m.add_argument("dbook")
    add_embed_opts(m)
    m.set_defaults(func=cmd_embed)

    i = sub.add_parser("info", help="mostrar o manifest")
    i.add_argument("dbook")
    i.set_defaults(func=cmd_info)

    v = sub.add_parser("verify", help="conferir integridade")
    v.add_argument("dbook")
    v.set_defaults(func=cmd_verify)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
