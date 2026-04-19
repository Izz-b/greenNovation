import type { ReactNode } from "react";

export function PageHeader({
  eyebrow,
  title,
  description,
  actions,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-8 animate-[fade-in-up_0.5s_ease-out]">
      <div>
        {eyebrow && (
          <div className="text-xs uppercase tracking-[0.2em] text-primary font-semibold mb-2">
            {eyebrow}
          </div>
        )}
        <h1 className="font-display text-3xl lg:text-4xl font-bold tracking-tight">{title}</h1>
        {description && (
          <p className="text-muted-foreground mt-2 max-w-2xl">{description}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}
