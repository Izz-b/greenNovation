import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { useState } from "react";
import {
  FileText,
  Highlighter,
  Sparkles,
  ListChecks,
  MessageCircleQuestion,
  Send,
  X,
  BookOpen,
  Upload,
  PanelRightOpen,
  ChevronDown,
  ChevronRight,
  FolderOpen,
  Folder,
} from "lucide-react";

export const Route = createFileRoute("/workspace")({
  head: () => ({
    meta: [
      { title: "Course Workspace — EcoLearn AI" },
      {
        name: "description",
        content:
          "Study your own materials with AI-generated summaries, quizzes and grounded answers.",
      },
      { property: "og:title", content: "Course Workspace — EcoLearn AI" },
      {
        property: "og:description",
        content: "A smart document studio, not a chatbot.",
      },
    ],
  }),
  component: () => (
    <AppLayout>
      <WorkspacePage />
    </AppLayout>
  ),
});

type Chapter = { id: string; name: string; pages: number };
type Material = { id: string; name: string; chapters: Chapter[] };

const materials: Material[] = [
  {
    id: "linalg",
    name: "Linear Algebra",
    chapters: [
      { id: "la-1", name: "Ch. 1 — Vectors & Spaces.pdf", pages: 12 },
      { id: "la-2", name: "Ch. 2 — Linear Maps.pdf", pages: 18 },
      { id: "la-3", name: "Ch. 3 — Eigenvectors.pdf", pages: 14 },
      { id: "la-4", name: "Ch. 4 — Diagonalization.pdf", pages: 9 },
    ],
  },
  {
    id: "ml",
    name: "Machine Learning",
    chapters: [
      { id: "ml-1", name: "Ch. 1 — Intro & Setup.pdf", pages: 10 },
      { id: "ml-2", name: "Ch. 2 — Linear Regression.pdf", pages: 22 },
      { id: "ml-3", name: "Ch. 3 — Neural Networks.pdf", pages: 28 },
    ],
  },
  {
    id: "physics",
    name: "Thermodynamics",
    chapters: [
      { id: "ph-1", name: "Ch. 1 — Heat & Temperature.pdf", pages: 15 },
      { id: "ph-2", name: "Ch. 2 — Laws of Thermo.pdf", pages: 20 },
    ],
  },
];

