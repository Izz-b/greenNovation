import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { PageHeader } from "@/components/PageHeader";
import { AvatarTip } from "@/components/AvatarTip";
import { Play, Brain, Trophy, Sparkles, ArrowRight } from "lucide-react";

export const Route = createFileRoute("/learning")({
  head: () => ({
    meta: [
      { title: "Learning — EcoLearn AI" },
      {
        name: "description",
        content: "Adaptive lessons, mastery tracking and a daily quiz tailored to you.",
      },
      { property: "og:title", content: "Learning — EcoLearn AI" },
      {
        property: "og:description",
        content: "A guided learning journey that adapts to your strengths and gaps.",
      },
    ],
  }),
  component: () => (
    <AppLayout>
      <LearningPage />
    </AppLayout>
  ),
});

function LearningPage() {
  const courses = [
    { name: "Linear Algebra", mastery: 72, accent: "primary" },
    { name: "Machine Learning", mastery: 58, accent: "info" },
    { name: "Modern Physics", mastery: 84, accent: "warning" },
    { name: "Ethics in Tech", mastery: 41, accent: "accent" },
  ];

  const topics = [
    { name: "Vectors & spaces", level: 92 },
    { name: "Linear maps", level: 78 },
    { name: "Eigenvalues", level: 62 },
    { name: "Eigenvectors", level: 42 },
    { name: "Diagonalization", level: 35 },
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <PageHeader
        eyebrow="Learning"
        title="A path tuned to you"
        description="Adaptive lessons, deep dives and quick wins — guided by your mastery."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Lesson card */}
        <div className="lg:col-span-2 rounded-3xl gradient-sky p-6 lg:p-8 shadow-card relative overflow-hidden">
          <div className="absolute -bottom-16 -right-16 h-56 w-56 rounded-full bg-card/30 blur-3xl" />
          <div className="relative">
            <span className="text-[10px] uppercase tracking-widest font-bold bg-card/70 px-2.5 py-1 rounded-full">
              Recommended lesson
            </span>
            <h2 className="font-display text-3xl font-bold mt-3 leading-tight">
              Eigenvectors, intuitively
            </h2>
            <p className="mt-2 text-foreground/80 max-w-md">
              A 12-minute visual deep-dive that builds on your last quiz. Includes 3 worked
              examples and an instant practice set.
            </p>
            <div className="flex flex-wrap gap-2 mt-5">
              <button className="inline-flex items-center gap-2 rounded-xl gradient-primary text-primary-foreground px-4 py-2.5 text-sm font-bold shadow-glow">
                <Play className="h-4 w-4 fill-current" /> Start lesson
              </button>
              <button className="rounded-xl bg-card/80 px-4 py-2.5 text-sm font-medium hover:bg-card transition">
                Save for later
              </button>
            </div>
          </div>
        </div>

        {/* Quiz of the day */}
        <div className="rounded-3xl bg-card border border-border p-6 shadow-card flex flex-col">
          <div className="flex items-center gap-2 text-sm font-semibold text-muted-foreground mb-2">
            <Trophy className="h-4 w-4 text-warning" />
            Quiz of the day
          </div>
          <h3 className="font-display text-xl font-bold leading-tight">
            5 questions · Backpropagation
          </h3>
          <p className="text-sm text-muted-foreground mt-2 flex-1">
            Earn a sapling 🌱 by completing today's quiz before midnight.
          </p>
          <button className="mt-4 inline-flex items-center justify-center gap-2 rounded-xl bg-foreground text-background px-4 py-2.5 text-sm font-semibold hover:opacity-90 transition">
            Take quiz <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      <AvatarTip message="Your weakest topic is Diagonalization. After today's lesson, I'll add a 5-min refresher tomorrow." />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <section className="lg:col-span-2 rounded-3xl bg-card border border-border p-6 shadow-card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Brain className="h-4 w-4 text-primary" />
              <h3 className="font-semibold">Mastery — Linear Algebra</h3>
            </div>
            <span className="text-xs text-muted-foreground">Adaptive difficulty: medium</span>
          </div>
          <ul className="space-y-4">
            {topics.map((t) => (
              <li key={t.name}>
                <div className="flex items-center justify-between text-sm mb-1.5">
                  <span className="font-medium">{t.name}</span>
                  <span className="text-muted-foreground text-xs font-mono">{t.level}%</span>
                </div>
                <div className="h-2.5 rounded-full bg-muted overflow-hidden">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${t.level}%`,
                      background:
                        t.level > 75
                          ? "var(--success)"
                          : t.level > 50
                            ? "var(--gradient-primary)"
                            : "var(--warning)",
                    }}
                  />
                </div>
              </li>
            ))}
          </ul>
        </section>

        <section className="rounded-3xl bg-card border border-border p-6 shadow-card">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="h-4 w-4 text-primary" />
            <h3 className="font-semibold">Your courses</h3>
          </div>
          <ul className="space-y-3">
            {courses.map((c) => (
              <li key={c.name} className="rounded-2xl border border-border p-3 hover:border-primary/40 transition">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="font-semibold">{c.name}</span>
                  <span className="text-xs text-muted-foreground">{c.mastery}%</span>
                </div>
                <div className="h-2 rounded-full bg-muted overflow-hidden">
                  <div className="h-full gradient-primary rounded-full" style={{ width: `${c.mastery}%` }} />
                </div>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}
