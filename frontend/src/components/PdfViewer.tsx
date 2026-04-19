import { useEffect, useState, type ComponentType } from "react";
import { Loader2 } from "lucide-react";

/**
 * SSR-safe wrapper: react-pdf / pdf.js use browser APIs (and newer JS) that break in Node during SSR.
 * The heavy viewer loads only after mount in the browser.
 */
export function PdfViewer({ url }: { url: string }) {
  const [Inner, setInner] = useState<ComponentType<{ url: string }> | null>(null);

  useEffect(() => {
    void import("./PdfViewerInner").then((m) => setInner(() => m.PdfViewerInner));
  }, []);

  if (!Inner) {
    return (
      <div className="rounded-2xl bg-muted/40 border border-border p-8 grid place-items-center min-h-[320px] text-muted-foreground">
        <div className="flex items-center gap-2 text-sm">
          <Loader2 className="h-5 w-5 animate-spin" /> Preparing PDF viewer…
        </div>
      </div>
    );
  }

  return <Inner url={url} />;
}
