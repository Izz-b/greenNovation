import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { PageHeader } from "@/components/PageHeader";
import { AvatarTip } from "@/components/AvatarTip";
import { useState } from "react";
import { Plus, Flame, MessageSquare, Sparkles, CheckCircle2 } from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { awardTree } from "@/lib/treeInventory";

export const Route = createFileRoute("/projects")({
  head: () => ({
    meta: [
      { title: "Projects — EcoLearn AI" },
      {
        name: "description",
        content: "Track milestones, deadlines and AI-suggested next steps for every project.",
      },
      { property: "og:title", content: "Projects — EcoLearn AI" },
      {
        property: "og:description",
        content: "A smart project manager built for students.",
      },
    ],
  }),
  component: () => (
    <AppLayout>
      <ProjectsPage />
    </AppLayout>
  ),
});

type Milestone = { id: string; name: string; done: boolean };
type Project = {
  id: string;
  name: string;
  tag: string;
  due: string;
  nextStep: string;
  notes: number;
  milestones: Milestone[];
};

const INITIAL_PROJECTS: Project[] = [
  {
    id: "ml",
    name: "ML Capstone · Image Classifier",
    tag: "AI / CS",
    due: "May 12",
    nextStep: "Train baseline CNN on cleaned dataset",
    notes: 4,
    milestones: [
      { id: "ml-1", name: "Dataset collection", done: true },
      { id: "ml-2", name: "Preprocessing pipeline", done: true },
      { id: "ml-3", name: "Baseline model", done: false },
      { id: "ml-4", name: "Hyperparameter tuning", done: false },
      { id: "ml-5", name: "Final report", done: false },
    ],
  },
  {
    id: "hist",
    name: "History Essay — Industrial Revolution",
    tag: "Humanities",
    due: "May 18",
    nextStep: "Outline three central arguments with sources",
    notes: 2,
    milestones: [
      { id: "h-1", name: "Research", done: true },
      { id: "h-2", name: "Outline", done: false },
      { id: "h-3", name: "First draft", done: false },
      { id: "h-4", name: "Final draft", done: false },
    ],
  },
  {
    id: "phys",
    name: "Group Lab Report — Thermodynamics",
    tag: "Physics",
    due: "Apr 28",
    nextStep: "Polish discussion section & format references",
    notes: 7,
    milestones: [
      { id: "p-1", name: "Experiment", done: true },
      { id: "p-2", name: "Data analysis", done: true },
      { id: "p-3", name: "Draft", done: true },
      { id: "p-4", name: "Review & submit", done: false },
    ],
  },
];

