import { useEffect, useState, type ComponentType } from "react";
import { Loader2 } from "lucide-react";

type Props = { url: string; downloadName: string };

/**
 * SSR-safe: loads @aiden0z/pptx-renderer only in the browser (DOM + zip parsing).
 */
export function PptxViewer(props: Props) {
  const [Inner, setInner] = useState<ComponentType<Props> | null>(null);

  useEffect(() => {
    void import("./PptxViewerInner").then((m) => setInner(() => m.PptxViewerInner));
  }, []);

  if (!Inner) {
    return (
      <div className="rounded-2xl bg-muted/40 border border-border p-8 grid place-items-center min-h-[280px] text-muted-foreground">
        <div className="flex items-center gap-2 text-sm">
          <Loader2 className="h-5 w-5 animate-spin" /> Preparing slide viewer…
        </div>
      </div>
    );
  }

  return <Inner {...props} />;
}
