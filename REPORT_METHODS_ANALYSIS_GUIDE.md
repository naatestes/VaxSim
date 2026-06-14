# Methods & Analysis — Writing Scaffold

> ⚠️ **This is a scaffold, not text to paste.** The professor penalizes AI-written prose. Use
> this as a checklist: each bullet = a point to make *in your own words*, with the exact number,
> figure, or citation to fold in. Write the sentences yourself. Declare AI use (code + this
> outline) honestly on Gradescope.

Required section order (Research/Application track): Title → Names (alphabetical by last name)
→ Abstract → Introduction → **Methods** → **Analysis** → Conclusions.

---

## METHODS — what to cover (in this order)

### M1. Overview / framing (3–4 sentences)
- State plainly: this is a **simplified, educational simulation** of the personalized neoantigen
  cancer-vaccine pipeline, built as an **ETL pipeline with a NoSQL vector database at its core**.
- One sentence on scope: real biological inputs, a transparent heuristic for prediction (not clinical-grade).
- Name the stack: Python, ChromaDB (vector DB), scikit-learn, UniProt as the data source.

### M2. Data sources (be specific — this earns "provenance" credit)
- **Proteins**: 4 canonical human oncoproteins from **UniProt** — EGFR (P00533), HER2/ERBB2 (P04626),
  KRAS (P01116), TP53 (P04637). [cite UniProt]
- **Mutations**: 16 documented recurrent oncogenic **point mutations** (e.g., KRAS G12D/V/C/R, EGFR
  L858R/T790M, TP53 R175H/R248W, HER2 S310F). State they're validated against the canonical sequence
  (the code checks the wild-type residue is really at that position).
- **Reference epitopes**: 32 published **HLA-A\*02:01-restricted immunogenic CD8+ T-cell epitopes**
  (viral + tumor-associated; e.g., CMV NLVPMVATV, EBV GLCTLVAML, NY-ESO-1, HER2/neu E75 KIFGSLAFL).
  [cite IEDB / primary literature]
- Note what is **real vs. modeled** (see the provenance split): inputs real; binding/score modeled.

### M3. Candidate generation (Extract → Transform)
- Apply each mutation to its protein; slide a **9-mer window** across the mutation, keeping every window
  that contains the changed residue (9-mers = the dominant length MHC class I presents). [cite the
  neoantigen-pipeline concept]
- Filter to peptides that differ from the wild-type ("self") window. Result: **144 candidate neoantigens**.

### M4. Embedding (the vector representation)
- Each 9-mer → a **47-dimensional physicochemical vector**: 5 amino-acid property scales × 9 positions
  + 2 global features (mean hydropathy, net charge).
- Scales: Kyte–Doolittle hydropathy [Kyte & Doolittle 1982], residue volume, Grantham polarity
  [Grantham 1974], charge, aromaticity; each z-score normalized.
- Justify: you need a **numeric representation of peptide chemistry** so "similarity" is meaningful —
  string identity can't measure it. (This is what makes vector search possible.)

### M5. The vector database (the NoSQL core — give this real estate; it's a NoSQL course)
- Store the 32 reference epitope vectors in a **persistent ChromaDB collection** with **cosine** distance;
  attach metadata (source antigen, category). [cite ChromaDB docs]
- Describe the query: each candidate's vector → **nearest-neighbor search** returning the closest known
  immunogenic epitope + a similarity = 1 − cosine distance.
- **Why NoSQL, not SQL** (make this argument explicitly): ranking neoantigens *is* a similarity search
  in 47-D space; a relational `WHERE`/`JOIN` cannot express "closest in chemistry." This is the
  course-relevant payoff.

### M6. Scoring & construct assembly
- **Binding**: a transparent **HLA-A\*02:01 anchor-residue heuristic** (P2 prefers L/M, PΩ prefers V/L;
  charged anchors penalized). [cite Falk et al. 1991; Rammensee SYFPEITHI]. State clearly it is a
  simplified motif rule, **not NetMHCpan**.
