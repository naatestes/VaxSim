/* In-Silico Cancer Vaccine Designer — interactive ETL explainer + live runner.
   Single-file React app. Data-driven from the FastAPI backend; only the narration
   copy and the Stage-3 sliding-window example are hardcoded. */

const { useState, useEffect, useRef, useMemo } = React;

/* ----------------------------------------------------------------- palette */
const C = {
  red: "#C0392B", yellow: "#D4AC0D", blue: "#2471A3", green: "#1E8449",
  ink: "#111111", gray: "#555555", rule: "#E6E6E6",
};

/* stages: key, label, headline, accent color */
const STAGES = [
  { key: "proteins",  label: "Stage 01", name: "Proteins",            headline: "Four cancer-driver proteins", accent: C.gray },
  { key: "mutations", label: "Stage 02", name: "Mutations",           headline: "Sixteen oncogenic mutations", accent: C.red },
  { key: "candidates",label: "Stage 03", name: "Candidates",          headline: "Mutation-spanning neoantigens", accent: C.yellow },
  { key: "embedding", label: "Stage 04", name: "Embedding",           headline: "Peptides become vectors",     accent: C.blue },
  { key: "vectordb",  label: "Stage 05", name: "Vector Database",     headline: "Search against known immunity", accent: C.blue },
  { key: "scoring",   label: "Stage 06", name: "Scoring & Construct", headline: "Rank, select, assemble",       accent: C.green },
];

const PROTEIN_META = {
  EGFR: { acc: "P00533", len: 1210 },
  HER2: { acc: "P04626", len: 1255 },
  KRAS: { acc: "P01116", len: 189 },
  TP53: { acc: "P04637", len: 393 },
};
const PROTEIN_TINT = { EGFR: "#C0392B", HER2: "#2471A3", KRAS: "#1E8449", TP53: "#7D3C98" };
const MAX_LEN = 1255;

/* Stage-3 hardcoded concept example: KRAS G12V local context.
   Positions 4..20 of KRAS; the mutated residue (G12V) is index 8 (the V). */
const KRAS_CONTEXT = "YKLVVVGAVGVGKSALT";
const KRAS_MUT_IDX = 8;

/* amino-acid physicochemical scales — identical to vaxsim/properties.py */
const AA = "ACDEFGHIKLMNPQRSTVWY";
const HYDRO = { A:1.8,R:-4.5,N:-3.5,D:-3.5,C:2.5,Q:-3.5,E:-3.5,G:-0.4,H:-3.2,I:4.5,L:3.8,K:-3.9,M:1.9,F:2.8,P:-1.6,S:-0.8,T:-0.7,W:-0.9,Y:-1.3,V:4.2 };
const VOL   = { A:88.6,R:173.4,N:114.1,D:111.1,C:108.5,Q:143.8,E:138.4,G:60.1,H:153.2,I:166.7,L:166.7,K:168.6,M:162.9,F:189.9,P:112.7,S:89.0,T:116.1,W:227.8,Y:193.6,V:140.0 };
const POL   = { A:8.1,R:10.5,N:11.6,D:13.0,C:5.5,Q:10.5,E:12.3,G:9.0,H:10.4,I:5.2,L:4.9,K:11.3,M:5.7,F:5.2,P:8.0,S:9.2,T:8.6,W:5.4,Y:6.2,V:5.9 };
const CHG   = (() => { const o={}; AA.split("").forEach(a=>o[a]=0); Object.assign(o,{D:-1,E:-1,K:1,R:1,H:0.1}); return o; })();
const ARO   = (() => { const o={}; AA.split("").forEach(a=>o[a]=0); Object.assign(o,{F:1,W:1,Y:1,H:1}); return o; })();
const SCALE_DEFS = [
  { name: "Hydropathy", map: HYDRO },
  { name: "Volume",     map: VOL },
  { name: "Polarity",   map: POL },
  { name: "Charge",     map: CHG },
  { name: "Aromatic",   map: ARO },
];

const mean = (a) => a.reduce((s, x) => s + x, 0) / a.length;
function zscore(map) {
  const vals = AA.split("").map((a) => map[a]);
  const m = mean(vals);
  const sd = Math.sqrt(mean(vals.map((v) => (v - m) ** 2))) || 1;
  const o = {};
  AA.split("").forEach((a) => (o[a] = (map[a] - m) / sd));
  return o;
}
const NSCALES = SCALE_DEFS.map((s) => zscore(s.map));
const SCALE_RANGE = SCALE_DEFS.map((s) => {
  const vals = AA.split("").map((a) => s.map[a]);
  return { min: Math.min(...vals), max: Math.max(...vals) };
});
// neutral blue-gray ramp for the 5 scale categories (keeps the 4 semantic accents free)
const SCALE_COLORS = ["#9FB3C0", "#6E8DA1", "#2471A3", "#17527C", "#0E3A57"];

/* JS mirror of features.embed(): 9*5 + 2 global = 47-d */
function embed(pep) {
  const v = [];
  for (const r of pep) for (const s of NSCALES) v.push(s[r] ?? 0);
  const mh = mean([...pep].map((r) => HYDRO[r] ?? 0)) / 4.5;
  const nc = [...pep].reduce((a, r) => a + (CHG[r] ?? 0), 0) / 3.0;
  v.push(mh, nc);
  return v;
}

