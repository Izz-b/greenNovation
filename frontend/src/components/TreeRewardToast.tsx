import { useEffect, useRef, useState } from "react";
import { Link } from "@tanstack/react-router";
import { ArrowRight, X, Sparkles } from "lucide-react";
import { Panda } from "@/components/PandaCompanion";
import { useTreeInventory } from "@/hooks/useTreeInventory";
import { clearLastReward, type TreeReward } from "@/lib/treeInventory";

// Plays a soft, pleasant chime when a tree is earned.
function playChime() {
  try {
    type AC = typeof AudioContext;
    const w = window as unknown as { AudioContext?: AC; webkitAudioContext?: AC };
    const Ctor = w.AudioContext ?? w.webkitAudioContext;
    if (!Ctor) return;
    const ctx = new Ctor();
    const now = ctx.currentTime;
    [523.25, 659.25, 783.99].forEach((freq, i) => {
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.type = "sine";
      o.frequency.value = freq;
      g.gain.setValueAtTime(0, now + i * 0.08);
      g.gain.linearRampToValueAtTime(0.06, now + i * 0.08 + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, now + i * 0.08 + 0.35);
      o.connect(g).connect(ctx.destination);
      o.start(now + i * 0.08);
      o.stop(now + i * 0.08 + 0.4);
    });
  } catch {
    // ignore
  }
}

const CONFETTI = ["🍃", "🌿", "✨", "🌱", "🍃", "✨"];

export function TreeRewardToast() {
  const { lastReward } = useTreeInventory();
  const [active, setActive] = useState<TreeReward | null>(null);
  const [leaving, setLeaving] = useState(false);
  const seenIds = useRef<Set<string>>(new Set());
  const dismissTimer = useRef<number | null>(null);

  useEffect(() => {
    if (!lastReward) return;
    if (seenIds.current.has(lastReward.id)) return;
    seenIds.current.add(lastReward.id);
    setLeaving(false);
    setActive(lastReward);
    playChime();
    if (dismissTimer.current) window.clearTimeout(dismissTimer.current);
    dismissTimer.current = window.setTimeout(() => dismiss(), 7000);
    return () => {
      if (dismissTimer.current) window.clearTimeout(dismissTimer.current);
    };
  }, [lastReward]);

  const dismiss = () => {
    setLeaving(true);
    window.setTimeout(() => {
      setActive(null);
      clearLastReward();
    }, 350);
  };

  if (!active) return null;

  return (
    <div
      className="fixed bottom-6 right-6 z-[120] w-[340px] max-w-[calc(100vw-2rem)] pointer-events-none"
      role="status"
      aria-live="polite"
    >
      {/* confetti */}
      <div className="absolute inset-x-0 -top-4 h-10 pointer-events-none overflow-visible">
        {CONFETTI.map((c, i) => (
          <span
            key={i}
            className="absolute text-lg"
            style={{
              left: `${10 + i * 14}%`,
              animation: `confetti-burst 1.4s cubic-bezier(.2,.7,.4,1) ${i * 0.05}s forwards`,
            }}
          >
            {c}
          </span>
        ))}
      </div>

      <div
        className={`pointer-events-auto rounded-3xl bg-card border border-primary/30 shadow-glow overflow-hidden ${
          leaving ? "animate-[reward-out_.35s_ease-in_forwards]" : "animate-[reward-in_.55s_cubic-bezier(.34,1.56,.64,1)_both]"
        }`}
      >
        <div className="relative p-4 pr-3 flex gap-3">
          {/* Decorative glow */}
          <div className="absolute -top-8 -right-8 h-28 w-28 rounded-full bg-primary-glow/30 blur-2xl pointer-events-none" />

          {/* Mascot */}
          <div className="relative shrink-0">
            <Panda mood="waving" size={56} />
            <span className="absolute -bottom-1 -right-1 text-xl select-none">🌱</span>
            <Sparkles className="absolute -top-1 -right-2 h-4 w-4 text-warning animate-[seed-sparkle_1.4s_ease-in-out_infinite]" />
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div className="font-display text-sm font-bold leading-tight">
                🌱 New tree earned!
              </div>
              <button
                onClick={dismiss}
                aria-label="Dismiss"
                className="shrink-0 -mt-1 -mr-1 rounded-full p-1 hover:bg-muted transition"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
            <p className="text-xs text-muted-foreground mt-1 leading-snug">{active.message}</p>
            <Link
              to="/forest"
              onClick={dismiss}
              className="mt-2.5 inline-flex items-center gap-1.5 rounded-full gradient-primary text-primary-foreground px-3 py-1.5 text-xs font-bold shadow-soft hover:opacity-95 transition"
            >
              Go to forest
              <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
