import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { useEffect, useRef, useState } from "react";
import {
  FileText,
  Sparkles,
  ListChecks,
  MessageCircleQuestion,
  Send,
  BookOpen,
  Upload,
  ChevronDown,
  ChevronRight,
  FolderOpen,
  Folder,
  MessagesSquare,
  Download,
  Loader2,
} from "lucide-react";
import type { Material } from "@/data/chapters";
import { RichContent } from "@/components/RichContent";
import { PdfViewer } from "@/components/PdfViewer";
import { PptxViewer } from "@/components/PptxViewer";
import { StudyNotifications } from "@/components/StudyNotifications";
import { ChatBubble, TypingDots } from "@/components/FloatingBamboo";
import { corpusFileUrl, deleteSession, fetchCorpusFiles, postChat } from "@/lib/api";
import { buildCorpusMaterial } from "@/lib/corpusWorkspace";

export const Route = createFileRoute("/workspace")({
  head: () => ({
    meta: [
      { title: "Course Workspace — EcoLearn AI" },
      {
        name: "description",
        content:
          "Study your own materials with AI-generated summaries, quizzes and grounded answers.",
      },
      { property: "og:title", content: "Course Workspace — EcoLearn AI" },
      {
        property: "og:description",
        content: "A smart document studio, not a chatbot.",
      },
    ],
  }),
  component: () => (
    <AppLayout>
      <WorkspacePage />
    </AppLayout>
  ),
});

type ChatMessage = { id: string; role: "user" | "bamboo"; text: string; streaming?: boolean };

const CHAT_SUGGESTIONS = [
  "Explain this concept simply",
  "Give me an example",
  "Summarize this page",
];

function chapterKindLabel(kind: string): string {
  if (kind === "download") return "File";
  if (kind === "pdf") return "PDF";
  if (kind === "pptx") return "PPTX";
  if (kind === "mixed") return "Mixed";
  if (kind === "rich") return "Text";
  return kind;
}

