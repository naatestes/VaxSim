# HW5: NoSQL R&D Project — Consolidated Context

> Working context for planning the DS4300 HW5 group project. Combines the official
> assignment PDF (`HW5_ NoSQL R&D Project (GROUP PROJECT).pdf`) with the professor's
> (John Rachlin) verbal guidance pulled from the class transcript.

---

## 1. Logistics & Hard Constraints

- **Report due:** Monday, **June 15, 2026 @ 11:59 PM**. (Today is June 14 — ~1 day left.)
- **Points:** 100. Submitted via **Gradescope** ("external tool").
- **NO late extensions. NO regrade requests.** Submit complete and correct by the deadline.
- **Group size:** individual or **groups of up to 5 people**.
- **In-class NoSQL "conference":** informal presentations **Tue June 16 & Wed June 17**.
  - You must be ready to present even if not everyone gets called on.
  - Not formal — spend "a few minutes" / 30 sec–1 min explaining your approach.
  - The professor may pick one group per database to lead discussion; other groups
    on the same DB add commentary. Multiple groups choosing the same DB is fine/expected.
  - **June 18 is the last day of class** (attendance still required; no assignment after HW5; no final exam — project-based course).
- **Project declaration:** declare intentions + group members via the Canvas link
  (a Google sheet) before starting. (Professor wants the declaration sheet filled in.)
- **Grading weight:** computed two ways — as a 25% project OR as 20% (one of five homeworks);
  whichever yields the better grade is used. Each project reviewed by ≥2 TAs + professor.
- **Group work:** peer evaluations may be required; individual grades can be adjusted
  within a group if contribution is uneven.

---

## 2. The Big Theme / Motivation

The class is collectively "writing a book": **_NoSQL 2026: Databases and Data Science
Applications_** (Rachlin is the editor; the class conference is the proceedings).
Inspired by *Seven Databases in Seven Weeks* (now outdated). Goal: a useful, current
NoSQL reference. Overarching course goal he repeats: **broaden your toolkit** and learn
to recognize when alternative (non-relational) approaches are warranted.

---

## 3. Two Project Options — Pick ONE

### Option (a) — Database Evaluation
Pick **any NoSQL database OTHER THAN Redis, MongoDB, or Neo4j** (these were covered in class).
Write a 5+ page evaluation as if you're **evaluating the tech for your company's dev team**.

Address objectively (GO BEYOND THE PRODUCT MARKETING — be critical, negative reviews are OK):
- Key principles / data model
- Use-cases (and unique cases where it would shine)
- Would this DB be useful? Easy to install & get running? Easy or hard to work with?
- Is it scalable?
- Licensing terms
- Active community of users?
- A **tutorial demonstration** of essential features + its query language.

Frame of mind: a product-dev team member where only 1–2 people know the DB and someone
must research whether it's worth adopting vs. just sticking with SQL.

**Where to find candidate DBs:** **DB-Engines** (db-engines.com) — "database of databases,"
hundreds of options. Professor's named examples:
- Wide-column: **Cassandra** (very popular; he expects many groups to pick it)
- Time-series: **InfluxDB**, **TimescaleDB**
- Document: **CouchDB**
- Wide-column / key-value: **HBase**, **DynamoDB**
- **Vector databases** (mentioned as an interesting modern category)

### Option (b) — Data Science Application / Research
Use a NoSQL database (**any non-relational DB — the covered ones Redis/Mongo/Neo4j ARE
allowed here**) to build an application/prototype OR carry out a data science investigation.
- Document data sources and methods.
- Include **insightful visualizations** and clearly state **conclusions**.
- Focus must have **scientific, cultural, or economic significance**. Aim for **innovation
  and originality**.
- Examples he floated: social network, group messaging system, online dating site,
  bioinformatics-style analysis, or an extension of the kind of work done for the Mongo unit.
- Write 5+ page report + submit code.

---

## 4. Report Format & Guidelines

- **5+ pages, single-spaced**, including all tutorials, diagrams, visualizations.
- ⚠️ **DO NOT USE AI TO WRITE PROSE.** Quote from PDF: *"A report written by AI will not be
  well received. Do not use AI to write prose! Don't let AI rob you of your voice."*
  (You WILL be asked to declare how AI was used.)

### Required outline — Option (a) Database Investigation
1. Title
2. Full names of all team members, **alphabetical by last name**
3. Abstract
4. Introduction
5. Use-Cases
6. Tutorial demonstrating the database and its query language
7. Strengths and Weaknesses
8. Conclusions / Summary

