"""Generate the story-driven project notebook with nbformat.

Run this, then execute the notebook to populate outputs:
    python scripts/build_notebook.py
    jupyter nbconvert --to notebook --execute --inplace notebooks/cancer_vaccine_designer.ipynb
"""

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "notebooks" / "cancer_vaccine_designer.ipynb"

nb = nbf.v4.new_notebook()
cells = []


def md(text):
    cells.append(nbf.v4.new_markdown_cell(text.strip("\n")))


def code(text):
    cells.append(nbf.v4.new_code_cell(text.strip("\n")))


md(r"""
# In-Silico Cancer Vaccine Designer
### Simulating the personalized neoantigen vaccine pipeline with a vector database

*DS4300 — HW5 NoSQL R&D Project (Data Science Application)*

---

**Motivation.** At Yale, Dr. Mark Mamula's lab developed a cancer vaccine for dogs that
targets the **EGFR** and **HER2** proteins over-expressed on many tumors — work he began
after losing his own dog to an inoperable cancer. One patient, a search-and-rescue dog
named Hunter, has had no evidence of cancer after treatment. Human "personalized cancer
vaccines" (e.g. mRNA neoantigen vaccines) follow a related idea: teach the immune system
to recognize proteins that are abnormal *only* in tumor cells.

But how is such a vaccine actually *designed*? This project simulates the core
**computational pipeline** that turns a tumor's mutations into a ranked set of vaccine
targets, and uses a **NoSQL vector database (ChromaDB)** as its scientific engine: we
rank candidate neoantigens by how similar they are to *known immunogenic epitopes*.

> **Scope & honesty.** This is a **simplified, educational simulation.** Real pipelines use
> whole-exome sequencing, neural-network binding predictors (e.g. NetMHCpan), and
> laboratory validation. We reproduce the *essential ideas*, not clinical-grade prediction.
""")

md(r"""
## The pipeline at a glance

1. **Load** human cancer-driver proteins (EGFR, HER2, KRAS, TP53) from UniProt.
2. **Mutate** them with real recurrent oncogenic point mutations and slice out every
   mutation-spanning **9-mer** (the length MHC class I presents to T cells).
3. **Score** each candidate neoantigen:
   - *Binding* — an HLA-A\*02:01 anchor-residue heuristic.
   - *Similarity* — a nearest-neighbor query against a **Chroma vector DB** of known
     immunogenic epitopes.
4. **Rank** candidates and **assemble** a "string-of-beads" vaccine construct.
""")

code(r"""
import sys, os
sys.path.insert(0, os.path.abspath(".."))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

from vaxsim import (
    load_all_proteins, HOTSPOT_MUTATIONS, REFERENCE_EPITOPES,
    EpitopeStore, score_candidates, design_vaccine,
    generate_neoepitopes, embed_many, EMBED_DIM,
)

plt.rcParams["figure.dpi"] = 120
FIG = os.path.abspath("../figures")
os.makedirs(FIG, exist_ok=True)
pd.set_option("display.max_colwidth", 30)
print("peptide embedding dimensionality:", EMBED_DIM)
""")

md(r"""
## Stage 1 — Cancer-driver proteins

We pull four canonical human oncoproteins from UniProt. EGFR and HER2 are exactly the
targets of the Yale canine vaccine; KRAS and TP53 are the two most frequently mutated
genes in human cancer.
""")

code(r"""
proteins = load_all_proteins()
pd.DataFrame(
    [(name, len(seq), seq[:30] + "...") for name, seq in proteins.items()],
    columns=["protein", "length (aa)", "sequence (start)"],
)
""")

md(r"""
## Stage 2 — The NoSQL vector database (ChromaDB)

This is the heart of the project. We embed each curated **known immunogenic epitope**
(published HLA-A\*02:01 CD8+ T-cell epitopes — viral and tumor-associated) into a
47-dimensional physicochemical feature vector and store it in a persistent Chroma
collection using **cosine** distance.

A vector database is a NoSQL store optimized for one question: *"what stored items are
most similar to this query vector?"* — exactly what we need to ask of new neoantigens.
""")

code(r"""
store = EpitopeStore()
n = store.build(reset=True)
print(f"Chroma collection '{store.collection.name}' now holds {n} known epitopes.")

cats = pd.Series([c for _, _, c in REFERENCE_EPITOPES]).value_counts()
print("\nReference epitopes by category:")
print(cats.to_string())
""")

md(r"""
### Vector-DB query demo (the "query language")

Below we ask the database for the nearest known epitopes to a few peptides. This is the
core NoSQL operation: a similarity search returning ranked neighbors with metadata.
""")

code(r"""
for q in ["NLVPMVATV", "KIFGSLAFL", "LVVVGADGV"]:  # CMV, HER2/neu, KRAS-G12D neoantigen
    print(f"query peptide: {q}")
    for hit in store.nearest(q, k=3):
        print(f"   {hit['similarity']:.3f}  {hit['epitope']:>10}  ({hit['antigen']}, {hit['category']})")
    print()
""")

md(r"""
## Stage 3 — Mutation → candidate neoantigens

For a point mutation, the altered residue can sit anywhere inside a presented 9-mer, so
we emit every mutation-spanning window. Here is the KRAS **G12D** mutation as an example —
note how each candidate differs from its wild-type ("self") counterpart at one position.
""")