/* blue → white → red color ramp for a roughly [-2.5, 2.5] value */
function lerpHex(h1, h2, t) {
  const p = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const a = p(h1), b = p(h2);
  const c = a.map((x, i) => Math.round(x + (b[i] - x) * t));
  return `rgb(${c[0]},${c[1]},${c[2]})`;
}
function valColor(v) {
  const t = Math.max(-1, Math.min(1, v / 2.5));
  return t < 0 ? lerpHex("#2471A3", "#FFFFFF", 1 + t) : lerpHex("#FFFFFF", "#C0392B", t);
}

/* ------------------------------------------------------------- narration */
const NARRATION = {
  proteins:
    "You are looking at the four proteins this pipeline starts from — EGFR, HER2, KRAS and TP53, the genes most frequently mutated across human solid tumors. Their full amino-acid sequences were downloaded from UniProt. EGFR and HER2 are the same proteins the Yale canine cancer vaccine targets.",
  mutations:
    "Each badge is a real, recurrent mutation found in patient tumors — a single amino-acid swapped for another (G → V, R → H, and so on). These are not random: they are the exact changes that drive cancer, and the change itself is what the vaccine will teach the immune system to recognize.",
  candidates:
    "A mutation can sit anywhere inside the short peptide that an MHC molecule displays to a T-cell, so we slide a 9-residue window across it and keep every window that contains the change. Each is a candidate neoantigen — a fragment that exists only in tumor cells. Across all 16 mutations this produced 144 candidates.",
  embedding:
    "You cannot compare peptides as plain text — 'similar' has to mean similar chemistry. So each 9-mer is converted into a 47-number vector built from five physicochemical scales at every position. That numeric fingerprint is what makes mathematical similarity search possible in the next stage.",
  vectordb:
    "Each candidate's vector is queried against a ChromaDB database of 32 known immunogenic epitopes. GFCTLVCPL, the top HER2 candidate, lands closest to GLCTLVAML — an Epstein-Barr virus peptide known to activate CD8+ T-cells. That chemical resemblance is the evidence the immune system is likely to see it too. A SQL WHERE clause cannot ask this question.",
  scoring:
    "Every candidate gets a composite score — half binding strength, half similarity to known immunity. The top epitope from each mutation is selected and the eight winners are strung together with AAY linkers into one 93-amino-acid vaccine construct. The immune system cleaves the linkers and processes each target on its own.",
};

/* --------------------------------------------------------------- helpers */
function parseConstruct(text) {
  if (!text) return { epitopes: [], length: 0, construct: "" };
  let construct = "", length = 0;
  const m = text.match(/Construct \((\d+) aa\):\s*([A-Z]+)/);
  if (m) { length = +m[1]; construct = m[2]; }
  else {
    const lines = text.trim().split(/\n/);
    const last = (lines[lines.length - 1] || "").trim();
    if (/^[A-Z]{12,}$/.test(last)) { construct = last; length = last.length; }
  }
  const epitopes = [];
  for (let i = 0; i < construct.length; i += 12) epitopes.push(construct.slice(i, i + 9));
  return { epitopes, length, construct };
}

async function getJSON(path, fallback) {
  try {
    const r = await fetch(path);
    if (!r.ok) throw new Error(r.status);
    return await r.json();
  } catch (e) { return fallback; }
}
async function getText(path, fallback) {
  try {
    const r = await fetch(path);
    if (!r.ok) throw new Error(r.status);
    return await r.text();
  } catch (e) { return fallback; }
}

/* ------------------------------------------------------------------ icons */
const Icon = ({ d, accent }) => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={accent}
       strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">{d}</svg>
);
const ICONS = {
  proteins:  <Icon accent="currentColor" d={<><circle cx="12" cy="12" r="3"/><path d="M5 8v8M19 8v8M5 8l7-4 7 4M5 16l7 4 7-4"/></>} />,
  mutations: <Icon accent="currentColor" d={<path d="M13 2 5 14h6l-2 8 8-12h-6z"/>} />,
  candidates:<Icon accent="currentColor" d={<><rect x="3" y="4" width="18" height="4"/><rect x="3" y="10" width="18" height="4"/><rect x="3" y="16" width="18" height="4"/></>} />,
  embedding: <Icon accent="currentColor" d={<><path d="M4 20V10M9 20V4M14 20v-8M19 20V7"/></>} />,
  vectordb:  <Icon accent="currentColor" d={<><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/></>} />,
  scoring:   <Icon accent="currentColor" d={<><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></>} />,
};

