"""ChromaDB vector store for immunogenic epitopes.

This is the NoSQL core of the project. We store the curated reference epitopes as
vectors (with antigen/category metadata) in a persistent Chroma collection using
cosine distance. Candidate neoantigens are then ranked by how similar they are to
known immunogenic peptides -- a nearest-neighbor query against the vector DB.

Chroma returns cosine *distance* (0 = identical direction). We convert to a
similarity in [0, 1] as ``similarity = 1 - distance``.
"""

from __future__ import annotations

from pathlib import Path

import chromadb

from .data import REFERENCE_EPITOPES
from .features import embed, embed_many, is_valid_peptide

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "chroma"
COLLECTION = "known_epitopes"


class EpitopeStore:
    """Thin wrapper around a persistent Chroma collection of known epitopes."""

    def __init__(self, path: Path | str = DEFAULT_DB_PATH):
        Path(path).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(path))
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION, metadata={"hnsw:space": "cosine"}
        )

    def build(self, reset: bool = True) -> int:
        """(Re)load the curated reference epitopes into the collection."""
        if reset:
            try:
                self.client.delete_collection(COLLECTION)
            except Exception:
                pass
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION, metadata={"hnsw:space": "cosine"}
            )
        peps, metas = [], []
        for peptide, antigen, category in REFERENCE_EPITOPES:
            if not is_valid_peptide(peptide):
                continue
            peps.append(peptide)
            metas.append({"antigen": antigen, "category": category})
        embeddings = embed_many(peps).tolist()
        self.collection.add(
            ids=peps,
            embeddings=embeddings,
            documents=peps,
            metadatas=metas,
        )
        return self.collection.count()

    def nearest(self, peptide: str, k: int = 3) -> list[dict]:
        """Return the k most similar known epitopes to ``peptide``."""
        res = self.collection.query(
            query_embeddings=[embed(peptide).tolist()],
            n_results=k,
        )
        out = []
        for pep, meta, dist in zip(
            res["documents"][0], res["metadatas"][0], res["distances"][0]
        ):
            out.append(
                {
                    "epitope": pep,
                    "antigen": meta["antigen"],
                    "category": meta["category"],
                    "similarity": round(1.0 - float(dist), 4),
                }
            )
        return out

    def similarity_score(self, peptide: str) -> float:
        """Similarity to the single nearest known immunogenic epitope, in [0, 1]."""
        hit = self.nearest(peptide, k=1)
        return hit[0]["similarity"] if hit else 0.0

    def count(self) -> int:
        return self.collection.count()