### Required outline — Option (b) Research/Application Report
1. Title
2. Full names of all team members, **alphabetical by last name**
3. Abstract
4. Introduction
5. Methods
6. Analysis
7. Conclusions / Summary

---

## 5. What to Submit to Gradescope (ONE submission per project)

- [ ] **5+ page report / evaluation / analysis** — **PDF**
- [ ] **Data (zipped) if practical** — **ZIP**
- [ ] **5-slide PowerPoint** presentation (to deliver June 16/17) — **PDF**
- [ ] **Code (if applicable)**
- [ ] Submitter: ensure authorship of all files is clear; **add all team members** to the
      Gradescope submission.
- [ ] Declare **how you used AI** in completing the assignment.
- [ ] Document **in detail how each group member contributed**.
- [ ] ALL members must verify the project is correctly & completely submitted by the deadline.

---

## 6. Course Context That May Be Relevant (from transcript lectures)

The surrounding lectures (for grounding / possible Option-b inspiration) covered:
- **Apache Spark / PySpark**: Spark DataFrames + Spark SQL as a way to parallelize SQL-like
  ETL via data-flow programming on a Hadoop cluster (lazy evaluation, distributed jobs).
  Real-world story: replacing 200k lines of Oracle PL/SQL ETL in healthcare data
  integration (Optum) with Spark — months instead of years; data-pipeline validation
  (compare row counts, columns, dtypes, aggregations, trends) and **data provenance**.
- **Neo4j / Cypher**: music recommendation system (HW4), and the **DisGeNET** dataset
  (genes↔diseases, publication-count edges) for graph + tabular analyses.
- **Partitioning**, data-flow programming, horizontal scaling, MapReduce vs. Spark.
- Recurring theme: NoSQL adoption friction in IT orgs ("everyone knows SQL"), and the value
  of objective, hands-on evaluation over vendor marketing.

---

## 7. Decisions Made & Still Open

**DECIDED:**
- ✅ **Track: Option (b) — Data Science Application / Research.** Use a non-relational DB
  (Redis/Mongo/Neo4j ARE allowed here) for an app/prototype or data investigation with
  visualizations + clear conclusions, focused on scientific/cultural/economic significance.
  Report outline = Title → Names (alphabetical by last name) → Abstract → Introduction →
  Methods → Analysis → Conclusions.
- ✅ **Team: 2 people** (Nathaniel Estes + one groupmate).

- ✅ **Topic + DB LOCKED:** *Semantic Search Across the Cancer-Vaccine Research Frontier* —
  a **vector database** project.
  - **DB:** ChromaDB (local, `pip install`, no Docker) — genuinely non-relational / NoSQL.
  - **Data:** ~thousands of **PubMed abstracts** on cancer vaccines/immunotherapy via NCBI
    E-utilities API (free, no key for modest volume).
  - **Embeddings:** `sentence-transformers` (e.g., all-MiniLM-L6-v2), CPU-friendly.
  - **Demo:** natural-language semantic search returning relevant papers keyword/SQL search misses.
  - **Analysis:** cluster embeddings → sub-themes (mRNA, dendritic-cell, neoantigen,
    checkpoint inhibitors, **canine/veterinary**); 2D map (UMAP/t-SNE); topic growth over time.
  - **Motivating story (intro):** Yale canine cancer vaccine — Dr. Mark Mamula (EGFR/HER2),
    his own dog's death, search-and-rescue dog "Hunter" (Deana Hudgins) now cancer-free.

**REFINED BUILD (what was actually built):** pivoted from "semantic search over literature"
to an **In-Silico Cancer Vaccine Designer** — simulates the personalized neoantigen
vaccine pipeline with ChromaDB as the ranking engine.
- Pipeline: protein (UniProt) → real hotspot mutation → mutation-spanning 9-mers →
  binding heuristic (HLA-A*02:01) + vector-DB similarity to known immunogenic epitopes →
  ranked string-of-beads construct.
- **Working & tested.** Latest run: 16 mutations → 135 candidates; 32-epitope vector DB;
  top hit HER2 S310F/GFCTLVCPL (0.765); 8-epitope 93-aa construct. 3 figures generated.
- Code: `vaxsim/` package, `scripts/run_pipeline.py`, `scripts/build_notebook.py`,
  `notebooks/cancer_vaccine_designer.ipynb` (executed with outputs). See `README.md` and
  `REPORT_OUTLINE.md`.