code(r"""
kras = proteins["KRAS"]
g12d = generate_neoepitopes("KRAS", kras, "G", 12, "D")
pd.DataFrame([
    {"peptide": n.peptide, "wildtype": n.wildtype_peptide,
     "mut_pos_in_9mer": n.mut_position_in_peptide, "novel": n.is_novel}
    for n in g12d
])
""")

md(r"""
## Stage 4 — Score every candidate

We combine the binding heuristic and the vector-DB similarity into a composite score
(equal weights). Higher = a more promising vaccine target.
""")

code(r"""
df = score_candidates(store)
print(f"Scored {len(df)} candidate neoantigens across "
      f"{df['protein'].nunique()} proteins and {df['mutation'].nunique()} mutations.\n")
df.head(12)
""")

md("## Stage 5 — Visualizations")

md("**(a) Where do the strongest candidates come from?** Best composite score per mutation.")
code(r"""
best = df.sort_values("composite", ascending=False).drop_duplicates(["protein", "mutation"])
best = best.sort_values("composite")
fig, ax = plt.subplots(figsize=(7, 5))
colors = {"EGFR": "#d62728", "HER2": "#1f77b4", "KRAS": "#2ca02c", "TP53": "#9467bd"}
ax.barh(best["protein"] + " " + best["mutation"], best["composite"],
        color=[colors[p] for p in best["protein"]])
ax.set_xlabel("composite vaccine-target score")
ax.set_title("Top neoantigen per oncogenic mutation")
plt.tight_layout(); plt.savefig(f"{FIG}/fig_a_top_per_mutation.png"); plt.show()
""")

md("**(b) Binding vs. immunogenic similarity.** Each point is a candidate; the best targets fall in the upper-right.")
code(r"""
fig, ax = plt.subplots(figsize=(7, 5.5))
sc = ax.scatter(df["binding"], df["similarity"], c=df["composite"],
                cmap="viridis", s=28, edgecolor="k", linewidth=0.3)
ax.set_xlabel("HLA-A*02:01 binding score (heuristic)")
ax.set_ylabel("similarity to known immunogenic epitopes (vector DB)")
ax.set_title("Candidate neoantigens: binding vs. immunogenic similarity")
plt.colorbar(sc, label="composite score")
plt.tight_layout(); plt.savefig(f"{FIG}/fig_b_binding_vs_similarity.png"); plt.show()
""")

md(r"""
**(c) Embedding space (PCA).** We project the 47-d vectors of known epitopes and our
candidates to 2-D. Candidates that land *inside* the cloud of known immunogenic epitopes
are, by construction, the ones the vector DB scores as most promising.
""")
code(r"""
ref_peps = [p for p, _, _ in REFERENCE_EPITOPES]
cand_peps = df["peptide"].tolist()
X = embed_many(ref_peps + cand_peps)
xy = PCA(n_components=2, random_state=0).fit_transform(X)
n_ref = len(ref_peps)

fig, ax = plt.subplots(figsize=(7.5, 6))
ax.scatter(xy[:n_ref, 0], xy[:n_ref, 1], c="crimson", marker="*", s=140,
           label="known immunogenic epitopes", edgecolor="k", linewidth=0.3)
sc = ax.scatter(xy[n_ref:, 0], xy[n_ref:, 1], c=df["composite"], cmap="viridis",
                s=26, label="candidate neoantigens", edgecolor="k", linewidth=0.3)
ax.set_title("Peptide embedding space (PCA of physicochemical vectors)")
ax.set_xlabel("PC1"); ax.set_ylabel("PC2"); ax.legend(loc="best")
plt.colorbar(sc, label="candidate composite score")
plt.tight_layout(); plt.savefig(f"{FIG}/fig_c_embedding_pca.png"); plt.show()
""")

md(r"""
## Stage 6 — The designed vaccine

Finally we select the top candidate per mutation and concatenate them with **AAY**
proteasomal-cleavage linkers — the "string-of-beads" design used in real multi-epitope
vaccines.
""")

code(r"""
vaccine = design_vaccine(df, top_n=8, one_per_mutation=True)
print(f"Selected {vaccine['n_epitopes']} epitopes | construct length {vaccine['length_aa']} aa\n")
display(vaccine["epitopes"][["protein", "mutation", "peptide", "binding",
                             "similarity", "nearest_antigen", "composite"]])
print("\nVaccine construct (string-of-beads):\n")
print(vaccine["construct"])
""")

md(r"""
## Conclusions

*(Write this section in your own words for the report.)* Talking points grounded in the run above:

- The simulation reproduces the real personalized-neoantigen pipeline end-to-end:
  **protein → mutation → 9-mer neoantigens → binding + immunogenicity scoring → construct.**
- A **NoSQL vector database** is a natural fit: ranking neoantigens *is* a nearest-neighbor
  similarity search, which Chroma answers directly — something a relational `WHERE`/`JOIN`
  cannot express over peptide chemistry.
- EGFR/HER2 candidates connect the human pipeline back to the Yale canine vaccine's targets.

**Strengths:** transparent, fast, no GPU, fully reproducible.
**Limitations:** heuristic binding (not NetMHCpan), one HLA allele, physicochemical (not
learned) embeddings, no expression/proteasomal-processing filters.
""")

nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python"},
}
OUT.parent.mkdir(parents=True, exist_ok=True)
nbf.write(nb, OUT)
print("wrote", OUT)
