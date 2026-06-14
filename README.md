# In-Silico Cancer Vaccine Designer

A simplified, educational simulation of the **personalized neoantigen cancer-vaccine
design pipeline**, built around a **ChromaDB vector database** of known immunogenic
epitopes. DS4300 HW5 — NoSQL R&D Project (Data Science Application track).

> **Scope.** This conveys the *essential ideas* of how a cancer vaccine is computationally
> designed. It is **not** a clinical tool — real pipelines use whole-exome sequencing,
> neural-network MHC binding predictors (NetMHCpan), and laboratory validation.

## What it does

`protein → oncogenic mutation → candidate 9-mer neoantigens → binding + immunogenicity
scoring → ranked vaccine construct`

The vector database is the scientific engine: candidate neoantigens are ranked by their
**similarity to known immunogenic epitopes** via a nearest-neighbor query — something a
relational database cannot express over peptide chemistry.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
# Full pipeline + data export (writes data/candidate_neoantigens.csv, data/vaccine_design.txt)
python scripts/run_pipeline.py

# Rebuild & execute the story notebook (writes figures/ and notebook outputs)
python scripts/build_notebook.py
jupyter nbconvert --to notebook --execute --inplace notebooks/cancer_vaccine_designer.ipynb
```

Or open `notebooks/cancer_vaccine_designer.ipynb` in Jupyter and run all cells.

## Layout

| Path | Purpose |
|------|---------|
| `vaxsim/properties.py` | Amino-acid physicochemical scales |
| `vaxsim/features.py` | Peptide → 47-dim feature vector (the embedding) |
| `vaxsim/data.py` | UniProt protein fetch/cache, hotspot mutations, reference epitopes |
| `vaxsim/mutate.py` | Apply mutations, generate mutation-spanning 9-mers |
| `vaxsim/binding.py` | HLA-A\*02:01 anchor-residue binding heuristic |
| `vaxsim/vectordb.py` | **ChromaDB** vector store + similarity queries |
| `vaxsim/pipeline.py` | Scoring + vaccine construct assembly |
| `notebooks/` | Story-driven notebook (report figures + live demo) |
| `scripts/` | `run_pipeline.py`, `build_notebook.py` |
| `data/` | Cached proteins, Chroma DB, exported results |
| `figures/` | Generated plots |

## Data sources

- Protein sequences: **UniProt** (EGFR P00533, HER2/ERBB2 P04626, KRAS P01116, TP53 P04637).
- Hotspot mutations: published recurrent oncogenic variants (e.g. KRAS G12D, EGFR L858R/T790M, TP53 R175H).
- Reference epitopes: curated published HLA-A\*02:01 immunogenic CD8+ T-cell epitopes (viral + tumor-associated; IEDB / primary literature).
