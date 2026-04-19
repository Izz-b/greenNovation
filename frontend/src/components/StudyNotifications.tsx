import { useEffect, useRef, useState } from "react";
import { Sparkles, Coffee, BookOpen, Brain, Leaf, Target, Clock } from "lucide-react";

type Notif = {
  uid: string;
  icon: typeof Sparkles;
  title: string;
  body: string;
  tone: "primary" | "warm" | "sky";
  isNew?: boolean;
};

const POOL: Omit<Notif, "uid" | "isNew">[] = [
  {
    icon: Brain,
    title: "Suggested study plan",
    body: "25 min reading → 10 min quiz → 5 min recap. Repeat tomorrow.",
    tone: "warm",
  },
  {
    icon: Target,
    title: "You're close to a streak",
    body: "Just 12 more focused minutes to hit your daily goal. 🔥",
    tone: "primary",
  },
  {
    icon: Coffee,
    title: "Time for a micro-break",
    body: "Stand, stretch, drink water. Bamboo will wait. ☕",
    tone: "sky",
  },
  {
    icon: BookOpen,
    title: "Pick up where you left off",
    body: "You stopped at Ch. 3 — Eigenvectors, page 4. One push to finish?",
    tone: "warm",
  },
  {
    icon: Leaf,
    title: "Your forest grew today",
    body: "+1 sapling planted. 3 more sessions and a new tree appears 🌳",
    tone: "primary",
  },
  {
    icon: Clock,
    title: "Best focus window",
    body: "You concentrate hardest 9:30–11:00. Save Q4 review for then.",
    tone: "sky",
  },
];

const TONE: Record<Notif["tone"], string> = {
  primary: "bg-primary/10 text-primary border-primary/20",
  warm: "bg-accent/40 text-accent-foreground border-accent/40",
  sky: "bg-secondary/60 text-secondary-foreground border-secondary",
};

let counter = 0;
const make = (i: number): Notif => {
  const item = POOL[i % POOL.length];
  counter += 1;
  return { ...item, uid: `n-${counter}` };
};

// Soft "blip" via WebAudio — no asset needed.
function playBlip() {
  try {
    const Ctx =
      (window.AudioContext as typeof AudioContext | undefined) ??
      ((window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext);
    if (!Ctx) return;
    const ctx = new Ctx();
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.type = "sine";
    o.frequency.setValueAtTime(880, ctx.currentTime);
    o.frequency.exponentialRampToValueAtTime(1320, ctx.currentTime + 0.08);
    g.gain.setValueAtTime(0.0001, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.08, ctx.currentTime + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.25);
    o.connect(g).connect(ctx.destination);
    o.start();
    o.stop(ctx.currentTime + 0.28);
    setTimeout(() => ctx.close(), 400);
  } catch {
    /* ignore */
  }
}

export function StudyNotifications() {
  // visible[0] = top, visible[1] = bottom
  const [visible, setVisible] = useState<Notif[]>(() => [make(0), make(1)]);
  const [leavingId, setLeavingId] = useState<string | null>(null);
  const idxRef = useRef(2);
  const mountedRef = useRef(false);

  useEffect(() => {
    const tick = () => {
      // Step 1: mark top as leaving
      const top = visible[0];
      setLeavingId(top.uid);

      // Step 2: after exit animation, drop top, append new
      setTimeout(() => {
        setVisible((cur) => {
          const next = make(idxRef.current);
          idxRef.current += 1;
          const newList = [cur[1], { ...next, isNew: true }];
          return newList;
        });
        setLeavingId(null);
        if (mountedRef.current) playBlip();

        // remove "isNew" flag after the highlight pulse
        setTimeout(() => {
          setVisible((cur) => cur.map((n) => ({ ...n, isNew: false })));
        }, 1200);
      }, 450);
    };

    const t = setInterval(tick, 7000);
    mountedRef.current = true;
    return () => clearInterval(t);
  }, [visible]);

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 px-1">
        <Sparkles className="h-3.5 w-3.5 text-primary" />
        <span className="text-[10px] uppercase tracking-widest font-bold text-muted-foreground">
          Live recommendations
        </span>
      </div>
      <div className="relative space-y-3">
        {visible.map((n, i) => {
          const Icon = n.icon;
          const leaving = leavingId === n.uid;
          const animation = leaving
            ? "notif-leave 0.45s cubic-bezier(0.4, 0, 1, 1) forwards"
            : n.isNew
              ? "notif-enter 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)"
              : "notif-shift 0.5s cubic-bezier(0.34, 1.4, 0.64, 1)";
          return (
            <div
              key={n.uid}
              className={`relative rounded-2xl bg-card border border-border shadow-card p-4 flex items-start gap-3 ${
                n.isNew ? "ring-2 ring-primary/40" : ""
              }`}
              style={{ animation }}
            >
              {n.isNew && (
                <span
                  className="pointer-events-none absolute inset-0 rounded-2xl"
                  style={{ animation: "notif-glow 1.2s ease-out" }}
                />
              )}
              <div
                className={`h-10 w-10 rounded-xl border grid place-items-center shrink-0 ${TONE[n.tone]}`}
              >
                <Icon className="h-5 w-5" />
              </div>
              <div className="min-w-0">
                <div className="text-xs font-bold flex items-center gap-1.5">
                  {n.title}
                  {i === 0 && (
                    <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
                  )}
                </div>
                <p className="text-xs text-muted-foreground mt-0.5 leading-snug">{n.body}</p>
              </div>
            </div>
          );
        })}
      </div>
      <style>{`
        @keyframes notif-enter {
          0% { transform: translateY(28px) scale(0.92); opacity: 0; }
          60% { transform: translateY(-2px) scale(1.02); opacity: 1; }
          100% { transform: translateY(0) scale(1); opacity: 1; }
        }
        @keyframes notif-leave {
          0% { transform: translateY(0) scale(1); opacity: 1; }
          100% { transform: translateY(-24px) scale(0.96); opacity: 0; }
        }
        @keyframes notif-shift {
          0% { transform: translateY(14px) scale(0.98); }
          100% { transform: translateY(0) scale(1); }
        }
        @keyframes notif-glow {
          0% { box-shadow: 0 0 0 0 color-mix(in oklab, var(--primary) 50%, transparent); }
          100% { box-shadow: 0 0 0 14px color-mix(in oklab, var(--primary) 0%, transparent); }
        }
      `}</style>
    </div>
  );
}
