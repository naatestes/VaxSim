"""Run the full vaccine-design pipeline and stream structured stage events.

    python scripts/run_pipeline.py

Emits machine-parseable lines on stdout so a frontend can drive a live
visualization. Convention (one event per line):

    STAGE:proteins:start
    STAGE:proteins:complete:<n>
    STAGE:mutations:start
    STAGE:mutations:complete:<n>
    STAGE:candidates:start
    STAGE:candidates:progress:<done>:<total>
    STAGE:candidates:complete:<n>
    STAGE:embedding:start
    STAGE:embedding:complete:<n>
    STAGE:vectordb:start
    STAGE:vectordb:complete:<n>
    STAGE:scoring:start
    STAGE:scoring:progress:<peptide>:<composite>
    STAGE:scoring:complete:<n_selected>
    STAGE:construct:complete:<length_aa>

Any other stdout line is a plain log line. Set VAXSIM_DEMO=1 to insert small
delays so the run is watchable during a live presentation.

Outputs:
    data/candidate_neoantigens.csv   -- all scored candidates (+ pca_x, pca_y)
    data/reference_points.csv        -- 32 known epitopes (+ pca_x, pca_y)
    data/vaccine_design.txt          -- selected epitopes + final construct
"""

from pathlib import Path
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

import pandas as pd
from sklearn.decomposition import PCA

from vaxsim.data import HOTSPOT_MUTATIONS, REFERENCE_EPITOPES, load_all_proteins
from vaxsim.mutate import generate_neoepitopes
from vaxsim.features import embed_many, is_valid_peptide
from vaxsim.binding import binding_score, anchor_status
from vaxsim.vectordb import EpitopeStore
from vaxsim.pipeline import design_vaccine

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DEMO = os.environ.get("VAXSIM_DEMO") == "1"


def emit(line: str) -> None:
    print(line, flush=True)


def nap(seconds: float) -> None:
    if DEMO:
        time.sleep(seconds)


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)

    # --- Stage 1: proteins -------------------------------------------------
    emit("STAGE:proteins:start")
    nap(0.4)
    proteins = load_all_proteins()
    for name, seq in proteins.items():
        emit(f"loaded {name} ({len(seq)} aa)")
        nap(0.1)
    emit(f"STAGE:proteins:complete:{len(proteins)}")
    nap(0.3)

    # --- Stage 2: mutations ------------------------------------------------
    emit("STAGE:mutations:start")
    nap(0.3)
    mutation_list = [
        (protein, wt, pos, mut)
        for protein, muts in HOTSPOT_MUTATIONS.items()
        for (wt, pos, mut) in muts
    ]
    emit(f"applied {len(mutation_list)} oncogenic point mutations")
    emit(f"STAGE:mutations:complete:{len(mutation_list)}")
    nap(0.3)

    # --- Stage 3: candidate generation (mutation-spanning 9-mers) ----------
    emit("STAGE:candidates:start")
    neos = []
    for (protein, wt, pos, mut) in mutation_list:
        for neo in generate_neoepitopes(protein, proteins[protein], wt, pos, mut):
            if neo.is_novel:
                neos.append(neo)
    total = len(neos)
    step = max(1, total // 12)
    for done in range(step, total + step, step):
        emit(f"STAGE:candidates:progress:{min(done, total)}:{total}")
        nap(0.06)
    emit(f"STAGE:candidates:complete:{total}")
    nap(0.3)

    # --- Stage 4: embedding ------------------------------------------------
    emit("STAGE:embedding:start")
    nap(0.3)
    cand_peps = [n.peptide for n in neos]
    cand_vecs = embed_many(cand_peps)
    emit(f"embedded {total} peptides -> {cand_vecs.shape[1]}-d vectors")
    emit(f"STAGE:embedding:complete:{total}")
    nap(0.3)

    # PCA: fit the 2-D map on the *reference* epitopes, project candidates onto it.
    ref_peps, ref_meta = [], []
    for pep, antigen, category in REFERENCE_EPITOPES:
        if is_valid_peptide(pep):
            ref_peps.append(pep)
            ref_meta.append((antigen, category))
    ref_vecs = embed_many(ref_peps)
    pca = PCA(n_components=2, random_state=0).fit(ref_vecs)
    cand_xy = pca.transform(cand_vecs)
    ref_xy = pca.transform(ref_vecs)

    # --- Stage 5: vector database (load reference epitopes) ----------------
    emit("STAGE:vectordb:start")
    nap(0.3)
    store = EpitopeStore()
    n_ref = store.build(reset=True)
    emit(f"loaded {n_ref} known immunogenic epitopes into ChromaDB")
    emit(f"STAGE:vectordb:complete:{n_ref}")
    nap(0.3)

    # --- Stage 6: scoring --------------------------------------------------
    emit("STAGE:scoring:start")
    rows = []
    for i, neo in enumerate(neos):
        b = binding_score(neo.peptide)
        hit = store.nearest(neo.peptide, k=1)[0]
        s = hit["similarity"]
        rows.append(
            {
                "protein": neo.protein,
                "mutation": neo.mutation,
                "peptide": neo.peptide,
                "wildtype": neo.wildtype_peptide,
                "mut_pos_in_peptide": neo.mut_position_in_peptide,
                "anchors": anchor_status(neo.peptide),
                "binding": round(b, 4),
                "similarity": round(s, 4),
                "nearest_known": hit["epitope"],
                "nearest_antigen": hit["antigen"],
                "composite": round(0.5 * b + 0.5 * s, 4),
                "pca_x": round(float(cand_xy[i, 0]), 4),
                "pca_y": round(float(cand_xy[i, 1]), 4),
            }
        )
    df = pd.DataFrame(rows).sort_values("composite", ascending=False).reset_index(drop=True)
    csv_path = DATA / "candidate_neoantigens.csv"
    df.to_csv(csv_path, index=False)

    vaccine = design_vaccine(df, top_n=8, one_per_mutation=True)
    for _, r in vaccine["epitopes"].iterrows():
        emit(f"STAGE:scoring:progress:{r['peptide']}:{r['composite']:.4f}")
        nap(0.08)
    emit(f"STAGE:scoring:complete:{vaccine['n_epitopes']}")
    nap(0.3)

    # reference_points.csv (for the embedding-space scatter, shared PCA space)
    ref_rows = [
        {
            "peptide": pep,
            "antigen": antigen,
            "category": category,
            "pca_x": round(float(ref_xy[j, 0]), 4),
            "pca_y": round(float(ref_xy[j, 1]), 4),
        }
        for j, (pep, (antigen, category)) in enumerate(zip(ref_peps, ref_meta))
    ]
    pd.DataFrame(ref_rows).to_csv(DATA / "reference_points.csv", index=False)

    # --- Construct ---------------------------------------------------------
    txt = DATA / "vaccine_design.txt"
    with open(txt, "w") as f:
        f.write("DESIGNED CANCER VACCINE (string-of-beads construct)\n")
        f.write("=" * 55 + "\n\n")
        f.write(
            vaccine["epitopes"][
                ["protein", "mutation", "peptide", "binding", "similarity",
                 "nearest_antigen", "composite"]
            ].to_string(index=False)
        )
        f.write(f"\n\nLinker: {vaccine['linker']}\n")
        f.write(f"Construct ({vaccine['length_aa']} aa):\n{vaccine['construct']}\n")
    emit(f"STAGE:construct:complete:{vaccine['length_aa']}")

    emit(f"done: {total} candidates scored, "
         f"{vaccine['n_epitopes']}-epitope construct ({vaccine['length_aa']} aa)")


if __name__ == "__main__":
    main()
