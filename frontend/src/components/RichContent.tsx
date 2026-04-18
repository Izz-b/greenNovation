import { Highlighter, Info, AlertTriangle, Lightbulb } from "lucide-react";
import { useState } from "react";
import type { RichBlock } from "@/data/chapters";

const calloutStyles: Record<"info" | "warn" | "tip", { wrap: string; icon: typeof Info }> = {
  info: { wrap: "bg-secondary/60 border-secondary text-secondary-foreground", icon: Info },
  warn: { wrap: "bg-warning/15 border-warning/30 text-warning-foreground", icon: AlertTriangle },
  tip: { wrap: "bg-primary/10 border-primary/25 text-foreground", icon: Lightbulb },
};

export function RichContent({ blocks }: { blocks: RichBlock[] }) {
  const [highlight, setHighlight] = useState(false);

  return (
    <div className={highlight ? "[&_p]:bg-warning/10 [&_p]:transition-colors" : ""}>
      <div className="flex items-center justify-end mb-3">
        <button
          onClick={() => setHighlight((h) => !h)}
          className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-semibold transition ${
            highlight
              ? "bg-warning text-warning-foreground"
              : "bg-warning/15 text-warning-foreground hover:bg-warning/25"
          }`}
        >
          <Highlighter className="h-3 w-3" />
          {highlight ? "Highlighting on" : "Highlight"}
        </button>
      </div>

      <article className="space-y-4">
        {blocks.map((b, i) => {
          if (b.type === "h2")
            return (
              <h2 key={i} className="font-display text-2xl font-bold mt-2">
                {b.text}
              </h2>
            );
          if (b.type === "h3")
            return (
              <h3 key={i} className="font-display text-lg font-semibold mt-4">
                {b.text}
              </h3>
            );
          if (b.type === "p")
            return (
              <p key={i} className="text-sm text-foreground/85 leading-relaxed">
                {b.text}
              </p>
            );
          if (b.type === "definition")
            return (
              <div key={i} className="rounded-2xl border-l-4 border-primary bg-primary/5 px-4 py-3">
                <div className="text-[10px] uppercase tracking-widest font-bold text-primary">
                  Definition
                </div>
                <div className="font-semibold text-sm mt-0.5">{b.term}</div>
                <p className="text-sm text-foreground/80 mt-1 leading-relaxed">{b.body}</p>
              </div>
            );
          if (b.type === "example")
            return (
              <div key={i} className="rounded-2xl bg-muted/60 p-4 border border-border">
                <div className="text-[10px] uppercase tracking-widest font-bold text-muted-foreground mb-1">
                  {b.title}
                </div>
                <p className="text-sm">{b.body}</p>
              </div>
            );
          if (b.type === "callout") {
            const cfg = calloutStyles[b.tone];
            const Icon = cfg.icon;
            return (
              <div key={i} className={`rounded-2xl border p-3.5 flex items-start gap-2.5 ${cfg.wrap}`}>
                <Icon className="h-4 w-4 mt-0.5 shrink-0" />
                <p className="text-sm leading-relaxed">{b.body}</p>
              </div>
            );
          }
          return null;
        })}
      </article>
    </div>
  );
}