- **Similarity**: cosine to nearest known immunogenic epitope (from M5).
- **Composite** = 0.5·binding + 0.5·similarity.
- Selection: top epitope per mutation → 8 epitopes joined by **AAY** proteasomal-cleavage linkers into a
  **string-of-beads** construct. [cite multi-epitope/string-of-beads vaccine design]

### M7. Reproducibility / implementation note
- Deterministic; runs in **~0.1 s** on CPU (no GPU). Mention the package (`vaxsim`) and that a live
  app + notebook reproduce every figure.

---

## ANALYSIS — what to cover (lean on the four figures)

### A1. Candidate landscape
- 144 candidates across 16 mutations / 4 proteins. Score distributions: binding mean **0.49**,
  similarity mean **0.42**, composite mean **0.46**; **15%** are strong binders (≥0.71).
- **Figure (a)** `figures/fig_a_top_per_mutation.png` — best score per mutation; which mutations yield
  the strongest targets. Comment on EGFR/HER2 prominence.

### A2. What separates the best candidates
- **Figure (b)** `figures/fig_b_binding_vs_similarity.png` — binding vs. similarity; the best targets sit
  upper-right (high on both). Discuss the trade-off and why the composite balances them.

### A3. Embedding space (ties candidates to known immunity)
- **Figure (c)** `figures/fig_c_embedding_pca.png` — PCA of the 47-D vectors; high-scoring candidates fall
  *among* the known immunogenic epitopes (the central thesis, shown visually).
- Call out a concrete hit: **HER2 S310F → `GFCTLVCPL`**, nearest known **`GLCTLVAML` (EBV BMLF1)**,
  composite **0.77** — differ at 2 positions, both strong A\*02:01 binders.

### A4. Validation (your strongest result — feature it)
- **Figure (d)** `figures/fig_d_validation.png` — the binding heuristic scores 32 known immunogenic
  epitopes far higher than 2,000 random proteome 9-mers: mean **0.92 vs 0.38**; **100% vs 10%** above the
  strong-binder threshold.
- State exactly what this shows: **face validity of the method** (it captures real HLA-A\*02:01
  immunology, not noise) — **not** clinical validation of any single candidate. This honesty matters.

### A5. The designed vaccine
- Final construct: **8 epitopes, 93 aa** (from `data/vaccine_design.txt`). Show the string.
- Tie back to motivation: EGFR/HER2 epitopes echo the **Yale canine vaccine's** targets. [cite Yale/Mamula]

### A6. Limitations (put these in Analysis or Conclusions — graders reward candor)
- Heuristic binding, not NetMHCpan; single HLA allele (A\*02:01); physicochemical (not learned)
  embeddings; no expression/proteasomal-processing filter; no experimental validation.

---

## Citations you can use (verify/format per your style)
- UniProt Consortium — uniprot.org (accessions P00533, P04626, P01116, P04637).
- Kyte J, Doolittle RF (1982). *J Mol Biol* 157:105–132. (hydropathy)
- Grantham R (1974). *Science* 185:862–864. (polarity)
- Falk K et al. (1991). *Nature* 351:290–296. (HLA-A\*02:01 motif) ; Rammensee HG et al. SYFPEITHI (1999).
- IEDB — Immune Epitope Database, iedb.org.
- ChromaDB — docs.trychroma.com.
- Yale canine cancer vaccine: news.yale.edu/2024/03/05 ; dvm360 coverage (Mamula EGFR/HER2 polyvalent).
- Personalized neoantigen / mRNA cancer-vaccine pipeline reviews (for Intro/Methods context on HLA typing,
  WES, somatic mutation calling, pMHC %rank prediction, in-vitro validation).
- NetMHCpan (Reynisson et al., 2020) — cite as the standard real predictor you approximate / future work.

> If you add a research upgrade later (e.g., a real predictor, ROC-AUC vs IEDB, or learned embeddings),
> extend M6/A4 accordingly and add the corresponding citation.
