import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { AvatarTip } from "@/components/AvatarTip";
import { Link } from "@tanstack/react-router";
import {
  Flame,
  Clock,
  TrendingUp,
  ArrowRight,
  Trees,
  CheckCircle2,
  AlertTriangle,
  BookOpen,
  Calendar,
  Brain,
  Zap,
} from "lucide-react";
import treeSapling from "@/assets/tree-sapling.png";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Dashboard — EcoLearn AI" },
      {
        name: "description",
        content:
          "Your command center: readiness, study plan, deadlines and Eco Forest at a glance.",
      },
      { property: "og:title", content: "Dashboard — EcoLearn AI" },
      {
        property: "og:description",
        content: "What should I do now? Your AI-powered student dashboard answers it.",
      },
    ],
  }),
  component: DashboardPage,
});

function DashboardPage() {
  return (
    <AppLayout>
      <Dashboard />
    </AppLayout>
  );
}

function Dashboard() {
  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Greeting */}
      <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4 animate-[fade-in-up_0.5s_ease-out]">
        <div>
          <div className="text-xs uppercase tracking-[0.2em] text-primary font-semibold mb-2">
            Tuesday · Week 7
          </div>
          <h1 className="font-display text-3xl lg:text-4xl font-bold tracking-tight">
            Good morning, <span className="text-gradient-primary">Sara</span> 🌿
          </h1>
          <p className="text-muted-foreground mt-2">
            You're 78% ready for today. Here's your next best move.
          </p>
        </div>
        <div className="flex gap-2">
          <button className="rounded-xl bg-card border border-border px-4 py-2.5 text-sm font-medium hover:bg-muted transition shadow-card">
            View calendar
          </button>
          <button className="rounded-xl gradient-primary text-primary-foreground px-4 py-2.5 text-sm font-semibold shadow-glow hover:opacity-95 transition">
            Start session
          </button>
        </div>
      </div>

      {/* Top grid: Readiness + Next Action + Forest */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <ReadinessCard />
        <NextActionCard />
        <EcoForestCard />
      </div>

      {/* Middle grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <StudyPlanCard />
        <DeadlinesCard />
        <WeakTopicsCard />
      </div>

      {/* Bottom row: avatar tip + projects */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-1">
          <AvatarTip mood="reading" message="You learn calculus best in 25-min sprints. Try one before lunch — I'll keep your forest watered. 🌳" />
        </div>
        <ActiveProjectsCard className="lg:col-span-2" />
      </div>
    </div>
  );
}

/* ---------------- Cards ---------------- */

function Card({
  children,
  className = "",
  variant = "default",
}: {
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "primary" | "warm" | "sky";
}) {
  const variants: Record<string, string> = {
    default: "bg-card border border-border",
    primary: "gradient-primary text-primary-foreground",
    warm: "gradient-warm",
    sky: "gradient-sky",
  };
  return (
    <div
      className={`rounded-3xl p-5 lg:p-6 shadow-card transition-all hover:shadow-soft ${variants[variant]} ${className}`}
    >
      {children}
    </div>
  );
}

function ReadinessCard() {
  const score = 78;
  return (
    <Card className="lg:col-span-4 relative overflow-hidden">
      <div className="absolute inset-0 opacity-40 pointer-events-none">
        <div className="absolute -top-10 -right-10 h-40 w-40 rounded-full bg-primary-glow/40 blur-3xl" />
      </div>
      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-muted-foreground">
            <Brain className="h-4 w-4 text-primary" />
            Readiness today
          </div>
          <span className="text-xs rounded-full bg-success/10 text-success px-2.5 py-1 font-semibold">
            Above average
          </span>
        </div>

        <div className="flex items-center gap-5">
          <div
            className="relative h-32 w-32 rounded-full grid place-items-center"
            style={{
              background: `conic-gradient(var(--primary) ${score * 3.6}deg, color-mix(in oklab, var(--muted) 90%, transparent) 0deg)`,
            }}
          >
            <div className="h-[104px] w-[104px] rounded-full bg-card grid place-items-center">
              <div className="text-center">
                <div className="font-display text-3xl font-bold">{score}</div>
                <div className="text-[10px] uppercase tracking-widest text-muted-foreground">
                  / 100
                </div>
              </div>
            </div>
          </div>
          <div className="flex-1 space-y-2.5">
            <Stat label="Focus" value={82} color="primary" />
            <Stat label="Sleep" value={70} color="info" />
            <Stat label="Mood" value={84} color="warning" />
          </div>
        </div>
      </div>
    </Card>
  );
}

