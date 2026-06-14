"""vaxsim -- an in-silico cancer vaccine designer.

A simplified, educational simulation of the personalized neoantigen cancer
vaccine design pipeline, built around a ChromaDB vector database of known
immunogenic epitopes. See the project report for scope and limitations.
"""

from .data import (
    PROTEINS,
    HOTSPOT_MUTATIONS,
    REFERENCE_EPITOPES,
    get_protein_sequence,
    load_all_proteins,
)
from .features import embed, embed_many, PEPTIDE_LENGTH, EMBED_DIM
from .binding import binding_score, anchor_status
from .mutate import generate_neoepitopes, apply_mutation, NeoEpitope
from .vectordb import EpitopeStore
from .pipeline import score_candidates, design_vaccine, Candidate

__all__ = [
    "PROTEINS",
    "HOTSPOT_MUTATIONS",
    "REFERENCE_EPITOPES",
    "get_protein_sequence",
    "load_all_proteins",
    "embed",
    "embed_many",
    "PEPTIDE_LENGTH",
    "EMBED_DIM",
    "binding_score",
    "anchor_status",
    "generate_neoepitopes",
    "apply_mutation",
    "NeoEpitope",
    "EpitopeStore",
    "score_candidates",
    "design_vaccine",
    "Candidate",
]
