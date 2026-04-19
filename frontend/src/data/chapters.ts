export type ChapterKind = "rich" | "pdf" | "mixed" | "download" | "pptx";

export type RichBlock =
  | { type: "h2"; text: string }
  | { type: "h3"; text: string }
  | { type: "p"; text: string }
  | { type: "definition"; term: string; body: string }
  | { type: "example"; title: string; body: string }
  | { type: "callout"; tone: "info" | "warn" | "tip"; body: string };

export type Chapter = {
  id: string;
  name: string;
  pages: number;
  kind: ChapterKind;
  pdfUrl?: string;
  /** In-browser PPTX preview URL (same-origin API or public URL) */
  pptxUrl?: string;
  blocks?: RichBlock[];
  /** Filename in the RAG `data/` folder — used for chat `allowed_sources` + download links */
  sourceFilename?: string;
};

export type Material = { id: string; name: string; chapters: Chapter[] };

// A small public sample PDF (Mozilla pdf.js test file, CORS-friendly)
const SAMPLE_PDF = "https://raw.githubusercontent.com/mozilla/pdf.js/ba2edeae/web/compressed.tracemonkey-pldi-09.pdf";

export const materials: Material[] = [
  {
    id: "linalg",
    name: "Linear Algebra",
    chapters: [
      {
        id: "la-1",
        name: "Ch. 1 — Vectors & Spaces",
        pages: 12,
        kind: "rich",
        blocks: [
          { type: "h2", text: "1. Vectors & Vector Spaces" },
          {
            type: "p",
            text: "A vector is an ordered tuple of numbers that represents both magnitude and direction. In linear algebra, vectors live inside vector spaces — sets where addition and scalar multiplication behave predictably.",
          },
          {
            type: "definition",
            term: "Vector space",
            body: "A set V over a field F equipped with addition and scalar multiplication satisfying the eight vector-space axioms (associativity, identity, inverses, distributivity, …).",
          },
          { type: "h3", text: "1.1 Linear combinations" },
          {
            type: "p",
            text: "Given vectors v₁, …, vₙ and scalars a₁, …, aₙ, the expression a₁v₁ + … + aₙvₙ is called a linear combination. The set of all such combinations is the span.",
          },
          {
            type: "example",
            title: "Worked example",
            body: "Take v₁ = (1, 0) and v₂ = (0, 1). Any (x, y) in ℝ² equals x·v₁ + y·v₂, so {v₁, v₂} spans ℝ².",
          },
          {
            type: "callout",
            tone: "tip",
            body: "Tip: if you can write any vector as a unique combination of a set, that set is a basis.",
          },
        ],
      },
      {
        id: "la-2",
        name: "Ch. 2 — Linear Maps",
        pages: 18,
        kind: "pdf",
        pdfUrl: SAMPLE_PDF,
      },
      {
        id: "la-3",
        name: "Ch. 3 — Eigenvectors",
        pages: 14,
        kind: "mixed",
        pdfUrl: SAMPLE_PDF,
        blocks: [
          { type: "h2", text: "3. Eigenvectors & Eigenvalues" },
          {
            type: "p",
            text: "Given a square matrix A, a non-zero vector v is an eigenvector of A if Av = λv for some scalar λ — the corresponding eigenvalue. Geometrically, eigenvectors are the directions a linear map only stretches, never rotates.",
          },
          {
            type: "definition",
            term: "Characteristic polynomial",
            body: "det(A − λI) = 0. Its roots are the eigenvalues of A.",
          },
          {
            type: "example",
            title: "Worked example",
            body: "For A = [[2,1],[0,3]], det(A − λI) = (2 − λ)(3 − λ), so λ ∈ {2, 3}.",
          },
          {
            type: "callout",
            tone: "info",
            body: "Eigen-decomposition powers PCA, PageRank, and quantum mechanics.",
          },
        ],
      },
      {
        id: "la-4",
        name: "Ch. 4 — Diagonalization",
        pages: 9,
        kind: "rich",
        blocks: [
          { type: "h2", text: "4. Diagonalization" },
          {
            type: "p",
            text: "A matrix A is diagonalizable if it has a basis of eigenvectors. Then A = PDP⁻¹ where D is diagonal with eigenvalues, and P holds eigenvectors as columns.",
          },
          {
            type: "callout",
            tone: "warn",
            body: "Not every matrix is diagonalizable — a defective matrix lacks a full eigenbasis.",
          },
        ],
      },
    ],
  },
  {
    id: "ml",
    name: "Machine Learning",
    chapters: [
      {
        id: "ml-1",
        name: "Ch. 1 — Intro & Setup",
        pages: 10,
        kind: "rich",
        blocks: [
          { type: "h2", text: "1. What is Machine Learning?" },
          {
            type: "p",
            text: "Machine learning is the study of algorithms that improve through experience. Instead of writing rules, we let data shape the model.",
          },
          {
            type: "definition",
            term: "Supervised learning",
            body: "Learning a function f : X → Y from labeled examples (xᵢ, yᵢ).",
          },
          {
            type: "callout",
            tone: "tip",
            body: "Start with a baseline (e.g. mean predictor) before reaching for deep models.",
          },
        ],
      },
      {
        id: "ml-2",
        name: "Ch. 2 — Linear Regression",
        pages: 22,
        kind: "pdf",
        pdfUrl: SAMPLE_PDF,
      },
      {
        id: "ml-3",
        name: "Ch. 3 — Neural Networks",
        pages: 28,
        kind: "mixed",
        pdfUrl: SAMPLE_PDF,
        blocks: [
          { type: "h2", text: "3. Neural Networks" },
          {
            type: "p",
            text: "A neural network composes simple non-linear units (neurons) into layers. Each neuron computes σ(Wx + b).",
          },
          {
            type: "example",
            title: "Why depth helps",
            body: "Shallow networks need exponentially many neurons to express functions that a deep network can express compactly.",
          },
        ],
      },
    ],
  },
  {
    id: "physics",
    name: "Thermodynamics",
    chapters: [
      {
        id: "ph-1",
        name: "Ch. 1 — Heat & Temperature",
        pages: 15,
        kind: "rich",
        blocks: [
          { type: "h2", text: "1. Heat vs Temperature" },
          {
            type: "p",
            text: "Temperature measures the average kinetic energy of particles; heat is the total energy transferred between systems at different temperatures.",
          },
          {
            type: "definition",
            term: "Thermal equilibrium",
            body: "Two systems are in thermal equilibrium when no net heat flows between them.",
          },
        ],
      },
      {
        id: "ph-2",
        name: "Ch. 2 — Laws of Thermo",
        pages: 20,
        kind: "pdf",
        pdfUrl: SAMPLE_PDF,
      },
    ],
  },
];
