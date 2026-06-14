"""Reference data: cancer-driver proteins, hotspot mutations, known epitopes.

Protein sequences are fetched once from UniProt (REST API) and cached under
``data/proteins/``. Hotspot mutations are real, well-documented oncogenic
variants. The reference epitope set is a curated list of published, immunogenic
HLA-A*02:01-restricted CD8+ T-cell epitopes (viral + tumor-associated), which
seeds the vector database of "what immunogenic peptides look like."
"""

from __future__ import annotations

import os
from pathlib import Path

import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROTEIN_DIR = DATA_DIR / "proteins"

# UniProt accessions for canonical human cancer-driver proteins.
# EGFR and HER2/ERBB2 are the exact targets of the Yale canine cancer vaccine.
PROTEINS = {
    "EGFR": "P00533",
    "HER2": "P04626",   # gene ERBB2
    "KRAS": "P01116",
    "TP53": "P04637",
}

# Real recurrent oncogenic point mutations (1-based positions, canonical isoform).
# Format: (wild-type residue, position, mutant residue).
HOTSPOT_MUTATIONS = {
    "EGFR": [("L", 858, "R"), ("T", 790, "M"), ("G", 719, "S")],
    "HER2": [("S", 310, "F"), ("V", 777, "L"), ("R", 678, "Q")],
    "KRAS": [("G", 12, "D"), ("G", 12, "V"), ("G", 12, "C"), ("G", 12, "R"), ("G", 13, "D")],
    "TP53": [("R", 175, "H"), ("R", 248, "W"), ("R", 248, "Q"), ("R", 273, "H"), ("G", 245, "S")],
}

# Curated published HLA-A*02:01 immunogenic 9-mer epitopes.
# (peptide, source antigen, category). These seed the vector DB.
REFERENCE_EPITOPES = [
    # --- Viral (canonical CD8 epitopes) ---
    ("NLVPMVATV", "CMV pp65", "viral"),
    ("GLCTLVAML", "EBV BMLF1", "viral"),
    ("GILGFVFTL", "Influenza A M1", "viral"),
    ("CLGGLLTMV", "EBV LMP2A", "viral"),
    ("FLYALALLL", "EBV LMP2A", "viral"),
    ("SLYNTVATL", "HIV-1 Gag", "viral"),
    ("ILKEPVHGV", "HIV-1 RT", "viral"),
    ("LLFGYPVYV", "HTLV-1 Tax", "viral"),
    # --- Tumor-associated antigens ---
    ("AAGIGILTV", "Melan-A/MART-1", "tumor"),
    ("IMDQVPFSV", "gp100", "tumor"),
    ("KTWGQYWQV", "gp100", "tumor"),
    ("YLEPGPVTA", "gp100", "tumor"),
    ("ITDQVPFSV", "gp100", "tumor"),
    ("SLLMWITQC", "NY-ESO-1", "tumor"),
    ("SLLMWITQV", "NY-ESO-1", "tumor"),
    ("RMFPNAPYL", "WT1", "tumor"),
    ("CMTWNQMNL", "WT1", "tumor"),
    ("VLDFAPPGA", "WT1", "tumor"),
    ("ILAKFLHWL", "hTERT", "tumor"),
    ("RLVDDFLLV", "hTERT", "tumor"),
    ("LLGRNSFEV", "p53", "tumor"),
    ("KIFGSLAFL", "HER2/neu (E75)", "tumor"),
    ("IISAVVGIL", "HER2/neu", "tumor"),
    ("ALCRWGLLL", "HER2/neu", "tumor"),
    ("RLLQETELV", "HER2/neu", "tumor"),
    ("YLSGANLNL", "CEA", "tumor"),
    ("FLWGPRALV", "MAGE-A3", "tumor"),
    ("KVAELVHFL", "MAGE-A3", "tumor"),
    ("YMDGTMSQV", "Tyrosinase", "tumor"),
    ("STAPPVHNV", "MUC1", "tumor"),
    ("VLDGLDVLL", "PRAME", "tumor"),
    ("LMLGEFLKL", "Survivin", "tumor"),
]


def _fetch_uniprot_fasta(accession: str) -> str:
    url = f"https://rest.uniprot.org/uniprotkb/{accession}.fasta"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    lines = resp.text.splitlines()
    return "".join(l.strip() for l in lines if not l.startswith(">"))


def get_protein_sequence(name: str, refresh: bool = False) -> str:
    """Return the amino-acid sequence for a named protein, fetching+caching once."""
    if name not in PROTEINS:
        raise KeyError(f"unknown protein {name!r}; known: {list(PROTEINS)}")
    PROTEIN_DIR.mkdir(parents=True, exist_ok=True)
    cache = PROTEIN_DIR / f"{name}.fasta"
    if cache.exists() and not refresh:
        return cache.read_text().strip()
    seq = _fetch_uniprot_fasta(PROTEINS[name])
    cache.write_text(seq)
    return seq


def load_all_proteins(refresh: bool = False) -> dict[str, str]:
    return {name: get_protein_sequence(name, refresh=refresh) for name in PROTEINS}
