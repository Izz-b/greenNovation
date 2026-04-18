import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { PageHeader } from "@/components/PageHeader";
import { AvatarTip } from "@/components/AvatarTip";
import { useState } from "react";
import { Trees, Flame, Leaf, Award, Sprout, Sparkles } from "lucide-react";
import treeOak from "@/assets/tree-oak.png";
import treePine from "@/assets/tree-pine.png";
import treeBlossom from "@/assets/tree-blossom.png";

export const Route = createFileRoute("/forest")({
  head: () => ({
    meta: [
      { title: "Eco Forest — EcoLearn AI" },
      {
        name: "description",
        content: "Grow a virtual forest by studying consistently — every session waters a tree.",
      },
      { property: "og:title", content: "Eco Forest — EcoLearn AI" },
      {
        property: "og:description",
        content: "Gamified, sustainable, and a little bit magical.",
      },
    ],
  }),
  component: () => (
    <AppLayout>
      <ForestPage />
    </AppLayout>
  ),
});

type TreeKind = "oak" | "pine" | "blossom";
type Tree = {
  id: number;
  kind: TreeKind;
  // percentages within the forest scene (0-100)
  x: number;
  y: number;
  scale: number;
  fresh?: boolean;
};

const TREE_IMG: Record<TreeKind, string> = {
  oak: treeOak,
  pine: treePine,
  blossom: treeBlossom,
};

// Pre-planted trees scattered to look like a real forest (back → front).
const INITIAL_TREES: Tree[] = [
  // back row (small, hazy)
  { id: 1, kind: "pine", x: 8, y: 22, scale: 0.55 },
  { id: 2, kind: "oak", x: 22, y: 18, scale: 0.6 },
  { id: 3, kind: "pine", x: 38, y: 20, scale: 0.55 },
  { id: 4, kind: "blossom", x: 54, y: 19, scale: 0.6 },
  { id: 5, kind: "pine", x: 72, y: 21, scale: 0.58 },
  { id: 6, kind: "oak", x: 88, y: 23, scale: 0.55 },
  // mid row
  { id: 7, kind: "oak", x: 14, y: 45, scale: 0.78 },
  { id: 8, kind: "blossom", x: 32, y: 42, scale: 0.82 },
  { id: 9, kind: "pine", x: 50, y: 46, scale: 0.85 },
  { id: 10, kind: "oak", x: 70, y: 44, scale: 0.78 },
  { id: 11, kind: "pine", x: 86, y: 47, scale: 0.8 },
  // front row (large)
  { id: 12, kind: "blossom", x: 20, y: 74, scale: 1.05 },
  { id: 13, kind: "oak", x: 46, y: 78, scale: 1.15 },
  { id: 14, kind: "pine", x: 76, y: 75, scale: 1.1 },
];