**INTERACTIVE APP (built + browser-verified):** full-stack live ETL runner + explainer for
the class conference. FastAPI backend (`server.py`) serves a single-file React app
(`app.jsx` + `index.html`) and streams a live pipeline run via SSE. Six stage views
(Proteins → Mutations → Candidates → Embedding → Vector DB → Scoring/Construct),
data-driven from the pipeline outputs. Run with `uvicorn server:app --port 8000` →
http://localhost:8000. See `README_APP.md`.
- `scripts/run_pipeline.py` now emits `STAGE:` events + writes `pca_x/pca_y` to the CSV and a
  `data/reference_points.csv`. Mutation set expanded to 16 real point mutations (144 candidates).
- Verified in a real browser: all 6 stages render, no console errors, live run streams + reloads.

**LATER ADDITIONS (all committed + pushed):**
- 5-slide deck `slides.html` (print → PDF; embeds the validation figure); served at `/slides`.
- Validation figure `figures/fig_d_validation.png` (binding heuristic: known epitopes 0.92 vs random 0.38;
  100% vs 10% above threshold) — face-validity, not clinical validation.
- App hardened via adversarial review + made offline-capable (React/Babel vendored in `vendor/`, Tailwind
  replaced by inline CSS); failed runs no longer show as success.
- **Differential agretopicity** columns (`wt_binding`, `dai`) added to the candidate CSV — non-disruptive
  (ranking/figures unchanged). 46/144 candidates have DAI>0; rest novel at TCR-facing positions.
- Report writing scaffold: `REPORT_METHODS_ANALYSIS_GUIDE.md` (structure + numbers + citations, NOT prose).

**HONEST SCOPE (state in report):** faithful pipeline *structure*, simplified *methods* (anchor heuristic not
NetMHCpan; one HLA allele A*02:01; 9-mers only; similarity-to-known as immunogenicity proxy), *omitted*
inputs (real sequencing/variant-calling, RNA expression, clonality, self-tolerance filter) and all wet-lab/
clinical validation. Outputs are illustrative of the method, not validated targets. Researched upgrade not taken:
mhcflurry (verified pip-installable on Py3.13, ~135MB model) would make binding "real" — left as future work.

## 8. REPOS
- Khoury (primary, groupmate collaborates): `git@github.khoury.northeastern.edu:estesn/VaxSim.git` (remote `origin`)
  — STILL TODO: add groupmate as collaborator at .../estesn/VaxSim/settings/access (Write).
- Personal github.com: `git@github.com:naatestes/VaxSim.git` (remote `github`). Push to both: `git push` then `git push github main`.

## 9. SUBMISSION PLAN — due MON 2026-06-15 @ 11:59 PM (no late extensions). 4-hour plan; finish by ~10 PM.
- **Declaration sheet:** Group # (next open) · Nathaniel Estes + [groupmate] · "Application" · "ChromaDB (vector
  database)" · "Vector database (embedding store)" · Title: "In-Silico Cancer Vaccine Designer: Neoantigen
  Selection with a NoSQL Vector Database". (ChromaDB IS allowed — application track; prof named vector DBs.)
- **Hr 1–2 — REPORT (own prose, NOT AI):** split sections (A: Abstract/Intro/Methods; B: Analysis/Conclusions),
  merge, 5+ pages single-spaced, include all caveats + the 4 figures. Use `REPORT_METHODS_ANALYSIS_GUIDE.md`.
  Export PDF. Key numbers: 144 candidates, 16 mutations, 32 refs, top HER2 S310F/GFCTLVCPL 0.765, 93-aa
  construct, validation 0.92 vs 0.38, 46/144 DAI>0.
- **Hr 3 — slides + prep:** open `slides.html` → fill names → Print→PDF (5 landscape pages). Write AI-use
  declaration (AI = code/app/scaffold/research; prose by us) + per-member contribution doc. Zip code (exclude
  `.venv/`) + `data/`.
- **Hr 4 — verify + submit + rehearse:** proofread aloud; Gradescope = report PDF + 5-slide PDF + code zip +
  data zip; **add both members**; verify every file opens. Then rehearse the live app demo (`uvicorn server:app
  --port 8000`, click 6 stages + Run once), 60s talking points each for Tue/Wed (Jun 16–17) conference.
- **Definition of done:** report PDF (your prose, caveats) · 5-slide PDF w/ both names · code+data zips ·
  AI-use + contribution declarations · both members on Gradescope · all files verified · groupmate added on Khoury.
