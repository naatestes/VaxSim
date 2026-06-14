# Report Outline & Writing Notes (5+ pages)

> ⚠️ **WRITE ALL PROSE YOURSELVES.** The professor explicitly penalizes AI-written reports
> ("Don't let AI rob you of your voice"). This file is only an outline + facts/figures to
> draw from — do NOT paste it in as text. Use it as a checklist while you write in your
> own words. The required section order for the Research/Application track is fixed
> (see below). You'll declare AI use (code scaffolding) honestly in the Gradescope form.

**Required order (Research/Application Report):** Title → Names (alphabetical by last name)
→ Abstract → Introduction → Methods → Analysis → Conclusions/Summary.

---

### Title
Something like: *"In-Silico Cancer Vaccine Designer: Simulating the Personalized Neoantigen
Pipeline with a Vector Database."* Then both team member names, alphabetical by last name.

### Abstract (~150 words)
- What you built, why vector DB, headline result (135 candidates scored, 8-epitope construct).

### Introduction
- The hook: Yale canine cancer vaccine (Dr. Mark Mamula, EGFR/HER2 targets; his own dog;
  Hunter the search-and-rescue dog now cancer-free). Bridge to human personalized
  neoantigen / mRNA cancer vaccines.
- The question: *how is a cancer vaccine actually designed?* State your goal: simulate the
  pipeline and use a NoSQL vector DB as the ranking engine.
- One sentence on scope/limitations honesty.

### Methods
- **Why NoSQL / vector DB** (the tutorial element): explain a vector DB stores items as
  vectors and answers nearest-neighbor (cosine) similarity queries — describe ChromaDB
  `PersistentClient`, `get_or_create_collection(metadata={"hnsw:space":"cosine"})`,
  `.add(ids, embeddings, metadatas)`, `.query(query_embeddings, n_results)`. Contrast with
  why SQL `WHERE`/`JOIN` can't rank by peptide chemistry.
- **Data**: 4 proteins from UniProt; real hotspot mutations; 32 curated HLA-A\*02:01
  immunogenic reference epitopes (viral + tumor).
- **Embedding**: 9-mer → 47-d physicochemical vector (5 AA scales × 9 positions + 2 global).
- **Scoring**: anchor-residue binding heuristic (HLA-A\*02:01 motif: P2=L/M, PΩ=V/L) +
  vector-DB similarity to nearest known epitope; composite = 0.5·binding + 0.5·similarity.
- **Construct**: top epitope per mutation joined with AAY linkers (string-of-beads).

### Analysis (lean on the 3 figures + tables)
- **Figure (a)** `figures/fig_a_top_per_mutation.png` — best score per mutation; which
  mutations yield the strongest targets.
- **Figure (b)** `figures/fig_b_binding_vs_similarity.png` — binding vs. similarity; top
  targets are upper-right.
- **Figure (c)** `figures/fig_c_embedding_pca.png` — PCA; high-scoring candidates fall
  among known immunogenic epitopes (the central thesis, visually).
- Table: top candidates (from `data/candidate_neoantigens.csv`). Discuss specific hits,
  e.g. **HER2 S310F → GFCTLVCPL**, nearest known = **GLCTLVAML (EBV BMLF1)**, composite 0.77;
  **KRAS G12V → LVVVGAVGV**. Note EGFR/HER2 tie back to the Yale vaccine targets.
- The final designed construct (from `data/vaccine_design.txt`): 8 epitopes, 93 aa.

### Conclusions / Summary
- Vector DB is a *natural* fit: ranking neoantigens = similarity search.
- Strengths: transparent, fast, reproducible, no GPU. Limitations: heuristic (not
  NetMHCpan) binding, single HLA allele, physicochemical (not learned) embeddings, no
  expression/processing filters. Future work: plug in mhcflurry, more alleles, ESM embeddings.

---

## Key numbers (from the latest run)
- Proteins: EGFR (1210 aa), HER2 (1255), KRAS (189), TP53 (393).
- 16 hotspot mutations → **135** scored candidate neoantigens.
- Vector DB: **32** known immunogenic epitopes (8 viral, 24 tumor).
- Top candidate: **HER2 S310F / GFCTLVCPL**, composite **0.7652**.
- Final vaccine: **8 epitopes**, **93 aa** string-of-beads construct.

## Submission checklist (Gradescope, due Mon Jun 15 11:59 PM)
- [ ] 5+ page report (PDF) — your prose.
- [ ] Code: zip the repo (exclude `.venv/`).
- [ ] Data (zip): `data/candidate_neoantigens.csv`, `data/vaccine_design.txt`, proteins cache.
- [ ] 5-slide PPT (PDF) for Jun 16/17.
- [ ] Add both members to the submission; declare AI use + per-member contributions.

## 5-slide deck suggestion
1. Title + the dog-vaccine hook. 2. The problem: how is a cancer vaccine designed?
3. Pipeline diagram + why a vector DB. 4. Results (Figure c + top-candidates table).
5. Designed construct + conclusions/limitations.