function WorkspacePage() {
  const [panelOpen, setPanelOpen] = useState(false);
  const [tab, setTab] = useState<"summary" | "quiz" | "explain">("summary");
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    linalg: true,
    ml: false,
    physics: false,
  });
  const [activeChapter, setActiveChapter] = useState<string>("la-3");

  const toggle = (id: string) => setExpanded((e) => ({ ...e, [id]: !e[id] }));

  const currentChapter = materials
    .flatMap((m) => m.chapters.map((c) => ({ ...c, material: m.name })))
    .find((c) => c.id === activeChapter);

  return (
    <div className="max-w-[1400px] mx-auto">
      <div className="flex items-center justify-between mb-5">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-primary font-semibold mb-1">
            Workspace
          </div>
          <h1 className="font-display text-2xl lg:text-3xl font-bold">
            {currentChapter ? `${currentChapter.material} · ${currentChapter.name.replace(".pdf", "")}` : "Workspace"}
          </h1>
        </div>
        <button
          onClick={() => setPanelOpen(true)}
          className="inline-flex items-center gap-2 rounded-xl bg-card border border-border px-3.5 py-2 text-sm font-semibold hover:bg-muted transition shadow-card"
        >
          <PanelRightOpen className="h-4 w-4" />
          Ask Bamboo
        </button>
      </div>

      <div className="grid grid-cols-12 gap-5">
        {/* Materials with expandable chapters */}
        <aside className="col-span-12 lg:col-span-3 rounded-3xl bg-card border border-border p-4 shadow-card h-fit">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-sm">Materials</h3>
            <button className="text-xs font-semibold text-primary inline-flex items-center gap-1 hover:underline">
              <Upload className="h-3.5 w-3.5" /> Upload
            </button>
          </div>
          <ul className="space-y-1">
            {materials.map((m) => {
              const open = expanded[m.id];
              return (
                <li key={m.id}>
                  <button
                    onClick={() => toggle(m.id)}
                    className="w-full flex items-center gap-2 rounded-xl px-2.5 py-2 hover:bg-muted transition text-left"
                  >
                    {open ? (
                      <ChevronDown className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    ) : (
                      <ChevronRight className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    )}
                    {open ? (
                      <FolderOpen className="h-4 w-4 text-primary shrink-0" />
                    ) : (
                      <Folder className="h-4 w-4 text-primary shrink-0" />
                    )}
                    <span className="text-sm font-semibold truncate">{m.name}</span>
                    <span className="ml-auto text-[10px] text-muted-foreground font-medium">
                      {m.chapters.length}
                    </span>
                  </button>
                  {open && (
                    <ul className="ml-4 mt-1 mb-2 space-y-0.5 border-l border-border pl-2">
                      {m.chapters.map((c) => {
                        const active = activeChapter === c.id;
                        return (
                          <li key={c.id}>
                            <button
                              onClick={() => setActiveChapter(c.id)}
                              className={`w-full text-left rounded-lg px-2.5 py-2 flex items-start gap-2 transition ${
                                active
                                  ? "bg-primary/10 border border-primary/30"
                                  : "hover:bg-muted border border-transparent"
                              }`}
                            >
                              <FileText
                                className={`h-3.5 w-3.5 mt-0.5 shrink-0 ${
                                  active ? "text-primary" : "text-muted-foreground"
                                }`}
                              />
                              <div className="min-w-0">
                                <div className="text-xs font-medium truncate">{c.name}</div>
                                <div className="text-[10px] text-muted-foreground">{c.pages} pages</div>
                              </div>
                            </button>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </li>
              );
            })}
          </ul>
        </aside>

        {/* Document reader */}
        <section className="col-span-12 lg:col-span-6 rounded-3xl bg-card border border-border p-6 lg:p-8 shadow-card">
          <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
            <span className="inline-flex items-center gap-1.5">
              <BookOpen className="h-3.5 w-3.5" /> Page 4 of {currentChapter?.pages ?? 14}
            </span>
            <button className="inline-flex items-center gap-1 rounded-lg bg-warning/15 text-warning-foreground px-2.5 py-1 font-semibold">
              <Highlighter className="h-3 w-3" /> Highlight
            </button>
          </div>
          <article className="prose prose-sm max-w-none">
            <h2 className="font-display text-2xl font-bold mb-3">3.2 — Eigenvectors</h2>
            <p className="text-foreground/90 leading-relaxed">
              Given a square matrix <em>A</em>, a non-zero vector <em>v</em> is an{" "}
              <span className="bg-warning/30 px-1 rounded">eigenvector</span> of <em>A</em> if{" "}
              <em>Av = λv</em> for some scalar <em>λ</em>, called the corresponding eigenvalue.
              Geometrically, eigenvectors are the directions that the linear map only stretches —
              never rotates.
            </p>
            <p className="text-foreground/80 leading-relaxed mt-4">
              The set of eigenvalues forms the spectrum of <em>A</em>. To find them we solve{" "}
              <em>det(A − λI) = 0</em>, the characteristic polynomial. Each root gives an
              eigenvalue, and the corresponding null space yields the eigenvectors.
            </p>
            <div className="mt-5 rounded-2xl bg-muted/60 p-4 border border-border">
              <div className="text-[10px] uppercase tracking-widest font-bold text-muted-foreground mb-1">
                Worked example
              </div>
              <p className="text-sm">
                For <em>A = [[2,1],[0,3]]</em>, det(A−λI) = (2−λ)(3−λ) so λ ∈ &#123;2, 3&#125;.
              </p>
            </div>
          </article>
        </section>

        {/* AI tools */}
        <aside className="col-span-12 lg:col-span-3 space-y-4">
          <div className="rounded-3xl bg-card border border-border shadow-card overflow-hidden">
            <div className="flex p-1 bg-muted/60">
              {(
                [
                  { id: "summary", label: "Summary", icon: Sparkles },
                  { id: "quiz", label: "Quiz", icon: ListChecks },
                  { id: "explain", label: "Explain", icon: MessageCircleQuestion },
                ] as const
              ).map((t) => (
                <button
                  key={t.id}
                  onClick={() => setTab(t.id)}
                  className={`flex-1 inline-flex items-center justify-center gap-1.5 rounded-xl px-2 py-2 text-xs font-semibold transition ${
                    tab === t.id
                      ? "bg-card shadow-card text-foreground"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <t.icon className="h-3.5 w-3.5" />
                  {t.label}
                </button>
              ))}
            </div>
            <div className="p-5">
              {tab === "summary" && (
                <ul className="space-y-3 text-sm">
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">·</span>
                    Eigenvectors are directions preserved by a linear map (only scaled).
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">·</span>
                    Eigenvalues come from solving the characteristic polynomial.
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">·</span>
                    Diagonalizable matrices have a full basis of eigenvectors.
                  </li>
                </ul>
              )}
              {tab === "quiz" && (
                <div className="space-y-3 text-sm">
                  <div className="font-semibold">Q1. If Av = 5v, then 5 is the …</div>
                  {["eigenvector", "eigenvalue", "determinant"].map((o) => (
                    <button
                      key={o}
                      className="w-full text-left rounded-xl border border-border px-3 py-2 hover:border-primary/50 hover:bg-primary/5 transition"
                    >
                      {o}
                    </button>
                  ))}
                </div>
              )}
              {tab === "explain" && (
                <p className="text-sm leading-relaxed">
                  Think of a globe spinning. The axis that doesn't move is an eigenvector — every
                  other point rotates, but those on the axis only get stretched (or stay still).
                </p>
              )}
            </div>
          </div>

          <div className="rounded-3xl gradient-warm p-5 shadow-card">
            <div className="text-xs font-bold uppercase tracking-wider text-accent-foreground mb-1">
              Suggested study plan
            </div>
            <p className="text-sm font-medium">
              25 min reading → 10 min quiz → 5 min recap. Repeat tomorrow.
            </p>
          </div>
        </aside>
      </div>

      {/* Slide-in assistant */}
      {panelOpen && (
        <>
          <div
            className="fixed inset-0 z-40 bg-foreground/20 backdrop-blur-sm"
            onClick={() => setPanelOpen(false)}
          />
          <aside className="fixed top-0 right-0 z-50 h-screen w-full sm:w-[420px] bg-card border-l border-border shadow-glow flex flex-col animate-[slide-in-right_0.3s_ease-out]">
            <div className="flex items-center justify-between p-4 border-b border-border">
              <div>
                <div className="text-xs uppercase tracking-widest text-primary font-bold">
                  Bamboo · grounded in your docs
                </div>
                <div className="font-display font-bold">Ask anything</div>
              </div>
              <button
                onClick={() => setPanelOpen(false)}
                className="rounded-lg p-2 hover:bg-muted"
                aria-label="Close"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              <div className="rounded-2xl bg-muted/60 p-3 text-sm">
                Hi! I can answer using <strong>{currentChapter?.name ?? "your chapter"}</strong> and your notes. Try “Why does
                A−λI need to be singular?”
              </div>
            </div>
            <div className="p-4 border-t border-border">
              <div className="flex items-center gap-2 rounded-2xl border border-border bg-background p-2">
                <input
                  className="flex-1 bg-transparent px-2 py-1.5 text-sm focus:outline-none"
                  placeholder="Ask about this material..."
                />
                <button className="h-9 w-9 rounded-xl gradient-primary grid place-items-center text-primary-foreground">
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
          </aside>
        </>
      )}
    </div>
  );
}