function Stat({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: "primary" | "info" | "warning";
}) {
  const bg = {
    primary: "bg-primary",
    info: "bg-info",
    warning: "bg-warning",
  }[color];
  return (
    <div>
      <div className="flex items-center justify-between text-xs font-medium mb-1">
        <span className="text-muted-foreground">{label}</span>
        <span className="text-foreground">{value}%</span>
      </div>
      <div className="h-2 rounded-full bg-muted overflow-hidden">
        <div className={`h-full rounded-full ${bg}`} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

function NextActionCard() {
  return (
    <Card variant="primary" className="lg:col-span-5 relative overflow-hidden">
      <div className="absolute -bottom-12 -right-8 h-48 w-48 rounded-full bg-primary-foreground/10 blur-3xl" />
      <div className="absolute top-4 right-4">
        <span className="text-[10px] uppercase tracking-widest font-bold bg-primary-foreground/15 px-2.5 py-1 rounded-full">
          Next best action
        </span>
      </div>
      <div className="relative">
        <div className="text-xs uppercase tracking-widest opacity-70 font-semibold mb-2">
          AI Recommendation
        </div>
        <h2 className="font-display text-2xl lg:text-3xl font-bold leading-tight">
          Review <span className="underline decoration-primary-foreground/40 decoration-2 underline-offset-4">Linear Algebra · Eigenvectors</span> for 25 min
        </h2>
        <p className="opacity-85 text-sm mt-3 max-w-md">
          You scored 62% on yesterday's quiz. A short focused review will lift your mastery to ~80%.
        </p>
        <div className="flex flex-wrap items-center gap-2 mt-5">
          <Link
            to="/workspace"
            className="inline-flex items-center gap-2 rounded-xl bg-primary-foreground text-primary px-4 py-2.5 text-sm font-bold hover:scale-[1.02] transition shadow-soft"
          >
            Start session
            <ArrowRight className="h-4 w-4" />
          </Link>
          <button className="rounded-xl bg-primary-foreground/15 px-4 py-2.5 text-sm font-medium hover:bg-primary-foreground/25 transition">
            Explain why
          </button>
          <div className="ml-auto flex items-center gap-1.5 text-xs opacity-80">
            <Zap className="h-3.5 w-3.5" />
            ~ 0.04 kWh
          </div>
        </div>
      </div>
    </Card>
  );
}

function EcoForestCard() {
  return (
    <Card className="lg:col-span-3 relative overflow-hidden gradient-forest">
      <div className="absolute inset-0 opacity-50 pointer-events-none">
        <div className="absolute bottom-0 left-0 right-0 h-2/3 bg-gradient-to-t from-primary/20 to-transparent" />
      </div>
      <div className="relative">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm font-semibold">
            <Trees className="h-4 w-4 text-primary" />
            Eco Forest
          </div>
          <span className="text-xs rounded-full bg-card/70 px-2 py-1 font-semibold">
            🔥 4-day streak
          </span>
        </div>
        <div className="flex items-end justify-center pt-2">
          <img
            src={treeSapling}
            alt="Your growing tree"
            width={140}
            height={140}
            className="h-32 drop-shadow-lg animate-[pulse-soft_3s_ease-in-out_infinite]"
            loading="lazy"
          />
        </div>
        <div className="text-center">
          <div className="font-display text-2xl font-bold">12 trees</div>
          <div className="text-xs text-muted-foreground">Grown this semester</div>
        </div>
        <Link
          to="/forest"
          className="mt-3 flex items-center justify-center gap-1.5 text-xs font-semibold text-primary hover:underline"
        >
          Visit your forest <ArrowRight className="h-3.5 w-3.5" />
        </Link>
      </div>
    </Card>
  );
}

function StudyPlanCard() {
  const blocks = [
    { time: "09:00", title: "Linear Algebra review", dur: "25 min", type: "review", done: true },
    { time: "10:30", title: "Quiz: Eigenvectors", dur: "10 min", type: "quiz", done: false },
    { time: "14:00", title: "ML notes summary", dur: "20 min", type: "summary", done: false },
    { time: "16:30", title: "Group project sync", dur: "30 min", type: "project", done: false },
  ];
  const typeStyle: Record<string, string> = {
    review: "bg-primary/10 text-primary",
    quiz: "bg-warning/15 text-warning-foreground",
    summary: "bg-info/15 text-info",
    project: "bg-accent text-accent-foreground",
  };
  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-primary" />
          <h3 className="font-semibold">Today's plan</h3>
        </div>
        <button className="text-xs font-semibold text-primary hover:underline">Edit</button>
      </div>
      <ul className="space-y-2.5">
        {blocks.map((b) => (
          <li
            key={b.title}
            className={`flex items-center gap-3 rounded-2xl p-3 border border-transparent hover:border-border transition ${
              b.done ? "opacity-60" : ""
            }`}
          >
            <div className="text-xs font-mono text-muted-foreground w-12">{b.time}</div>
            <div
              className={`h-9 w-9 rounded-xl grid place-items-center text-xs font-bold ${typeStyle[b.type]}`}
            >
              {b.type[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className={`text-sm font-medium truncate ${b.done ? "line-through" : ""}`}>
                {b.title}
              </div>
              <div className="text-xs text-muted-foreground">{b.dur}</div>
            </div>
            {b.done && <CheckCircle2 className="h-4 w-4 text-success" />}
          </li>
        ))}
      </ul>
    </Card>
  );
}

function DeadlinesCard() {
  const items = [
    { title: "ML Project · Phase 2", in: "2 days", urgency: "high" },
    { title: "Calculus problem set", in: "5 days", urgency: "med" },
    { title: "Ethics essay draft", in: "9 days", urgency: "low" },
  ];
  const urgencyColor: Record<string, string> = {
    high: "bg-destructive/10 text-destructive",
    med: "bg-warning/15 text-warning-foreground",
    low: "bg-info/10 text-info",
  };
  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Clock className="h-4 w-4 text-primary" />
          <h3 className="font-semibold">Upcoming deadlines</h3>
        </div>
        <Link to="/projects" className="text-xs font-semibold text-primary hover:underline">
          All
        </Link>
      </div>
      <ul className="space-y-3">
        {items.map((d) => (
          <li
            key={d.title}
            className="flex items-center gap-3 rounded-2xl p-3 hover:bg-muted/60 transition"
          >
            <AlertTriangle
              className={`h-4 w-4 ${
                d.urgency === "high"
                  ? "text-destructive"
                  : d.urgency === "med"
                    ? "text-warning"
                    : "text-info"
              }`}
            />
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{d.title}</div>
              <div className="text-xs text-muted-foreground">in {d.in}</div>
            </div>
            <span className={`text-[10px] uppercase tracking-wider rounded-full px-2 py-1 font-bold ${urgencyColor[d.urgency]}`}>
              {d.urgency}
            </span>
          </li>
        ))}
      </ul>
    </Card>
  );
}

function WeakTopicsCard() {
  const topics = [
    { name: "Eigenvectors", level: 42 },
    { name: "Backpropagation", level: 55 },
    { name: "Bayesian inference", level: 61 },
  ];
  return (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-primary" />
          <h3 className="font-semibold">Topics to strengthen</h3>
        </div>
        <span className="text-xs text-muted-foreground">Mastery</span>
      </div>
      <ul className="space-y-4">
        {topics.map((t) => (
          <li key={t.name}>
            <div className="flex items-center justify-between text-sm mb-1.5">
              <span className="font-medium">{t.name}</span>
              <span className="text-muted-foreground text-xs">{t.level}%</span>
            </div>
            <div className="h-2.5 rounded-full bg-muted overflow-hidden">
              <div
                className="h-full rounded-full gradient-primary"
                style={{ width: `${t.level}%` }}
              />
            </div>
          </li>
        ))}
      </ul>
      <Link
        to="/learning"
        className="mt-5 inline-flex items-center gap-1.5 text-xs font-semibold text-primary hover:underline"
      >
        Practice now <ArrowRight className="h-3.5 w-3.5" />
      </Link>
    </Card>
  );
}

function ActiveProjectsCard({ className = "" }: { className?: string }) {
  const projects = [
    {
      name: "ML Capstone · Image Classifier",
      progress: 65,
      next: "Train baseline CNN",
      due: "in 2 days",
      tag: "AI",
    },
    {
      name: "History essay · Industrial revolution",
      progress: 30,
      next: "Outline arguments",
      due: "in 1 week",
      tag: "Humanities",
    },
  ];
  return (
    <Card className={className}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <BookOpen className="h-4 w-4 text-primary" />
          <h3 className="font-semibold">Active projects</h3>
        </div>
        <Link to="/projects" className="text-xs font-semibold text-primary hover:underline">
          View all
        </Link>
      </div>
      <div className="grid sm:grid-cols-2 gap-3">
        {projects.map((p) => (
          <div
            key={p.name}
            className="rounded-2xl border border-border p-4 hover:border-primary/40 hover:shadow-soft transition"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] uppercase tracking-wider font-bold rounded-full bg-secondary text-secondary-foreground px-2 py-0.5">
                {p.tag}
              </span>
              <Flame className="h-3.5 w-3.5 text-accent-foreground" />
            </div>
            <div className="font-semibold text-sm leading-snug">{p.name}</div>
            <div className="mt-3 h-2 rounded-full bg-muted overflow-hidden">
              <div className="h-full gradient-primary rounded-full" style={{ width: `${p.progress}%` }} />
            </div>
            <div className="mt-3 flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Next: {p.next}</span>
              <span className="font-semibold text-foreground">{p.due}</span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}
