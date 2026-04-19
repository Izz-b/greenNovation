import { useEffect, useMemo, useRef, useState } from "react";
import { Wind, X, Sparkles, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

const BREAK_SECONDS = 5 * 60;

const FUNNY_LINES = [
  "Hey genius… your brain is overheating 🧠🔥",
  "Take 5 minutes. Breathe with me 🐼",
  "Inhale… exhale… don't argue.",
  "Your tabs will survive without you. Probably.",
  "Even pandas reboot. You're not a machine (yet).",
];

const PHASES = [
  { label: "Inhale", sub: "4 seconds", duration: 4000, scale: 1.35 },
  { label: "Hold", sub: "2 seconds", duration: 2000, scale: 1.35 },
  { label: "Exhale", sub: "6 seconds", duration: 6000, scale: 0.8 },
] as const;

// Pre-computed leaf particle config (stable across renders)
const LEAVES = Array.from({ length: 18 }, (_, i) => ({
  id: i,
  left: Math.random() * 100,
  delay: Math.random() * 12,
  duration: 14 + Math.random() * 14,
  size: 14 + Math.random() * 22,
  rotate: Math.random() * 360,
  emoji: ["🍃", "🌿", "🍃", "✨", "🌱"][Math.floor(Math.random() * 5)],
}));

export function BreathingBreak({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const [secondsLeft, setSecondsLeft] = useState(BREAK_SECONDS);
  const [phaseIdx, setPhaseIdx] = useState(0);
  const [closing, setClosing] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Pick a fresh funny line each time the break opens
  const line = useMemo(
    () => FUNNY_LINES[Math.floor(Math.random() * FUNNY_LINES.length)],
    [open],
  );

  // Reset on open
  useEffect(() => {
    if (open) {
      setSecondsLeft(BREAK_SECONDS);
      setPhaseIdx(0);
      setClosing(false);
    }
  }, [open]);

  // Countdown
  useEffect(() => {
    if (!open) return;
    const id = setInterval(() => {
      setSecondsLeft((s) => (s <= 1 ? 0 : s - 1));
    }, 1000);
    return () => clearInterval(id);
  }, [open]);

  // Breathing phase cycler
  useEffect(() => {
    if (!open) return;
    const t = setTimeout(() => {
      setPhaseIdx((i) => (i + 1) % PHASES.length);
    }, PHASES[phaseIdx].duration);
    return () => clearTimeout(t);
  }, [open, phaseIdx]);

  // Lock body scroll while open
  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  // Try to autoplay video (muted required for most browsers)
  useEffect(() => {
    if (open && videoRef.current) {
      videoRef.current.play().catch(() => {});
    }
  }, [open]);

  // Esc to close
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") handleClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  function handleClose() {
    setClosing(true);
    setTimeout(() => {
      onOpenChange(false);
    }, 450);
  }

  if (!open) return null;

  const phase = PHASES[phaseIdx];
  const mins = Math.floor(secondsLeft / 60);
  const secs = secondsLeft % 60;
  const done = secondsLeft === 0;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Take a breathing break"
      className={`fixed inset-0 z-[100] grid place-items-center p-4 transition-opacity duration-500 ${
        closing ? "opacity-0" : "opacity-100 animate-[fade-in-up_0.25s_ease-out]"
      }`}
    >
      {/* Glass backdrop — same as Bamboo chat popup */}
      <div
        className="absolute inset-0 bg-foreground/30 backdrop-blur-md"
        onClick={handleClose}
      />

      {/* Floating leaves / particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {LEAVES.map((l) => (
          <span
            key={l.id}
            className="absolute select-none opacity-70"
            style={{
              left: `${l.left}%`,
              top: "-10%",
              fontSize: `${l.size}px`,
              animation: `breath-leaf-fall ${l.duration}s linear ${l.delay}s infinite`,
              transform: `rotate(${l.rotate}deg)`,
            }}
          >
            {l.emoji}
          </span>
        ))}
      </div>

      {/* Modal card — matches FloatingBamboo layout */}
      <div
        className="relative w-full max-w-lg max-h-[85vh] flex flex-col rounded-3xl bg-card border border-border shadow-glow overflow-hidden"
        style={{ animation: "scale-in 0.25s cubic-bezier(0.34, 1.56, 0.64, 1)" }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header — gradient-forest with panda video avatar */}
        <div className="relative gradient-forest p-5 border-b border-border">
          <div className="flex items-start gap-4">
            <div className="h-16 w-16 rounded-2xl bg-card/60 grid place-items-center shrink-0 overflow-hidden">
              <video
                ref={videoRef}
                src="/panda-breathing.webm"
                autoPlay
                loop
                muted
                playsInline
                className="h-full w-full object-cover"
              />
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-bold uppercase tracking-widest text-primary flex items-center gap-1.5">
                <Sparkles className="h-3 w-3" />
                Bamboo · Breathing
              </div>
              <div className="font-display text-xl font-bold mt-0.5">
                {done ? "Welcome back ✨" : "Mini mental reset"}
              </div>
              <div className="text-xs text-muted-foreground mt-0.5">
                {done ? "You did it. Look at you. 🌿" : line}
              </div>
            </div>
            <button
              onClick={handleClose}
              className="rounded-lg p-2 hover:bg-card/60 transition shrink-0"
              aria-label="Close"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Body — breathing animation + timer */}
        <div className="flex-1 overflow-hidden px-6 pt-4 pb-4 flex flex-col items-center text-center">
          {/* Breathing rings — compact, never overlap header */}
          <div className="relative mt-2 mb-1 grid place-items-center" style={{ minHeight: 180 }}>
            <div
              className="absolute rounded-full bg-primary/15 transition-transform ease-in-out"
              style={{
                width: 160,
                height: 160,
                transform: `scale(${phase.scale})`,
                transitionDuration: `${phase.duration}ms`,
              }}
            />
            <div
              className="absolute rounded-full bg-accent/25 transition-transform ease-in-out"
              style={{
                width: 130,
                height: 130,
                transform: `scale(${phase.scale})`,
                transitionDuration: `${phase.duration}ms`,
              }}
            />
            <div
              className="absolute rounded-full border-2 border-primary/40 transition-transform ease-in-out"
              style={{
                width: 145,
                height: 145,
                transform: `scale(${phase.scale})`,
                transitionDuration: `${phase.duration}ms`,
              }}
            />
            <div className="relative h-24 w-24 rounded-full overflow-hidden bg-background/60 ring-4 ring-background/80 shadow-glow">
              <video
                src="/panda-breathing.webm"
                autoPlay
                loop
                muted
                playsInline
                className="h-full w-full object-cover"
              />
            </div>
          </div>

          {/* Phase label */}
          <div key={phaseIdx} className="animate-[fade-in-up_0.3s_ease-out] mt-2">
            <div className="text-base md:text-lg font-display font-bold text-primary tracking-wide">
              {done ? "All done" : phase.label}
            </div>
            {!done && (
              <div className="text-[10px] uppercase tracking-[0.25em] text-muted-foreground mt-0.5">
                {phase.sub}
              </div>
            )}
          </div>

          {/* Timer */}
          <div className="mt-2 flex items-baseline gap-1 font-display">
            <span className="text-3xl font-bold tabular-nums text-foreground drop-shadow-sm">
              {String(mins).padStart(2, "0")}
            </span>
            <span className="text-xl font-bold text-muted-foreground">:</span>
            <span className="text-3xl font-bold tabular-nums text-foreground drop-shadow-sm">
              {String(secs).padStart(2, "0")}
            </span>
          </div>
          <div className="text-[10px] uppercase tracking-[0.25em] text-muted-foreground mt-1">
            {done ? "Break complete" : "Minutes of pure chill"}
          </div>
        </div>

        {/* Footer actions */}
        <div className="p-4 border-t border-border flex flex-wrap justify-center gap-2">
          <Button
            onClick={handleClose}
            size="lg"
            className="rounded-full px-6 gradient-primary text-primary-foreground shadow-glow hover:scale-105 transition-transform"
          >
            <Zap className="h-4 w-4" />
            {done ? "Back to greatness" : "I'm recharged"}
          </Button>
          {!done && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleClose}
              className="rounded-full px-4 bg-background/50 backdrop-blur text-xs"
            >
              Skip (panda will judge you)
            </Button>
          )}
        </div>
      </div>

      {/* Local keyframes */}
      <style>{`
        @keyframes breath-leaf-fall {
          0% { transform: translateY(0) rotate(0deg); opacity: 0; }
          10% { opacity: 0.8; }
          100% { transform: translateY(110vh) rotate(720deg); opacity: 0; }
        }
        @keyframes scale-in {
          0% { transform: scale(0.85); opacity: 0; }
          100% { transform: scale(1); opacity: 1; }
        }
      `}</style>
    </div>
  );
}

export function BreathingBreakButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="group hidden sm:flex items-center gap-1.5 rounded-full bg-primary/10 hover:bg-primary/20 text-primary px-3 py-1.5 text-xs font-semibold transition-all hover:scale-105"
      title="Take a 5-minute breathing break"
    >
      <Wind className="h-3.5 w-3.5 transition-transform group-hover:rotate-12" />
      Take a Break
    </button>
  );
}

export function BreathingBreakIconButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="sm:hidden relative rounded-xl p-2.5 hover:bg-muted transition-colors"
      title="Take a break"
      aria-label="Take a breathing break"
    >
      <Wind className="h-5 w-5" />
    </button>
  );
}
