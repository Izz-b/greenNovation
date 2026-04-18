import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { PageHeader } from "@/components/PageHeader";
import { AvatarTip } from "@/components/AvatarTip";
import { Smile, Meh, Frown, Heart, Moon, Coffee, Wind } from "lucide-react";

export const Route = createFileRoute("/wellbeing")({
  head: () => ({
    meta: [
      { title: "Well-being — EcoLearn AI" },
      {
        name: "description",
        content: "A calm space to check in with yourself and prevent study overload.",
      },
      { property: "og:title", content: "Well-being — EcoLearn AI" },
      {
        property: "og:description",
        content: "Supportive, never clinical. Stay balanced while you study.",
      },
    ],
  }),
  component: () => (
    <AppLayout>
      <WellbeingPage />
    </AppLayout>
  ),
});

function WellbeingPage() {
  const week = [3, 4, 5, 4, 6, 5, 4]; // hours
  const max = Math.max(...week);
  const days = ["M", "T", "W", "T", "F", "S", "S"];

  const quotes = [
    "“Slow is smooth, smooth is fast.” — every owl ever 🦉",
    "Your brain is not a browser tab. Close some.",
    "Tiny wins, daily. The forest grew one leaf at a time.",
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <PageHeader
        eyebrow="Well-being"
        title="How are you feeling today?"
        description="A gentle check-in helps EcoLearn shape a kinder schedule for you."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Check-in */}
        <section className="lg:col-span-2 rounded-3xl bg-card border border-border p-6 lg:p-8 shadow-card">
          <h3 className="font-display text-xl font-bold mb-4">Daily check-in</h3>
          <div className="grid grid-cols-3 gap-3">
            {[
              { icon: Smile, label: "Great", color: "bg-success/10 text-success border-success/30" },
              { icon: Meh, label: "Okay", color: "bg-warning/10 text-warning border-warning/30" },
              { icon: Frown, label: "Heavy", color: "bg-info/10 text-info border-info/30" },
            ].map((m) => (
              <button
                key={m.label}
                className={`rounded-2xl border-2 p-5 flex flex-col items-center gap-2 hover:scale-[1.03] active:scale-[0.98] transition ${m.color}`}
              >
                <m.icon className="h-8 w-8" />
                <span className="font-semibold text-sm">{m.label}</span>
              </button>
            ))}
          </div>

          <div className="mt-6 rounded-2xl gradient-warm p-5">
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider mb-1">
              <Heart className="h-3.5 w-3.5" /> Today's quote
            </div>
            <p className="text-base font-medium">{quotes[0]}</p>
          </div>
        </section>

        {/* Suggestions */}
        <section className="rounded-3xl bg-card border border-border p-6 shadow-card">
          <h3 className="font-semibold mb-4">Balance suggestions</h3>
          <ul className="space-y-3">
            {[
              { icon: Wind, label: "5-min breathing break", time: "now" },
              { icon: Coffee, label: "Hydrate & stretch", time: "in 30 min" },
              { icon: Moon, label: "Wind-down at 22:30", time: "tonight" },
            ].map((s) => (
              <li
                key={s.label}
                className="flex items-center gap-3 rounded-2xl p-3 hover:bg-muted/60 transition"
              >
                <div className="h-10 w-10 rounded-xl gradient-sky grid place-items-center">
                  <s.icon className="h-5 w-5" />
                </div>
                <div className="flex-1">
                  <div className="text-sm font-semibold">{s.label}</div>
                  <div className="text-xs text-muted-foreground">{s.time}</div>
                </div>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <AvatarTip message="Your study time has crept up the last 3 days. Let's protect tonight — no sessions after 22:00. 💚" />

      {/* Overload chart */}
      <section className="rounded-3xl bg-card border border-border p-6 lg:p-8 shadow-card">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold">Study intensity · This week</h3>
          <span className="text-xs text-muted-foreground">hours / day</span>
        </div>
        <p className="text-sm text-muted-foreground mb-6">
          Aim for steady 4–5h with at least one lighter day.
        </p>
        <div className="flex items-end gap-3 h-48">
          {week.map((h, i) => (
            <div key={i} className="flex-1 flex flex-col items-center gap-2">
              <div className="w-full flex-1 flex items-end">
                <div
                  className={`w-full rounded-t-2xl transition-all ${
                    h > 5 ? "gradient-warm" : "gradient-primary"
                  }`}
                  style={{ height: `${(h / max) * 100}%` }}
                  title={`${h}h`}
                />
              </div>
              <div className="text-xs font-mono text-muted-foreground">{days[i]}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