function WorkspacePage() {
  const [tab, setTab] = useState<"summary" | "quiz" | "explain">("summary");
  const [view, setView] = useState<"reader" | "chat">("reader");
  const [corpusMaterial, setCorpusMaterial] = useState<ReturnType<typeof buildCorpusMaterial>>(null);
  const [corpusLoading, setCorpusLoading] = useState(true);
  const [corpusError, setCorpusError] = useState<string | null>(null);
  const corpusBootstrapped = useRef(false);

  const workspaceMaterials: Material[] = corpusMaterial ? [corpusMaterial] : [];

  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    corpus: true,
  });
  const [activeChapter, setActiveChapter] = useState<string>("");

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const chatScrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setCorpusLoading(true);
      setCorpusError(null);
      try {
        const res = await fetchCorpusFiles();
        if (cancelled) return;
        const built = buildCorpusMaterial(res.files);
        setCorpusMaterial(built);
        if (built?.chapters[0] && !corpusBootstrapped.current) {
          corpusBootstrapped.current = true;
          setActiveChapter(built.chapters[0].id);
          setView("reader");
        }
      } catch (e) {
        if (!cancelled) setCorpusError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!cancelled) setCorpusLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const toggle = (id: string) => setExpanded((e) => ({ ...e, [id]: !e[id] }));

  const currentChapter = workspaceMaterials
    .flatMap((m) => m.chapters.map((c) => ({ ...c, material: m.name })))
    .find((c) => c.id === activeChapter);

  useEffect(() => {
    if (view === "chat") {
      chatScrollRef.current?.scrollTo({
        top: chatScrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, thinking, view]);

  const sendChat = async (textArg?: string) => {
    const text = (textArg ?? chatInput).trim();
    if (!text) return;
    setView("chat");
    setMessages((m) => [...m, { id: crypto.randomUUID(), role: "user", text }]);
    setChatInput("");
    setThinking(true);

    try {
      const res = await postChat({
        message: text,
        session_id: sessionId,
        course_context: currentChapter
          ? {
              lesson_title: currentChapter.name,
              course_name: currentChapter.material,
              ...(currentChapter.sourceFilename
                ? { allowed_sources: [currentChapter.sourceFilename] }
                : {}),
            }
          : undefined,
      });
      setSessionId(res.session_id);
      const reply =
        res.errors?.length && !res.reply?.trim()
          ? `Error: ${res.errors.join("; ")}`
          : [res.reply, ...(res.warnings?.length ? [`\n\n_${res.warnings.join(" ")}_`] : [])].join(
              "",
            );
      setMessages((m) => [
        ...m,
        { id: crypto.randomUUID(), role: "bamboo", text: reply, streaming: false },
      ]);
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setMessages((m) => [
        ...m,
        {
          id: crypto.randomUUID(),
          role: "bamboo",
          text:
            `Could not reach the AI backend (${msg}). Start: \`uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8001\` (match VITE_API_PROXY_TARGET in frontend/.env.local).`,
          streaming: false,
        },
      ]);
    } finally {
      setThinking(false);
    }
  };

  return (
    <div className="max-w-[1400px] mx-auto">
      <div className="flex items-center justify-between mb-3 gap-4">
        <div className="min-w-0">
          <div className="text-[10px] uppercase tracking-[0.2em] text-primary font-semibold">
            Workspace
          </div>
          <h1 className="font-display text-lg lg:text-xl font-bold truncate leading-tight">
            {currentChapter
              ? `${currentChapter.material} · ${currentChapter.name}`
              : "Workspace"}
          </h1>
        </div>

        {/* Reader / Chat toggle */}
        <div className="flex p-1 bg-muted rounded-2xl shrink-0">
          <button
            onClick={() => setView("reader")}
            className={`inline-flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-semibold transition ${
              view === "reader"
                ? "bg-card shadow-card text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <BookOpen className="h-3.5 w-3.5" /> Reader
          </button>
          <button
            onClick={() => setView("chat")}
            className={`inline-flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-semibold transition ${
              view === "chat"
                ? "bg-card shadow-card text-foreground"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            <MessagesSquare className="h-3.5 w-3.5" /> Chat
            {messages.length > 0 && (
              <span className="ml-0.5 h-4 min-w-4 px-1 rounded-full bg-primary text-primary-foreground text-[10px] font-bold grid place-items-center">
                {messages.length}
              </span>
            )}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-5">
        {/* Materials with expandable chapters */}
        <aside className="col-span-12 lg:col-span-3 rounded-3xl bg-card border border-border p-4 shadow-card h-fit">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-sm">Materials</h3>
            <button
              type="button"
              className="text-xs font-semibold text-primary inline-flex items-center gap-1 hover:underline opacity-60 cursor-not-allowed"
              title="Upload is not wired yet — add files to greenNovation/data and rebuild the index"
            >
              <Upload className="h-3.5 w-3.5" /> Upload
            </button>
          </div>
          {corpusLoading && (
            <div className="flex items-center gap-2 text-xs text-muted-foreground mb-3">
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              Loading your documents…
            </div>
          )}
          {corpusError && (
            <p className="text-[11px] text-muted-foreground mb-3 rounded-lg bg-muted/50 px-2 py-1.5">
              Could not load documents ({corpusError}). Check that the API is running and{" "}
              <code className="text-[10px]">VITE_API_PROXY_TARGET</code> matches its port.
            </p>
          )}
          {!corpusLoading && !corpusError && workspaceMaterials.length === 0 && (
            <p className="text-sm text-muted-foreground mb-3 rounded-xl border border-dashed border-border px-3 py-4">
              No files in your corpus folder yet. Add PDFs to{" "}
              <code className="text-xs bg-muted px-1 rounded">greenNovation/data</code> and refresh, or rebuild the
              index if you add new sources.
            </p>
          )}
          <ul className="space-y-1">
            {workspaceMaterials.map((m) => {
              const open = expanded[m.id];
              return (
                <li key={m.id}>
                  <button
                    onClick={() => toggle(m.id)}
                    className="w-full flex items-center gap-2 rounded-xl px-2.5 py-2 hover:bg-muted transition text-left"
                  >
                    {open ? (
                      <ChevronDown className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    ) : (
                      <ChevronRight className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    )}
                    {open ? (
                      <FolderOpen className="h-4 w-4 text-primary shrink-0" />
                    ) : (
                      <Folder className="h-4 w-4 text-primary shrink-0" />
                    )}
                    <span className="text-sm font-semibold truncate">{m.name}</span>
                    <span className="ml-auto text-[10px] text-muted-foreground font-medium">
                      {m.chapters.length}
                    </span>
                  </button>
                  {open && (
                    <ul className="ml-4 mt-1 mb-2 space-y-0.5 border-l border-border pl-2">
                      {m.chapters.map((c) => {
                        const active = activeChapter === c.id;
                        return (
                          <li key={c.id}>
                            <button
                              onClick={() => {
                                setActiveChapter(c.id);
                                setView("reader");
                              }}
                              className={`w-full text-left rounded-lg px-2.5 py-2 flex items-start gap-2 transition ${
                                active
                                  ? "bg-primary/10 border border-primary/30"
                                  : "hover:bg-muted border border-transparent"
                              }`}
                            >
                              <FileText
                                className={`h-3.5 w-3.5 mt-0.5 shrink-0 ${
                                  active ? "text-primary" : "text-muted-foreground"
                                }`}
                              />
                              <div className="min-w-0 flex-1">
                                <div className="text-xs font-medium truncate">{c.name}</div>
                                <div className="text-[10px] text-muted-foreground flex items-center gap-1.5">
                                  {c.pages > 0 ? <span>{c.pages} pages</span> : <span>·</span>}
                                  <span className="rounded-full bg-muted px-1.5 py-0.5 text-[9px] uppercase tracking-wider font-bold">
                                    {chapterKindLabel(c.kind)}
                                  </span>
                                </div>
                              </div>
                            </button>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </li>
              );
            })}
          </ul>
        </aside>

        {/* Reader / Chat panel + aligned sticky chat bar */}
        <div className="col-span-12 lg:col-span-6 flex flex-col gap-2 h-[calc(100vh-9rem)]">
          <section className="rounded-3xl bg-card border border-border shadow-card overflow-hidden flex flex-col flex-1 min-h-0">
            {view === "reader" && !currentChapter && (
              <div className="p-6 lg:p-8 flex-1 overflow-y-auto grid place-items-center min-h-[280px]">
                <div className="text-center text-sm text-muted-foreground max-w-sm">
                  <BookOpen className="h-10 w-10 mx-auto mb-3 text-primary/40" />
                  <p>Select a document from Materials, or add files to your data folder and reload.</p>
                </div>
              </div>
            )}

            {view === "reader" && currentChapter && (
              <div className="p-6 lg:p-8 flex-1 overflow-y-auto min-w-0">
                <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
                  <span className="inline-flex items-center gap-1.5">
                    <BookOpen className="h-3.5 w-3.5" />
                    {currentChapter.pages > 0 ? `${currentChapter.pages} pages · ` : ""}
                    {currentChapter.kind === "pdf"
                      ? "PDF document"
                      : currentChapter.kind === "pptx"
                        ? "PowerPoint"
                        : currentChapter.kind === "mixed"
                          ? "Notes + PDF"
                          : currentChapter.kind === "download"
                            ? "Download to open locally"
                            : "Study notes"}
                  </span>
                </div>

                {currentChapter.kind === "rich" && currentChapter.blocks && (
                  <RichContent blocks={currentChapter.blocks} />
                )}
                {currentChapter.kind === "pdf" && currentChapter.pdfUrl && (
                  <PdfViewer url={currentChapter.pdfUrl} />
                )}
                {currentChapter.kind === "pptx" && currentChapter.pptxUrl && (
                  <PptxViewer url={currentChapter.pptxUrl} downloadName={currentChapter.name} />
                )}
                {currentChapter.kind === "download" && currentChapter.sourceFilename && (
                  <div className="rounded-2xl border border-border bg-muted/30 p-6 text-center space-y-4">
                    <Download className="h-10 w-10 mx-auto text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">
                      This file type is not shown in the browser. Download it to open with the right app (e.g. PowerPoint).
                    </p>
                    <a
                      href={corpusFileUrl(currentChapter.sourceFilename)}
                      download={currentChapter.sourceFilename}
                      className="inline-flex items-center justify-center rounded-xl gradient-primary text-primary-foreground px-4 py-2.5 text-sm font-semibold shadow-glow hover:opacity-95"
                    >
                      Download {currentChapter.name}
                    </a>
                  </div>
                )}
                {currentChapter.kind === "mixed" && (
                  <div className="space-y-6">
                    {currentChapter.blocks && <RichContent blocks={currentChapter.blocks} />}
                    {currentChapter.pdfUrl && (
                      <div>
                        <div className="text-[10px] uppercase tracking-widest font-bold text-muted-foreground mb-2">
                          Source paper
                        </div>
                        <PdfViewer url={currentChapter.pdfUrl} />
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {view === "chat" && (
              <div className="flex flex-col h-full">
                <div className="px-6 py-4 border-b border-border flex items-center justify-between">
                  <div>
                    <div className="text-[10px] uppercase tracking-widest font-bold text-primary">
                      Chat · grounded in {currentChapter?.name ?? "your material"}
                    </div>
                    <div className="font-display text-lg font-bold">Discuss this chapter</div>
                  </div>
                  {messages.length > 0 && (
                    <button
                      onClick={() => {
                        if (sessionId) void deleteSession(sessionId);
                        setSessionId(null);
                        setMessages([]);
                      }}
                      className="text-xs font-semibold text-muted-foreground hover:text-foreground"
                    >
                      Clear
                    </button>
                  )}
                </div>
                <div ref={chatScrollRef} className="flex-1 overflow-y-auto p-6 space-y-3 min-h-0">
                  {messages.length === 0 && !thinking && (
                    <div className="grid place-items-center h-full text-center text-sm text-muted-foreground py-12">
                      <div>
                        <MessagesSquare className="h-8 w-8 mx-auto mb-2 text-primary/50" />
                        Ask anything about this chapter to get started.
                      </div>
                    </div>
                  )}
                  {messages.map((m) => (
                    <ChatBubble key={m.id} role={m.role} text={m.text} streaming={m.streaming} />
                  ))}
                  {thinking && <TypingDots />}
                </div>
              </div>
            )}
          </section>

          {/* Chat bar — aligned under reader, compact */}
          <div className="z-30">
            <div className="rounded-2xl bg-card/95 backdrop-blur-xl border border-border shadow-glow p-2">
              {view === "chat" && (
                <div className="flex gap-2 mb-2 overflow-x-auto px-1">
                  {CHAT_SUGGESTIONS.map((s) => (
                    <button
                      key={s}
                      onClick={() => sendChat(s)}
                      className="shrink-0 text-[11px] font-medium rounded-full border border-border bg-muted/40 px-2.5 py-1 hover:border-primary/50 hover:bg-primary/5 transition"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  sendChat();
                }}
                className="flex items-center gap-2 rounded-xl border border-border bg-background px-2.5 py-1 focus-within:border-ring focus-within:ring-2 focus-within:ring-ring/20 transition"
              >
                <MessagesSquare className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                <input
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder={`Ask Bamboo about ${currentChapter?.name ?? "this material"}…`}
                  className="flex-1 bg-transparent px-1 py-1 text-sm focus:outline-none"
                />
                <button
                  type="submit"
                  disabled={!chatInput.trim()}
                  aria-label="Send"
                  className="h-7 w-7 rounded-lg gradient-primary grid place-items-center text-primary-foreground hover:scale-105 transition disabled:opacity-50"
                >
                  <Send className="h-3.5 w-3.5" />
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* AI tools + notifications */}
        <aside className="col-span-12 lg:col-span-3 space-y-4">
          <div className="rounded-3xl bg-card border border-border shadow-card overflow-hidden">
            <div className="flex p-1 bg-muted/60">
              {(
                [
                  { id: "summary", label: "Summary", icon: Sparkles },
                  { id: "quiz", label: "Quiz", icon: ListChecks },
                  { id: "explain", label: "Explain", icon: MessageCircleQuestion },
                ] as const
              ).map((t) => (
                <button
                  key={t.id}
                  onClick={() => setTab(t.id)}
                  className={`flex-1 inline-flex items-center justify-center gap-1.5 rounded-xl px-2 py-2 text-xs font-semibold transition ${
                    tab === t.id
                      ? "bg-card shadow-card text-foreground"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  <t.icon className="h-3.5 w-3.5" />
                  {t.label}
                </button>
              ))}
            </div>
            <div className="p-5">
              {tab === "summary" && (
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Ask for a summary in chat — it will use your selected document and the course index when the API is
                  running.
                </p>
              )}
              {tab === "quiz" && (
                <p className="text-sm text-muted-foreground leading-relaxed">
                  For practice questions, use chat with prompts like “give me quiz questions on this PDF”. The tutor
                  answers from your indexed materials.
                </p>
              )}
              {tab === "explain" && (
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Use chat to request a simpler explanation of a passage or concept from the document you have open.
                </p>
              )}
            </div>
          </div>

          <StudyNotifications />
        </aside>
      </div>
    </div>
  );
}

