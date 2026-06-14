"""Apply mutations to a protein and generate candidate neo-epitopes.

Given a somatic point mutation at position ``p``, the mutated residue can appear
anywhere within a 9-mer presented to a T cell. We therefore slide a 9-residue
window across the mutation and emit every 9-mer that *contains* the mutated
position -- these are the candidate neoantigens for that mutation.
"""

from __future__ import annotations

from dataclasses import dataclass

from .features import PEPTIDE_LENGTH


@dataclass(frozen=True)
class NeoEpitope:
    protein: str
    mutation: str          # e.g. "G12D"
    peptide: str           # mutant 9-mer
    wildtype_peptide: str  # corresponding normal 9-mer (same window)
    mut_position_in_peptide: int  # 1-based index of the mutated residue in the 9-mer

    @property
    def id(self) -> str:
        return f"{self.protein}:{self.mutation}:{self.peptide}"

    @property
    def is_novel(self) -> bool:
        """True if the mutant 9-mer differs from the self (wild-type) 9-mer."""
        return self.peptide != self.wildtype_peptide


def apply_mutation(seq: str, wt: str, pos: int, mut: str) -> str:
    """Return ``seq`` with residue at 1-based ``pos`` changed wt->mut (validated)."""
    idx = pos - 1
    if idx < 0 or idx >= len(seq):
        raise IndexError(f"position {pos} outside protein of length {len(seq)}")
    if seq[idx] != wt:
        raise ValueError(
            f"reference mismatch at {pos}: sequence has {seq[idx]!r}, expected {wt!r}"
        )
    return seq[:idx] + mut + seq[idx + 1:]


def generate_neoepitopes(protein: str, seq: str, wt: str, pos: int, mut: str) -> list[NeoEpitope]:
    """All mutation-spanning 9-mers for one point mutation."""
    mutant_seq = apply_mutation(seq, wt, pos, mut)
    idx = pos - 1
    label = f"{wt}{pos}{mut}"
    out: list[NeoEpitope] = []
    start_min = max(0, idx - (PEPTIDE_LENGTH - 1))
    start_max = min(idx, len(seq) - PEPTIDE_LENGTH)
    for start in range(start_min, start_max + 1):
        mut_pep = mutant_seq[start:start + PEPTIDE_LENGTH]
        wt_pep = seq[start:start + PEPTIDE_LENGTH]
        if any(c not in "ACDEFGHIKLMNPQRSTVWY" for c in mut_pep):
            continue
        out.append(
            NeoEpitope(
                protein=protein,
                mutation=label,
                peptide=mut_pep,
                wildtype_peptide=wt_pep,
                mut_position_in_peptide=(idx - start) + 1,
            )
        )
    return out