/* ============================================================== SIDEBAR */
function Sidebar({ stageStatus, active, onPick, counts, running }) {
  return (
    <div className="flex flex-col" style={{ width: 280, borderRight: `1px solid ${C.rule}`, minHeight: "100%" }}>
      <div style={{ padding: "26px 24px 18px" }}>
        <div className="font-mono" style={{ fontSize: 11, letterSpacing: 2, color: C.gray, textTransform: "uppercase" }}>
          ETL Pipeline
        </div>
        <div className="font-display" style={{ fontSize: 26, lineHeight: 1.1, marginTop: 6 }}>
          Cancer Vaccine<br />Designer
        </div>
      </div>
      <hr className="rule" />
      <div style={{ padding: "10px 0" }}>
        {STAGES.map((s, i) => {
          const st = stageStatus[s.key] || "idle";
          const isActive = i === active;
          const reachable = !running || st === "complete";  // browse freely when idle
          const dotColor = st === "complete" ? s.accent : st === "running" ? s.accent : st === "error" ? C.red : "#CFCFCF";
          return (
            <div key={s.key}
                 onClick={() => reachable && onPick(i)}
                 className="flex items-center"
                 style={{
                   padding: "12px 22px", gap: 14,
                   cursor: reachable ? "pointer" : "default",
                   background: isActive ? "#FAFAFA" : "transparent",
                   borderLeft: isActive ? `3px solid ${s.accent}` : "3px solid transparent",
                 }}>
              <div className={st === "running" ? "pulse" : ""}
                   style={{
                     width: 26, height: 26, flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center",
                     border: `1px solid ${st === "idle" ? "#D5D5D5" : dotColor}`,
                     background: st === "complete" ? dotColor : "#FFFFFF",
                     color: st === "complete" ? "#FFFFFF" : dotColor,
                   }}>
                {ICONS[s.key]}
              </div>
              <div style={{ flex: 1 }}>
                <div className="font-mono" style={{ fontSize: 9.5, letterSpacing: 1.5, color: C.gray, textTransform: "uppercase" }}>{s.label}</div>
                <div className="font-body" style={{ fontSize: 14, color: st === "idle" ? "#9A9A9A" : C.ink, fontWeight: 500 }}>{s.name}</div>
              </div>
              {counts[s.key] != null && (
                <div className="font-mono" style={{ fontSize: 12, color: st === "idle" ? "#BBB" : s.accent, minWidth: 30, textAlign: "right" }}>
                  {counts[s.key]}
                </div>
              )}
            </div>
          );
        })}
      </div>
      <hr className="rule" />
      <div style={{ padding: "16px 24px", fontSize: 11, color: C.gray }} className="font-body">
        A simplified educational simulation of the personalized neoantigen vaccine pipeline.
      </div>
    </div>
  );
}

/* ============================================================ StageShell */
function StageShell({ stage, children }) {
  return (
    <div className="flex flex-col" style={{ flex: 1, padding: "34px 48px 18px", overflowY: "auto" }}>
      <div className="font-mono" style={{ fontSize: 12, letterSpacing: 2, color: stage.accent, textTransform: "uppercase" }}>
        {stage.label} · {stage.name}
      </div>
      <div className="font-display" style={{ fontSize: 46, lineHeight: 1.05, margin: "6px 0 18px", color: C.ink }}>
        {stage.headline}
      </div>
      <hr className="rule" />
      <div style={{ padding: "26px 0", flex: 1 }}>{children}</div>
    </div>
  );
}

const Empty = () => (
  <div className="font-body" style={{ color: C.gray, fontSize: 15 }}>
    No data yet — click <strong>Run Pipeline</strong> below to generate results.
  </div>
);