function ForestPage() {
  const [trees, setTrees] = useState<Tree[]>(INITIAL_TREES);
  const [planting, setPlanting] = useState(false);

  const stats = [
    { icon: Trees, label: "Trees grown", value: String(trees.length), color: "bg-primary/10 text-primary" },
    { icon: Flame, label: "Streak", value: "4 days", color: "bg-warning/15 text-warning-foreground" },
    { icon: Leaf, label: "CO₂ saved (sim.)", value: `${(trees.length * 0.2).toFixed(1)} kg`, color: "bg-success/10 text-success" },
    { icon: Award, label: "Level", value: "Sprout · 3", color: "bg-info/10 text-info" },
  ];

  const plantTree = () => {
    if (planting) return;
    setPlanting(true);
    const kinds: TreeKind[] = ["oak", "pine", "blossom"];
    const kind = kinds[Math.floor(Math.random() * kinds.length)];
    // pick a free-ish spot in the front/mid area
    const x = 8 + Math.random() * 84;
    const y = 55 + Math.random() * 30;
    const scale = 0.85 + Math.random() * 0.35;
    const newTree: Tree = {
      id: Date.now(),
      kind,
      x,
      y,
      scale,
      fresh: true,
    };
    setTrees((t) => [...t, newTree]);
    setTimeout(() => {
      setTrees((t) => t.map((tr) => (tr.id === newTree.id ? { ...tr, fresh: false } : tr)));
      setPlanting(false);
    }, 1000);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <PageHeader
        eyebrow="Eco Forest"
        title="Your forest is thriving 🌳"
        description="Every focused session waters a tree. Inactivity won't hurt — they just nap."
        actions={
          <button
            onClick={plantTree}
            disabled={planting}
            className="inline-flex items-center gap-2 rounded-xl gradient-primary text-primary-foreground px-4 py-2.5 text-sm font-semibold shadow-glow hover:opacity-95 transition disabled:opacity-60"
          >
            <Sprout className="h-4 w-4" />
            {planting ? "Planting…" : "Plant a tree"}
          </button>
        }
      />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {stats.map((s) => (
          <div key={s.label} className="rounded-2xl bg-card border border-border p-4 shadow-card">
            <div className={`h-10 w-10 rounded-xl grid place-items-center ${s.color}`}>
              <s.icon className="h-5 w-5" />
            </div>
            <div className="mt-3 font-display text-2xl font-bold">{s.value}</div>
            <div className="text-xs text-muted-foreground">{s.label}</div>
          </div>
        ))}
      </div>

      {/* The forest scene */}
      <section className="rounded-3xl shadow-card relative overflow-hidden border border-primary/10">
        {/* Sky → ground gradient */}
        <div
          className="relative w-full"
          style={{
            height: "min(620px, 75vh)",
            background:
              "linear-gradient(to bottom, oklch(0.92 0.06 230) 0%, oklch(0.95 0.05 200) 35%, oklch(0.88 0.10 145) 55%, oklch(0.78 0.13 140) 80%, oklch(0.70 0.14 145) 100%)",
          }}
        >
          {/* Sun */}
          <div
            className="absolute h-20 w-20 rounded-full"
            style={{
              top: "8%",
              right: "10%",
              background:
                "radial-gradient(circle, oklch(0.95 0.14 90) 0%, oklch(0.92 0.12 80 / 0.4) 60%, transparent 100%)",
              filter: "blur(2px)",
            }}
          />
          {/* Distant mountains */}
          <svg
            className="absolute inset-x-0 top-[18%] w-full"
            viewBox="0 0 1000 120"
            preserveAspectRatio="none"
            style={{ height: "12%" }}
          >
            <path
              d="M0,120 L0,70 L120,30 L220,80 L340,20 L460,70 L580,30 L720,80 L860,40 L1000,70 L1000,120 Z"
              fill="oklch(0.78 0.06 200 / 0.55)"
            />
            <path
              d="M0,120 L0,90 L160,55 L300,90 L440,50 L600,90 L760,60 L900,90 L1000,80 L1000,120 Z"
              fill="oklch(0.70 0.07 180 / 0.65)"
            />
          </svg>

          {/* Ground hills */}
          <svg
            className="absolute inset-x-0 bottom-0 w-full"
            viewBox="0 0 1000 220"
            preserveAspectRatio="none"
            style={{ height: "55%" }}
          >
            <path
              d="M0,220 L0,80 Q250,20 500,70 T1000,60 L1000,220 Z"
              fill="oklch(0.82 0.12 145)"
            />
            <path
              d="M0,220 L0,140 Q300,90 600,130 T1000,120 L1000,220 Z"
              fill="oklch(0.74 0.14 145)"
            />
            <path
              d="M0,220 L0,180 Q350,150 700,175 T1000,170 L1000,220 Z"
              fill="oklch(0.66 0.15 145)"
            />
          </svg>

          {/* Floating leaves ambience */}
          {[0, 1, 2, 3].map((i) => (
            <div
              key={i}
              className="absolute text-2xl pointer-events-none animate-[leaf-fall_6s_ease-in-out_infinite]"
              style={{
                left: `${15 + i * 22}%`,
                top: 0,
                animationDelay: `${i * 1.4}s`,
              }}
            >
              🍃
            </div>
          ))}

          {/* Trees */}
          {trees.map((t) => (
            <img
              key={t.id}
              src={TREE_IMG[t.kind]}
              alt={`${t.kind} tree`}
              className={`absolute pointer-events-none drop-shadow-lg ${
                t.fresh ? "animate-[tree-pop_0.9s_cubic-bezier(0.34,1.56,0.64,1)]" : ""
              }`}
              style={{
                left: `${t.x}%`,
                top: `${t.y}%`,
                transform: `translate(-50%, -100%) scale(${t.scale})`,
                transformOrigin: "bottom center",
                width: 130,
                height: 130,
                zIndex: Math.round(t.y),
              }}
              loading="lazy"
            />
          ))}

          {/* Header overlay */}
          <div className="absolute top-4 left-4 right-4 flex items-center justify-between z-50">
            <div className="rounded-2xl bg-card/80 backdrop-blur px-3 py-1.5 shadow-card">
              <div className="text-[10px] uppercase tracking-widest font-bold text-primary">
                Spring grove · 2025
              </div>
              <div className="text-xs font-semibold">{trees.length} trees thriving</div>
            </div>
            <span className="rounded-full bg-card/80 backdrop-blur px-3 py-1.5 text-xs font-semibold shadow-card inline-flex items-center gap-1.5">
              <Sparkles className="h-3 w-3 text-primary" /> +1 tree per focused session
            </span>
          </div>
        </div>
      </section>

      <AvatarTip
        mood="reading"
        message={
          planting
            ? "A new sapling is taking root… 🌱"
            : "Tap “Plant a tree” to add one to your grove. Every session counts! 🌳"
        }
      />
    </div>
  );
}