function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>(INITIAL_PROJECTS);
  const [pending, setPending] = useState<{
    projectId: string;
    milestoneId: string;
    name: string;
    completing: boolean; // true = ticking, false = un-ticking
  } | null>(null);

  const requestToggle = (project: Project, m: Milestone) => {
    setPending({
      projectId: project.id,
      milestoneId: m.id,
      name: m.name,
      completing: !m.done,
    });
  };

  const confirmToggle = () => {
    if (!pending) return;
    setProjects((ps) =>
      ps.map((p) => {
        if (p.id !== pending.projectId) return p;
        const updatedMilestones = p.milestones.map((m) =>
          m.id === pending.milestoneId ? { ...m, done: pending.completing } : m,
        );
        const wasComplete = p.milestones.every((m) => m.done);
        const isComplete = updatedMilestones.every((m) => m.done);
        if (!wasComplete && isComplete) {
          // Award a tree exactly once per project completion.
          awardTree(
            "project",
            `Project complete: "${p.name}" — you earned a bamboo tree! 🎋`,
            `project-${p.id}`,
          );
        }
        return { ...p, milestones: updatedMilestones };
      }),
    );
    setPending(null);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <PageHeader
        eyebrow="Projects"
        title="Your active work"
        description="Milestones, deadlines and AI-suggested next steps — all in one place."
        actions={
          <button className="inline-flex items-center gap-2 rounded-xl gradient-primary text-primary-foreground px-4 py-2.5 text-sm font-semibold shadow-glow hover:opacity-95 transition">
            <Plus className="h-4 w-4" />
            New project
          </button>
        }
      />

      <AvatarTip
        mood="reading"
        message="Your Lab Report is almost done — tick off the last task to free your weekend."
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {projects.map((p) => {
          const completed = p.milestones.filter((m) => m.done).length;
          const progress = Math.round((completed / p.milestones.length) * 100);
          return (
            <article
              key={p.id}
              className="rounded-3xl bg-card border border-border p-6 shadow-card hover:shadow-soft transition"
            >
              <div className="flex items-start justify-between gap-3 mb-3">
                <div>
                  <span className="text-[10px] uppercase tracking-widest font-bold rounded-full bg-secondary text-secondary-foreground px-2.5 py-1">
                    {p.tag}
                  </span>
                  <h3 className="font-display text-lg font-bold mt-2 leading-tight">{p.name}</h3>
                </div>
                <div className="text-right">
                  <div className="text-xs text-muted-foreground">Due</div>
                  <div className="font-semibold">{p.due}</div>
                </div>
              </div>

              <div className="flex items-center justify-between text-xs mb-1.5">
                <span className="text-muted-foreground">Progress</span>
                <span className="font-semibold">{progress}%</span>
              </div>
              <div className="h-2.5 rounded-full bg-muted overflow-hidden mb-5">
                <div
                  className="h-full gradient-primary rounded-full transition-all duration-500"
                  style={{ width: `${progress}%` }}
                />
              </div>

              <div className="rounded-2xl gradient-warm p-4 mb-4">
                <div className="flex items-center gap-1.5 text-xs font-bold text-accent-foreground uppercase tracking-wider mb-1">
                  <Sparkles className="h-3.5 w-3.5" />
                  AI suggests next
                </div>
                <p className="text-sm font-medium">{p.nextStep}</p>
              </div>

              <ul className="space-y-1.5 mb-4">
                {p.milestones.map((m) => (
                  <li key={m.id}>
                    <button
                      onClick={() => requestToggle(p, m)}
                      className={`w-full flex items-center gap-2.5 text-sm text-left rounded-lg px-2 py-1.5 transition hover:bg-muted/60 ${
                        m.done ? "" : ""
                      }`}
                      aria-pressed={m.done}
                    >
                      <span
                        className={`h-5 w-5 rounded-md grid place-items-center text-[11px] shrink-0 transition ${
                          m.done
                            ? "bg-primary text-primary-foreground"
                            : "border-2 border-border bg-card hover:border-primary/60"
                        }`}
                      >
                        {m.done && <CheckCircle2 className="h-3.5 w-3.5" />}
                      </span>
                      <span
                        className={
                          m.done ? "text-muted-foreground line-through" : "text-foreground"
                        }
                      >
                        {m.name}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>

              <div className="flex items-center justify-between border-t border-border pt-3 text-xs text-muted-foreground">
                <span className="inline-flex items-center gap-1">
                  <MessageSquare className="h-3.5 w-3.5" /> {p.notes} notes
                </span>
                <span className="inline-flex items-center gap-1 text-accent-foreground">
                  <Flame className="h-3.5 w-3.5" /> on track
                </span>
              </div>
            </article>
          );
        })}
      </div>

      {/* Confirmation dialog */}
      <AlertDialog open={pending !== null} onOpenChange={(o) => !o && setPending(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {pending?.completing ? "Mark task as completed?" : "Mark task as not completed?"}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {pending?.completing ? (
                <>
                  You're about to tick <strong className="text-foreground">{pending?.name}</strong>{" "}
                  as done. Bamboo will celebrate with you 🐼🎉
                </>
              ) : (
                <>
                  You're about to un-tick{" "}
                  <strong className="text-foreground">{pending?.name}</strong>. Are you sure it's
                  not finished?
                </>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={confirmToggle}>
              {pending?.completing ? "Yes, mark done" : "Yes, un-tick"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
