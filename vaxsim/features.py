"""Turn a peptide string into a fixed-length numeric vector (its "embedding").

We work exclusively with 9-mers (the dominant length presented by MHC class I),
so every peptide maps to a vector of identical shape:

    9 positions x 5 physicochemical scales  = 45 per-position features
    + 2 global features (mean hydropathy, net charge) = 47 dimensions

This is a transparent, physics-based embedding -- no trained model, no GPU.
It is what gets stored in and queried against the Chroma vector database.
"""

from __future__ import annotations

import numpy as np

from .properties import AMINO_ACIDS, NORM_SCALES, HYDROPATHY, CHARGE

PEPTIDE_LENGTH = 9
EMBED_DIM = PEPTIDE_LENGTH * len(NORM_SCALES) + 2

_VALID = set(AMINO_ACIDS)


def is_valid_peptide(pep: str) -> bool:
    """True if ``pep`` is a 9-mer of standard amino acids."""
    return len(pep) == PEPTIDE_LENGTH and all(c in _VALID for c in pep)


def embed(pep: str) -> np.ndarray:
    """Embed a single 9-mer peptide into a length-47 feature vector."""
    if not is_valid_peptide(pep):
        raise ValueError(f"expected a {PEPTIDE_LENGTH}-mer of standard AAs, got {pep!r}")
    block = []
    for residue in pep:
        for scale in NORM_SCALES:
            block.append(scale[residue])
    mean_hydro = sum(HYDROPATHY[r] for r in pep) / len(pep)
    net_charge = sum(CHARGE[r] for r in pep)
    block.extend([mean_hydro / 4.5, net_charge / 3.0])  # roughly scaled to ~[-1, 1]
    return np.asarray(block, dtype=np.float32)


def embed_many(peptides: list[str]) -> np.ndarray:
    """Embed a list of peptides into a (n, 47) matrix."""
    return np.vstack([embed(p) for p in peptides])
