import { useEffect, useRef, useState } from "react";
import type { PptxViewer } from "@aiden0z/pptx-renderer";
import { ChevronLeft, ChevronRight, Download, Loader2 } from "lucide-react";

type Props = { url: string; downloadName: string };

/**
 * Client-only: @aiden0z/pptx-renderer uses DOM + SVG (+ pdf.js for some assets). Not imported during SSR.
 * `fitMode: 'contain'` scales to the mount element’s `clientWidth` (omit `width` so ResizeObserver works).
 */
export function PptxViewerInner({ url, downloadName }: Props) {
  const mountRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<PptxViewer | null>(null);

  const [slide, setSlide] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const ac = new AbortController();
    let cancelled = false;

    const run = async () => {
      setLoading(true);
      setError(null);
      viewerRef.current?.destroy();
      viewerRef.current = null;

      try {
        const { PptxViewer } = await import("@aiden0z/pptx-renderer");
        if (cancelled) return;

        const res = await fetch(url, { signal: ac.signal, credentials: "same-origin" });
        if (!res.ok) throw new Error(`Could not load file (${res.status})`);
        const buffer = await res.arrayBuffer();
        if (cancelled) return;

        // Do not pass `width`: the library only enables ResizeObserver + refit when width is omitted.
        // A stale width here caused half-width layout and overflow clipping.
        await new Promise<void>((r) => requestAnimationFrame(() => r()));

        const viewer = await PptxViewer.open(buffer, mount, {
          fitMode: "contain",
          renderMode: "slide",
          signal: ac.signal,
          onSlideChange: (index) => setSlide(index + 1),
        });

        if (cancelled) {
          viewer.destroy();
          return;
        }

        viewerRef.current = viewer;
        const n = viewer.slideCount;
        setTotal(n);
        setSlide(Math.min(viewer.currentSlideIndex + 1, Math.max(1, n)));
      } catch (e) {
        if (cancelled) return;
        if (e instanceof DOMException && e.name === "AbortError") return;
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    void run();

    return () => {
      cancelled = true;
      ac.abort();
      viewerRef.current?.destroy();
      viewerRef.current = null;
    };
  }, [url]);

  const goPrev = async () => {
    const v = viewerRef.current;
    if (!v || v.currentSlideIndex <= 0) return;
    try {
      await v.goToSlide(v.currentSlideIndex - 1);
    } catch {
      /* ignore */
    }
  };

  const goNext = async () => {
    const v = viewerRef.current;
    if (!v || v.currentSlideIndex >= v.slideCount - 1) return;
    try {
      await v.goToSlide(v.currentSlideIndex + 1);
    } catch {
      /* ignore */
    }
  };

  if (error) {
    return (
      <div className="rounded-2xl border border-border bg-muted/30 p-6 text-center space-y-4">
        <p className="text-sm text-destructive">{error}</p>
        <p className="text-xs text-muted-foreground">
          You can still download the file and open it in PowerPoint or LibreOffice.
        </p>
        <a
          href={url}
          download={downloadName}
          className="inline-flex items-center justify-center gap-2 rounded-xl gradient-primary text-primary-foreground px-4 py-2.5 text-sm font-semibold shadow-glow hover:opacity-95"
        >
          <Download className="h-4 w-4" />
          Download {downloadName}
        </a>
      </div>
    );
  }

  return (
    <div className="rounded-2xl bg-muted/40 border border-border p-2 lg:p-4">
      <div
        id="pptx-viewer-container"
        className="relative w-full min-w-0 min-h-[min(70vh,600px)] flex flex-col items-stretch"
      >
        {loading && (
          <div className="absolute inset-0 z-10 grid place-items-center rounded-xl bg-background/70">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-5 w-5 animate-spin" /> Loading presentation…
            </div>
          </div>
        )}
        <div
          ref={mountRef}
          className="w-full min-w-0 flex-1 min-h-[min(65vh,560px)]"
        />
      </div>

      {total > 0 && (
        <div className="flex items-center justify-between mt-3 px-2">
          <button
            type="button"
            disabled={loading || slide <= 1}
            onClick={() => void goPrev()}
            className="inline-flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-semibold hover:bg-card disabled:opacity-40 transition"
          >
            <ChevronLeft className="h-4 w-4" /> Prev
          </button>
          <div className="text-xs text-muted-foreground font-medium">
            Slide {slide} of {total}
          </div>
          <button
            type="button"
            disabled={loading || slide >= total}
            onClick={() => void goNext()}
            className="inline-flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-semibold hover:bg-card disabled:opacity-40 transition"
          >
            Next <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}
