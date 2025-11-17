#!/usr/bin/env python3
"""Simple helper to extract text from PDFs and POST to the backend /ingest endpoint.

Usage:
  python ingest_pdfs.py --file path/to/doc.pdf --url http://127.0.0.1:8000/ingest
  python ingest_pdfs.py --dir ./pdfs --url http://127.0.0.1:8000/ingest
"""
import os
import argparse
import json
import requests
from pdfminer.high_level import extract_text


def extract_pdf_text(path: str) -> str:
    return extract_text(path)


def build_doc_from_file(path: str) -> dict:
    text = extract_pdf_text(path)
    fname = os.path.basename(path)
    doc_id = os.path.splitext(fname)[0]
    return {"id": doc_id, "text": text, "meta": {"source": fname}}


def post_docs(docs: list, ingest_url: str):
    payload = {"documents": docs}
    resp = requests.post(ingest_url, json=payload)
    try:
        print("Status:", resp.status_code)
        print(resp.json())
    except Exception:
        print(resp.text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", help="Single PDF file to ingest")
    parser.add_argument("--dir", help="Directory of PDFs to ingest")
    parser.add_argument("--url", required=True, help="Ingest endpoint URL, e.g. http://127.0.0.1:8000/ingest")
    args = parser.parse_args()

    docs = []
    if args.file:
        docs.append(build_doc_from_file(args.file))
    elif args.dir:
        for fn in os.listdir(args.dir):
            if fn.lower().endswith(".pdf"):
                path = os.path.join(args.dir, fn)
                docs.append(build_doc_from_file(path))
    else:
        print("Provide --file or --dir")
        return

    post_docs(docs, args.url)


if __name__ == "__main__":
    main()
