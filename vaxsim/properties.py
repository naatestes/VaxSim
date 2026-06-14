"""Amino-acid physicochemical property scales.

These are the raw, published per-residue scales we use to turn a peptide string
into a numeric vector (see ``features.py``). Each scale is z-score normalized at
load time so no single property dominates the embedding.

Sources:
  - Hydropathy: Kyte & Doolittle (1982), J. Mol. Biol. 157:105-132.
  - Residue volume: Zamyatnin (1972), Prog. Biophys. Mol. Biol. 24:107-123.
  - Polarity: Grantham (1974), Science 185:862-864.
  - Charge at pH 7 and aromaticity: standard biochemistry.
"""

from __future__ import annotations

AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"

# Kyte-Doolittle hydropathy index (higher = more hydrophobic).
HYDROPATHY = {
    "A": 1.8, "R": -4.5, "N": -3.5, "D": -3.5, "C": 2.5,
    "Q": -3.5, "E": -3.5, "G": -0.4, "H": -3.2, "I": 4.5,
    "L": 3.8, "K": -3.9, "M": 1.9, "F": 2.8, "P": -1.6,
    "S": -0.8, "T": -0.7, "W": -0.9, "Y": -1.3, "V": 4.2,
}

# Residue side-chain volume (cubic Angstroms).
VOLUME = {
    "A": 88.6, "R": 173.4, "N": 114.1, "D": 111.1, "C": 108.5,
    "Q": 143.8, "E": 138.4, "G": 60.1, "H": 153.2, "I": 166.7,
    "L": 166.7, "K": 168.6, "M": 162.9, "F": 189.9, "P": 112.7,
    "S": 89.0, "T": 116.1, "W": 227.8, "Y": 193.6, "V": 140.0,
}

# Grantham polarity (higher = more polar).
POLARITY = {
    "A": 8.1, "R": 10.5, "N": 11.6, "D": 13.0, "C": 5.5,
    "Q": 10.5, "E": 12.3, "G": 9.0, "H": 10.4, "I": 5.2,
    "L": 4.9, "K": 11.3, "M": 5.7, "F": 5.2, "P": 8.0,
    "S": 9.2, "T": 8.6, "W": 5.4, "Y": 6.2, "V": 5.9,
}

# Net side-chain charge at physiological pH (~7.4).
CHARGE = {aa: 0.0 for aa in AMINO_ACIDS}
CHARGE.update({"D": -1.0, "E": -1.0, "K": 1.0, "R": 1.0, "H": 0.1})

# Aromatic side chain indicator.
AROMATIC = {aa: 0.0 for aa in AMINO_ACIDS}
AROMATIC.update({"F": 1.0, "W": 1.0, "Y": 1.0, "H": 1.0})

# The ordered list of scales used to build the per-residue feature block.
SCALES = [HYDROPATHY, VOLUME, POLARITY, CHARGE, AROMATIC]


def _zscore(scale: dict[str, float]) -> dict[str, float]:
    vals = [scale[a] for a in AMINO_ACIDS]
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    std = var ** 0.5 or 1.0
    return {a: (scale[a] - mean) / std for a in AMINO_ACIDS}


# Normalized copies used by the feature builder.
NORM_SCALES = [_zscore(s) for s in SCALES]
