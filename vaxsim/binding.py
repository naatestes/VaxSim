"""A transparent HLA-A*02:01 peptide-binding heuristic.

Real neoantigen pipelines predict peptide-MHC binding with neural networks such
as NetMHCpan. We deliberately use a simple, inspectable rule based on the
well-characterized HLA-A*02:01 binding motif so the logic is fully explainable
in the report. This is an educational approximation, NOT a clinical predictor.

HLA-A*02:01 motif (9-mers):
  - Primary anchor at position 2 (P2): strongly prefers L or M; tolerates I/V/A/T.
  - Primary anchor at the C-terminus (P9, "P-Omega"): prefers V or L; tolerates I/A/M/T.
  - Proline at P1/P2 and charged residues at anchor positions are unfavorable.
Reference: Rammensee et al. (1999) SYFPEITHI; Falk et al. (1991) Nature 351:290.
"""

from __future__ import annotations

P2_STRONG = {"L", "M"}
P2_OK = {"I", "V", "A", "T"}
POMEGA_STRONG = {"V", "L"}
POMEGA_OK = {"I", "A", "M", "T"}
CHARGED = {"D", "E", "K", "R"}


def binding_score(pep: str) -> float:
    """Return an HLA-A*02:01 binding score in [0, 1] (higher = stronger binder)."""
    if len(pep) != 9:
        raise ValueError("binding heuristic expects a 9-mer")
    raw = 0.0

    p2 = pep[1]
    if p2 in P2_STRONG:
        raw += 2.0
    elif p2 in P2_OK:
        raw += 1.0
    elif p2 in CHARGED:
        raw -= 1.5
    if p2 == "P":
        raw -= 2.0

    pomega = pep[-1]
    if pomega in POMEGA_STRONG:
        raw += 2.0
    elif pomega in POMEGA_OK:
        raw += 1.0
    elif pomega in CHARGED:
        raw -= 1.5

    if pep[0] == "P":
        raw -= 1.0
    # Excess charge across the peptide tends to hurt binding.
    raw -= 0.2 * sum(1 for r in pep if r in CHARGED)

    # Map raw (~[-3.5, 4]) into [0, 1].
    return max(0.0, min(1.0, (raw + 3.0) / 7.0))


def anchor_status(pep: str) -> str:
    """Human-readable summary of the anchor residues, for tables/plots."""
    return f"P2={pep[1]}, PΩ={pep[-1]}"
