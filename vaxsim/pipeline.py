"""End-to-end in-silico cancer vaccine design pipeline.

Stages (mirroring a real personalized neoantigen vaccine workflow):
  1. Load cancer-driver protein sequences.
  2. Apply somatic mutations -> generate mutation-spanning 9-mer neo-epitopes.
  3. Score each candidate:
       - binding:   HLA-A*02:01 anchor-residue heuristic
       - similarity: nearest-neighbor query against the Chroma vector DB of
                     known immunogenic epitopes
       - composite = weighted blend (novel self-distinct peptides only)
  4. Rank candidates and assemble a "string-of-beads" vaccine construct.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .binding import binding_score, anchor_status
from .data import HOTSPOT_MUTATIONS, load_all_proteins
from .mutate import generate_neoepitopes, NeoEpitope
from .vectordb import EpitopeStore

# AAY is a commonly used proteasomal-cleavage linker in string-of-beads vaccines.
LINKER = "AAY"


@dataclass
class Candidate:
    neo: NeoEpitope
    binding: float
    similarity: float
    nearest_antigen: str
    composite: float


def score_candidates(
    store: EpitopeStore,
    proteins: dict[str, str] | None = None,
    mutations: dict[str, list] | None = None,
    w_binding: float = 0.5,
    w_similarity: float = 0.5,
) -> pd.DataFrame:
    """Run mutation -> neo-epitope -> scoring for all proteins; return a DataFrame."""
    proteins = proteins or load_all_proteins()
    mutations = mutations or HOTSPOT_MUTATIONS

    rows = []
    for protein, muts in mutations.items():
        seq = proteins[protein]
        for (wt, pos, mut) in muts:
            for neo in generate_neoepitopes(protein, seq, wt, pos, mut):
                if not neo.is_novel:
                    continue  # mutation fell outside this window; skip self-peptide
                b = binding_score(neo.peptide)
                b_wt = binding_score(neo.wildtype_peptide)  # differential agretopicity
                hit = store.nearest(neo.peptide, k=1)[0]
                s = hit["similarity"]
                composite = w_binding * b + w_similarity * s
                rows.append(
                    {
                        "protein": protein,
                        "mutation": neo.mutation,
                        "peptide": neo.peptide,
                        "wildtype": neo.wildtype_peptide,
                        "mut_pos_in_peptide": neo.mut_position_in_peptide,
                        "anchors": anchor_status(neo.peptide),
                        "binding": round(b, 4),
                        "wt_binding": round(b_wt, 4),
                        "dai": round(b - b_wt, 4),  # >0: mutation creates/strengthens binding vs self
                        "similarity": round(s, 4),
                        "nearest_known": hit["epitope"],
                        "nearest_antigen": hit["antigen"],
                        "composite": round(composite, 4),
                    }
                )
    df = pd.DataFrame(rows)
    return df.sort_values("composite", ascending=False).reset_index(drop=True)


def design_vaccine(df: pd.DataFrame, top_n: int = 8, one_per_mutation: bool = True) -> dict:
    """Select top epitopes and assemble a string-of-beads construct."""
    ranked = df.copy()
    if one_per_mutation:
        ranked = ranked.sort_values("composite", ascending=False).drop_duplicates(
            subset=["protein", "mutation"], keep="first"
        )
    selected = ranked.head(top_n)
    construct = LINKER.join(selected["peptide"].tolist())
    return {
        "epitopes": selected,
        "construct": construct,
        "linker": LINKER,
        "n_epitopes": len(selected),
        "length_aa": len(construct),
    }