/* ============================================================= STAGE 1 */
function StageProteins({ candidates, revealed, running }) {
  const present = useMemo(() => {
    const set = new Set(candidates.map((r) => r.protein));
    return Object.keys(PROTEIN_META).filter((p) => set.has(p) || !candidates.length);
  }, [candidates]);
  if (!candidates.length && !running) return <Empty />;
  return (
    <div className="grid grid-cols-4" style={{ gap: 18 }}>
      {Object.keys(PROTEIN_META).map((p) => {
        const meta = PROTEIN_META[p];
        const show = running ? revealed.has(p) : present.includes(p);
        return (
          <div key={p} style={{ border: `1px solid ${C.rule}`, padding: "22px 20px", opacity: show ? 1 : 0.18, transition: "opacity .4s" }}>
            <div className="font-display" style={{ fontSize: 34, lineHeight: 1 }}>{p}</div>
            <div className="font-mono" style={{ fontSize: 12, color: C.gray, marginTop: 8 }}>{meta.acc}</div>
            <div className="font-mono" style={{ fontSize: 13, marginTop: 16 }}>{meta.len} aa</div>
            <div style={{ height: 6, background: "#F0F0F0", marginTop: 8 }}>
              <div style={{ height: "100%", width: `${(meta.len / MAX_LEN) * 100}%`, background: C.gray }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ============================================================= STAGE 2 */
function parseMut(m) {
  const r = m.match(/^([A-Z])(\d+)([A-Z])$/);
  return r ? { wt: r[1], pos: r[2], mut: r[3] } : { wt: "", pos: m, mut: "" };
}
function StageMutations({ candidates, running, stageStatus }) {
  const muts = useMemo(() => {
    const seen = new Map();
    candidates.forEach((r) => { const k = r.protein + r.mutation; if (!seen.has(k)) seen.set(k, { protein: r.protein, mutation: r.mutation }); });
    return [...seen.values()].sort((a, b) => a.protein.localeCompare(b.protein));
  }, [candidates]);
  const reveal = candidates.length > 0;  // grid is built from candidates; wait until they load
  if (!candidates.length && !running) return <Empty />;
  if (!reveal) return <div className="font-body pulse" style={{ color: C.red }}>Applying mutations…</div>;
  return (
    <div className="grid" style={{ gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
      {muts.map((m, i) => {
        const { wt, mut } = parseMut(m.mutation);
        const tint = PROTEIN_TINT[m.protein] || C.gray;
        return (
          <div key={i} style={{ border: `1px solid ${C.rule}`, borderTop: `2px solid ${tint}`, padding: "14px 16px" }}>
            <div className="font-body" style={{ fontSize: 11, color: tint, fontWeight: 600, letterSpacing: 0.5 }}>{m.protein}</div>
            <div className="font-mono" style={{ fontSize: 22, marginTop: 6, color: C.ink }}>{m.mutation}</div>
            <div className="font-mono" style={{ fontSize: 13, marginTop: 4, color: C.gray }}>
              {wt} <span style={{ color: C.red }}>→</span> <span style={{ color: C.red }}>{mut}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ============================================================= STAGE 3 */
function StageCandidates({ candidates, live, running }) {
  const [w, setW] = useState(0);
  const [playing, setPlaying] = useState(true);
  const windows = KRAS_CONTEXT.length - 8; // number of 9-mer windows = 9
  useEffect(() => {
    if (!playing) return;
    const t = setInterval(() => setW((x) => (x + 1) % windows), 1100);
    return () => clearInterval(t);
  }, [playing, windows]);

  const total = candidates.length;
  const liveCount = live ? live.done : total;

  // histogram: candidates per mutation
  const hist = useMemo(() => {
    const m = new Map();
    candidates.forEach((r) => { const k = r.protein + " " + r.mutation; m.set(k, (m.get(k) || 0) + 1); });
    return [...m.entries()];
  }, [candidates]);
  const maxH = Math.max(1, ...hist.map((h) => h[1]));

  const win = KRAS_CONTEXT.slice(w, w + 9);
  const mutInWin = KRAS_MUT_IDX - w; // index of mutated residue within window

  return (
    <div className="flex flex-col" style={{ gap: 30 }}>
      <div>
        <div className="font-body" style={{ fontSize: 13, color: C.gray, marginBottom: 10 }}>
          Example · KRAS G12V — the 9-residue window slides across the mutation (red).
        </div>
        {/* sequence track */}
        <div className="seq font-mono" style={{ fontSize: 26, letterSpacing: 4, paddingBottom: 8 }}>
          {KRAS_CONTEXT.split("").map((ch, i) => {
            const inWin = i >= w && i < w + 9;
            const isMut = i === KRAS_MUT_IDX;
            return (
              <span key={i} style={{
                color: isMut ? C.red : inWin ? C.ink : "#C8C8C8",
                borderBottom: inWin ? `3px solid ${C.yellow}` : "3px solid transparent",
                fontWeight: isMut ? 600 : 400, padding: "0 1px",
              }}>{ch}</span>
            );
          })}
        </div>
        {/* current 9-mer */}
        <div className="flex items-center" style={{ gap: 18, marginTop: 16 }}>
          <div className="font-mono" style={{ fontSize: 30, letterSpacing: 3, border: `1px solid ${C.rule}`, padding: "8px 14px" }}>
            {win.split("").map((ch, i) => (
              <span key={i} style={{ color: i === mutInWin ? C.red : C.ink, fontWeight: i === mutInWin ? 600 : 400 }}>{ch}</span>
            ))}
          </div>
          <div className="font-body" style={{ fontSize: 13, color: C.gray }}>
            window {w + 1} of {windows}<br />mutation at position {mutInWin + 1}
          </div>
          <div className="flex" style={{ gap: 8 }}>
            <button onClick={() => { setPlaying(false); setW((x) => (x - 1 + windows) % windows); }} style={btn}>‹</button>
            <button onClick={() => setPlaying((p) => !p)} style={btn}>{playing ? "❚❚" : "▶"}</button>
            <button onClick={() => { setPlaying(false); setW((x) => (x + 1) % windows); }} style={btn}>›</button>
          </div>
        </div>
      </div>

      <hr className="rule" />

      <div className="flex" style={{ gap: 40, alignItems: "flex-start" }}>
        <div>
          <div className="font-mono" style={{ fontSize: 13, color: C.gray, textTransform: "uppercase", letterSpacing: 1 }}>candidates generated</div>
          <div className="font-display" style={{ fontSize: 64, color: C.yellow, lineHeight: 1 }}>
            {running && live ? liveCount : total}
            {running && live ? <span style={{ fontSize: 26, color: C.gray }}> / {live.total}</span> : null}
          </div>
        </div>
        <div style={{ flex: 1 }}>
          <div className="font-mono" style={{ fontSize: 12, color: C.gray, marginBottom: 8 }}>candidates per mutation</div>
          <div className="flex" style={{ gap: 3, alignItems: "flex-end", height: 90 }}>
            {hist.map((h, i) => (
              <div key={i} title={`${h[0]}: ${h[1]}`} style={{ flex: 1, height: `${(h[1] / maxH) * 100}%`, background: C.yellow, minWidth: 6 }} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
const btn = { border: `1px solid ${C.rule}`, background: "#fff", padding: "6px 12px", fontSize: 14, color: C.ink };

/* ============================================================= STAGE 4 */
function StageEmbedding({ candidates, running }) {
  if (!candidates.length) return running ? <div className="font-body pulse" style={{ color: C.blue }}>Embedding peptides…</div> : <Empty />;
  const top = candidates[0];
  const pep = top.peptide;
  const vec = embed(pep);
  return (
    <div className="flex flex-col" style={{ gap: 26 }}>
      <div className="font-body" style={{ fontSize: 13, color: C.gray }}>
        Top candidate <span className="font-mono" style={{ color: C.ink }}>{pep}</span> ({top.protein} {top.mutation}) → 47-dimensional vector.
      </div>

      {/* per-residue mini bar charts */}
      <div className="seq" style={{ paddingBottom: 6 }}>
        <div className="flex" style={{ gap: 14 }}>
          {pep.split("").map((ch, i) => (
            <div key={i} className="flex flex-col items-center" style={{ minWidth: 52 }}>
              <div className="flex" style={{ gap: 3, alignItems: "flex-end", height: 60 }}>
                {SCALE_DEFS.map((s, j) => {
                  const rng = SCALE_RANGE[j];
                  const val = s.map[ch] ?? 0;
                  const norm = (val - rng.min) / (rng.max - rng.min || 1);
                  const h = Math.max(4, (isFinite(norm) ? norm : 0) * 100);
                  return <div key={j} title={`${s.name}: ${val}`} style={{ width: 6, height: `${h}%`, background: SCALE_COLORS[j] }} />;
                })}
              </div>
              <div className="font-mono" style={{ fontSize: 22, marginTop: 8 }}>{ch}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex" style={{ gap: 10, fontSize: 11, color: C.gray, flexWrap: "wrap" }}>
        {SCALE_DEFS.map((s, j) => (
          <span key={j} className="font-body" style={{ display: "inline-flex", alignItems: "center", gap: 5 }}>
            <span style={{ width: 9, height: 9, background: SCALE_COLORS[j], display: "inline-block" }} />{s.name}
          </span>
        ))}
      </div>

      <hr className="rule" />

      {/* collapsed 47-cell vector */}
      <div>
        <div className="font-mono" style={{ fontSize: 12, color: C.gray, marginBottom: 8 }}>the 47-dimensional vector (9 residues × 5 scales, then 2 global features)</div>
        <div className="seq">
          <div className="flex" style={{ gap: 2 }}>
            {vec.slice(0, 45).map((v, i) => (
              <div key={i} title={v.toFixed(2)} style={{ width: 14, height: 28, background: valColor(v), border: i % 5 === 0 ? `1px solid #eee` : "none" }} />
            ))}
            <div style={{ width: 14 }} />
            {vec.slice(45).map((v, i) => (
              <div key={i} title={v.toFixed(2)} style={{ width: 14, height: 28, background: valColor(v), outline: `1px solid ${C.green}` }} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ============================================================= STAGE 5 */
function StageVectorDB({ candidates, references, running }) {
  const [fill, setFill] = useState(0);
  const top = candidates[0];
  const sim = top ? top.similarity : 0;
  useEffect(() => { setFill(0); const t = setTimeout(() => setFill(sim), 120); return () => clearTimeout(t); }, [sim]);
  if (!top) return running ? <div className="font-body pulse" style={{ color: C.blue }}>Querying vector database…</div> : <Empty />;

  const q = top.peptide, near = top.nearest_known || "";
  const refPt = references.find((r) => r.peptide === near);

  // scatter scaling
  const pts = [...references.map((r) => ({ ...r, kind: "ref" })),
               ...candidates.map((r) => ({ peptide: r.peptide, pca_x: r.pca_x, pca_y: r.pca_y, composite: r.composite, kind: "cand" }))]
               .filter((p) => p.pca_x != null && p.pca_y != null);
  const hasCoords = pts.length > 0;
  const xs = pts.map((p) => p.pca_x), ys = pts.map((p) => p.pca_y);
  const xmin = Math.min(...xs), xmax = Math.max(...xs), ymin = Math.min(...ys), ymax = Math.max(...ys);
  const W = 360, H = 320, pad = 22;
  const spanX = (isFinite(xmax - xmin) && xmax - xmin) || 1;
  const spanY = (isFinite(ymax - ymin) && ymax - ymin) || 1;
  const sx = (x) => pad + ((x - xmin) / spanX) * (W - 2 * pad);
  const sy = (y) => H - pad - ((y - ymin) / spanY) * (H - 2 * pad);
  const topPt = candidates[0];

  return (
    <div className="flex" style={{ gap: 40, flexWrap: "wrap" }}>
      {/* left: alignment */}
      <div style={{ flex: "1 1 360px" }}>
        <div className="font-mono" style={{ fontSize: 12, color: C.gray, marginBottom: 6 }}>top candidate ({top.protein} {top.mutation})</div>
        <Aligned a={q} b={near} top />
        <div className="font-mono" style={{ fontSize: 12, color: C.gray, margin: "16px 0 6px" }}>
          nearest known epitope · {top.nearest_antigen}
        </div>
        <Aligned a={near} b={q} />
        <div style={{ marginTop: 22 }}>
          <div className="flex" style={{ justifyContent: "space-between", fontSize: 12, color: C.gray }}>
            <span className="font-body">cosine similarity</span>
            <span className="font-mono" style={{ color: C.blue }}>{sim.toFixed(4)}</span>
          </div>
          <div style={{ height: 12, background: "#F0F0F0", marginTop: 6 }}>
            <div style={{ height: "100%", width: `${fill * 100}%`, background: C.blue, transition: "width 1s ease-out" }} />
          </div>
        </div>
      </div>

      {/* right: scatter */}
      <div style={{ flex: "1 1 360px" }}>
        <div className="font-mono" style={{ fontSize: 12, color: C.gray, marginBottom: 6 }}>embedding space (PCA) — blue = known epitopes, yellow = candidates</div>
        {!hasCoords && <div className="font-body" style={{ fontSize: 13, color: C.gray, padding: 20 }}>Embedding map unavailable (no coordinates).</div>}
        {hasCoords && <svg width={W} height={H} style={{ border: `1px solid ${C.rule}` }}>
          {refPt && topPt && (
            <line x1={sx(topPt.pca_x)} y1={sy(topPt.pca_y)} x2={sx(refPt.pca_x)} y2={sy(refPt.pca_y)}
                  stroke={C.blue} strokeWidth="1" strokeDasharray="3 3" />
          )}
          {pts.filter((p) => p.kind === "cand").map((p, i) => (
            <circle key={"c" + i} cx={sx(p.pca_x)} cy={sy(p.pca_y)} r={2 + (p.composite || 0.4) * 5}
                    fill={C.yellow} fillOpacity="0.7" stroke="#fff" strokeWidth="0.4">
              <title>{p.peptide} · {(p.composite || 0).toFixed(3)}</title>
            </circle>
          ))}
          {pts.filter((p) => p.kind === "ref").map((p, i) => (
            <circle key={"r" + i} cx={sx(p.pca_x)} cy={sy(p.pca_y)} r="4" fill={C.blue}>
              <title>{p.peptide} · {p.antigen}</title>
            </circle>
          ))}
          {topPt && topPt.pca_x != null && (
            <circle cx={sx(topPt.pca_x)} cy={sy(topPt.pca_y)} r="9" fill="none" stroke={C.green} strokeWidth="2" className="pulse" />
          )}
        </svg>}
      </div>
    </div>
  );
}
function Aligned({ a, b, top }) {
  return (
    <div className="seq font-mono" style={{ fontSize: 30, letterSpacing: 4 }}>
      {a.split("").map((ch, i) => {
        const match = b && b[i] === ch;
        return <span key={i} style={{ color: top ? (match ? C.blue : C.ink) : (match ? C.blue : C.gray) }}>{ch}</span>;
      })}
    </div>
  );
}

/* ============================================================= STAGE 6 */
function StageScoring({ candidates, construct, running, selected, setSelected }) {
  const [sortKey, setSortKey] = useState("composite");
  const [dir, setDir] = useState("desc");
  const parsed = useMemo(() => parseConstruct(construct), [construct]);
  const constructSet = useMemo(() => new Set(parsed.epitopes), [parsed]);

  const rows = useMemo(() => {
    const r = [...candidates];
    r.sort((a, b) => {
      const va = a[sortKey], vb = b[sortKey];
      const c = typeof va === "number" ? va - vb : String(va).localeCompare(String(vb));
      return dir === "asc" ? c : -c;
    });
    return r;
  }, [candidates, sortKey, dir]);

  if (!candidates.length) return running ? <div className="font-body pulse" style={{ color: C.green }}>Scoring candidates…</div> : <Empty />;
  const head = (k, lbl) => (
    <th onClick={() => { setSortKey(k); setDir(sortKey === k && dir === "desc" ? "asc" : "desc"); }}
        className="font-body" style={{ textAlign: k === "peptide" || k === "protein" || k === "mutation" ? "left" : "right", padding: "6px 10px", cursor: "pointer", color: C.gray, fontSize: 11, textTransform: "uppercase", letterSpacing: 0.5, borderBottom: `1px solid ${C.rule}`, userSelect: "none" }}>
      {lbl}{sortKey === k ? (dir === "desc" ? " ↓" : " ↑") : ""}
    </th>
  );

  return (
    <div className="flex flex-col" style={{ gap: 24 }}>
      {/* table */}
      <div style={{ maxHeight: 300, overflowY: "auto", border: `1px solid ${C.rule}` }}>
        <table style={{ width: "100%", fontSize: 13 }}>
          <thead style={{ position: "sticky", top: 0, background: "#fff" }}>
            <tr>{head("protein", "Protein")}{head("mutation", "Mutation")}{head("peptide", "Peptide")}{head("binding", "Binding")}{head("similarity", "Similarity")}{head("composite", "Composite")}</tr>
          </thead>
          <tbody>
            {rows.map((r, i) => {
              const inC = constructSet.has(r.peptide);
              const sel = selected === r.peptide;
              return (
                <tr key={i} onClick={() => inC && setSelected(sel ? null : r.peptide)}
                    style={{ background: sel ? "#EAF5EE" : inC ? "#F4FBF6" : "transparent", cursor: inC ? "pointer" : "default", borderLeft: inC ? `3px solid ${C.green}` : "3px solid transparent" }}>
                  <td className="font-body" style={{ padding: "5px 10px" }}>{r.protein}</td>
                  <td className="font-mono" style={{ padding: "5px 10px" }}>{r.mutation}</td>
                  <td className="font-mono" style={{ padding: "5px 10px", color: inC ? C.green : C.ink }}>{r.peptide}</td>
                  <td className="font-mono" style={{ padding: "5px 10px", textAlign: "right" }}>{(+r.binding).toFixed(3)}</td>
                  <td className="font-mono" style={{ padding: "5px 10px", textAlign: "right" }}>{(+r.similarity).toFixed(3)}</td>
                  <td className="font-mono" style={{ padding: "5px 10px", textAlign: "right", color: C.green, fontWeight: 500 }}>{(+r.composite).toFixed(3)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* construct */}
      <div>
        <div className="flex items-baseline" style={{ gap: 14, marginBottom: 10 }}>
          <div className="font-mono" style={{ fontSize: 12, color: C.gray, textTransform: "uppercase", letterSpacing: 1 }}>final vaccine construct</div>
          <div className="font-mono" style={{ fontSize: 13, color: C.green }}>{parsed.length} aa · {parsed.epitopes.length} epitopes</div>
        </div>
        <div className="seq" style={{ paddingBottom: 8 }}>
          <div className="flex items-center" style={{ gap: 0 }}>
            {parsed.epitopes.map((ep, i) => (
              <React.Fragment key={i}>
                <span onClick={() => setSelected(selected === ep ? null : ep)} className="font-mono"
                      style={{ fontSize: 26, letterSpacing: 2, padding: "6px 10px", cursor: "pointer",
                               color: selected === ep ? "#fff" : C.green,
                               background: selected === ep ? C.green : "#F4FBF6",
                               border: `1px solid ${selected === ep ? C.green : "#D7EADD"}` }}>{ep}</span>
                {i < parsed.epitopes.length - 1 && (
                  <span className="font-mono" style={{ fontSize: 12, color: "#BBB", padding: "0 6px" }}>AAY</span>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
        <div className="font-body" style={{ fontSize: 12, color: C.gray, marginTop: 8 }}>
          Click an epitope or a highlighted table row to link them. EGFR and HER2 epitopes echo the Yale canine vaccine's targets.
        </div>
      </div>
    </div>
  );
}

/* ============================================================ Narration */
function Narration({ stageKey }) {
  return (
    <div style={{ borderTop: `1px solid ${C.rule}`, padding: "16px 48px" }}>
      <div className="font-body" style={{ fontSize: 15, color: "#444", maxWidth: 680, margin: "0 auto", lineHeight: 1.55, textAlign: "center" }}>
        {NARRATION[stageKey]}
      </div>
    </div>
  );
}

/* ============================================================== BottomBar */
function BottomBar({ running, onRun, lastRun, log }) {
  const [showLog, setShowLog] = useState(false);
  return (
    <div>
      {showLog && (
        <div className="font-mono" style={{ background: "#0F1115", color: "#C8E6C9", fontSize: 11.5, padding: "10px 16px", maxHeight: 130, overflowY: "auto", borderTop: `1px solid #222` }}>
          {log.length ? log.map((l, i) => <div key={i}>{l}</div>) : <div style={{ color: "#666" }}>pipeline stdout will appear here…</div>}
        </div>
      )}
      <div className="flex items-center" style={{ borderTop: `1px solid ${C.rule}`, padding: "12px 24px", gap: 16 }}>
        <button onClick={onRun} disabled={running}
                style={{ background: running ? "#999" : C.green, color: "#fff", border: "none", padding: "10px 22px", fontSize: 14, fontWeight: 600, letterSpacing: 0.5 }}>
          {running ? "Running…" : "▶  Run Pipeline"}
        </button>
        <div className="font-body" style={{ fontSize: 12, color: C.gray }}>
          {lastRun ? `Last run: ${new Date(lastRun).toLocaleString()}` : "No results yet"}
        </div>
        <div style={{ flex: 1 }} />
        <button onClick={() => setShowLog((s) => !s)} className="font-mono" style={{ background: "none", border: `1px solid ${C.rule}`, padding: "6px 12px", fontSize: 12, color: C.gray }}>
          {showLog ? "hide log" : "show log"}
        </button>
      </div>
    </div>
  );
}

/* ================================================================== APP */
function App() {
  const [candidates, setCandidates] = useState([]);
  const [references, setReferences] = useState([]);
  const [construct, setConstruct] = useState("");
  const [lastRun, setLastRun] = useState(null);
  const [active, setActive] = useState(0);
  const [running, setRunning] = useState(false);
  const [stageStatus, setStageStatus] = useState({});
  const [live, setLive] = useState(null);
  const [revealed, setRevealed] = useState(new Set());
  const [log, setLog] = useState([]);
  const [selected, setSelected] = useState(null);
  const activeRef = useRef(0);
  const runFailedRef = useRef(false);

  const allComplete = () => { const s = {}; STAGES.forEach((x) => (s[x.key] = "complete")); return s; };

  async function loadData() {
    const [c, r, t, st] = await Promise.all([
      getJSON("/data/candidates", []),
      getJSON("/data/references", []),
      getText("/data/construct", ""),
      getJSON("/data/status", { has_results: false, last_run: null }),
    ]);
    setCandidates(c); setReferences(r); setConstruct(t);
    setLastRun(st.last_run);
    return st;
  }
  useEffect(() => { (async () => { const st = await loadData(); if (st.has_results) setStageStatus(allComplete()); })(); }, []);

  function handleLine(line) {
    if (line.startsWith("STAGE:")) {
      const parts = line.slice(6).split(":");   // strip "STAGE:"
      const key = parts[0], ev = parts[1];
      if (key === "done") {                       // terminal sentinel: STAGE:done:<rc>
        if (+ev !== 0) {
          runFailedRef.current = true;
          setStageStatus((s) => { const k = Object.keys(s).find((x) => s[x] === "running"); return k ? { ...s, [k]: "error" } : s; });
        }
        return;
      }
      const skey = key === "construct" ? "scoring" : key;  // construct event drives Stage 6
      if (ev === "start") {
        setStageStatus((s) => ({ ...s, [skey]: "running" }));
        const idx = STAGES.findIndex((x) => x.key === skey);
        if (idx >= 0) { setActive(idx); activeRef.current = idx; }
      } else if (ev === "complete") {
        setStageStatus((s) => ({ ...s, [skey]: "complete" }));
        if (key === "candidates") setLive({ done: +parts[2], total: +parts[2] });
      } else if (ev === "progress") {
        if (key === "candidates") setLive({ done: +parts[2], total: +parts[3] });
      }
    } else {
      setLog((l) => [...l, line].slice(-300));
      const m = line.match(/^loaded ([A-Z0-9]+) \(\d+ aa\)/);  // protein-load lines only
      if (m) setRevealed((s) => new Set(s).add(m[1]));
    }
  }

  async function onRun() {
    setRunning(true);
    runFailedRef.current = false;
    setLog([]); setLive(null); setRevealed(new Set());
    setCandidates([]); setReferences([]); setConstruct("");   // clear stale data so stages show live state
    setStageStatus(Object.fromEntries(STAGES.map((x) => [x.key, "idle"])));
    setActive(0); activeRef.current = 0;
    let ok = true;
    try {
      const resp = await fetch("/pipeline/run", { method: "POST" });
      if (!resp.body) throw new Error("no stream");
      const reader = resp.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let idx;
        while ((idx = buf.indexOf("\n\n")) >= 0) {
          const frame = buf.slice(0, idx); buf = buf.slice(idx + 2);
          const line = frame.replace(/^data: ?/, "");
          if (line) handleLine(line);
        }
      }
    } catch (e) {
      ok = false;
      setLog((l) => [...l, "stream error: " + e.message + " (is the server running?)"]);
      setStageStatus((s) => ({ ...s, [STAGES[activeRef.current].key]: "error" }));
    }
    await loadData();
    if (ok && !runFailedRef.current) setStageStatus(allComplete());  // only on a clean run
    setRunning(false);
  }

  const counts = {
    proteins: 4,
    mutations: new Set(candidates.map((r) => r.protein + r.mutation)).size || null,
    candidates: candidates.length || (live ? live.total : null),
    embedding: candidates.length || null,
    vectordb: references.length || null,
    scoring: parseConstruct(construct).epitopes.length || null,
  };

  const stage = STAGES[active];
  const view = () => {
    switch (stage.key) {
      case "proteins":   return <StageProteins candidates={candidates} revealed={revealed} running={running} />;
      case "mutations":  return <StageMutations candidates={candidates} running={running} stageStatus={stageStatus} />;
      case "candidates": return <StageCandidates candidates={candidates} live={live} running={running} />;
      case "embedding":  return <StageEmbedding candidates={candidates} running={running} />;
      case "vectordb":   return <StageVectorDB candidates={candidates} references={references} running={running} />;
      case "scoring":    return <StageScoring candidates={candidates} construct={construct} running={running} selected={selected} setSelected={setSelected} />;
      default: return null;
    }
  };

  return (
    <div className="flex" style={{ height: "100vh", minWidth: 1080 }}>
      <Sidebar stageStatus={stageStatus} active={active} onPick={setActive} counts={counts} running={running} />
      <div className="flex flex-col" style={{ flex: 1, minWidth: 0 }}>
        <div className="flex flex-col" style={{ flex: 1, minHeight: 0 }}>
          <StageShell stage={stage}>{view()}</StageShell>
          <Narration stageKey={stage.key} />
        </div>
        <BottomBar running={running} onRun={onRun} lastRun={lastRun} log={log} />
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
