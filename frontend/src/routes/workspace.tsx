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
} from "lucide-react";
import { materials, type Chapter } from "@/data/chapters";
import { RichContent } from "@/components/RichContent";
import { PdfViewer } from "@/components/PdfViewer";
import { StudyNotifications } from "@/components/StudyNotifications";
import { ChatBubble, TypingDots } from "@/components/FloatingBamboo";

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

function fakeReply(prompt: string, chapter?: Chapter): string {
  const p = prompt.toLowerCase();
  const topic = chapter?.name.replace(/^Ch\.\s*\d+\s*—\s*/, "") ?? "this material";
  if (p.includes("simply") || p.includes("simple"))
    return `Sure! ${topic} in plain words: it's about how a transformation acts on space — some directions only get stretched, others get rotated. The "stretch-only" directions are the special ones.`;
  if (p.includes("example"))
    return `Imagine spinning a globe. The axis going through the poles is the eigenvector — every other point rotates, but the poles stay still and only "stretch" along the axis. That's the geometric idea.`;
  if (p.includes("summar"))
    return `Quick summary of ${topic}:\n• Eigenvectors are directions a linear map only scales.\n• Eigenvalues come from solving det(A − λI) = 0.\n• A diagonalizable matrix has a full eigenbasis.`;
  return `Great question. In the context of ${topic}, the short answer is: yes — and the reason is that the determinant condition forces a non-trivial null space, which is exactly where eigenvectors live.`;
}

function WorkspacePage() {
  const [tab, setTab] = useState<"summary" | "quiz" | "explain">("summary");
  const [view, setView] = useState<"reader" | "chat">("reader");
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    linalg: true,
    ml: false,
    physics: false,
  });
  const [activeChapter, setActiveChapter] = useState<string>("la-3");

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const chatScrollRef = useRef<HTMLDivElement>(null);

  const toggle = (id: string) => setExpanded((e) => ({ ...e, [id]: !e[id] }));

  const currentChapter = materials
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

  const sendChat = (textArg?: string) => {
    const text = (textArg ?? chatInput).trim();
    if (!text) return;
    setView("chat");
    setMessages((m) => [...m, { id: crypto.randomUUID(), role: "user", text }]);
    setChatInput("");
    setThinking(true);

    setTimeout(() => {
      const reply = fakeReply(text, currentChapter);
      const id = crypto.randomUUID();
      setThinking(false);
      setMessages((m) => [...m, { id, role: "bamboo", text: "", streaming: true }]);
      const words = reply.split(" ");
      let i = 0;
      const interval = setInterval(() => {
        i++;
        setMessages((m) =>
          m.map((msg) =>
            msg.id === id
              ? { ...msg, text: words.slice(0, i).join(" "), streaming: i < words.length }
              : msg,
          ),
        );
        if (i >= words.length) clearInterval(interval);
      }, 50);
    }, 850);
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
            <button className="text-xs font-semibold text-primary inline-flex items-center gap-1 hover:underline">
              <Upload className="h-3.5 w-3.5" /> Upload
            </button>
          </div>
          <ul className="space-y-1">
            {materials.map((m) => {
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
                                  <span>{c.pages} pages</span>
                                  <span className="rounded-full bg-muted px-1.5 py-0.5 text-[9px] uppercase tracking-wider font-bold">
                                    {c.kind === "pdf" ? "PDF" : c.kind === "mixed" ? "Mixed" : "Text"}
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
            {view === "reader" && currentChapter && (
              <div className="p-6 lg:p-8 flex-1 overflow-y-auto">
                <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
                  <span className="inline-flex items-center gap-1.5">
                    <BookOpen className="h-3.5 w-3.5" /> {currentChapter.pages} pages ·{" "}
                    {currentChapter.kind === "pdf"
                      ? "PDF document"
                      : currentChapter.kind === "mixed"
                        ? "Notes + PDF"
                        : "Study notes"}
                  </span>
                </div>

                {currentChapter.kind === "rich" && currentChapter.blocks && (
                  <RichContent blocks={currentChapter.blocks} />
                )}
                {currentChapter.kind === "pdf" && currentChapter.pdfUrl && (
                  <PdfViewer url={currentChapter.pdfUrl} />
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
                      onClick={() => setMessages([])}
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
                <ul className="space-y-3 text-sm">
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">·</span>
                    Eigenvectors are directions preserved by a linear map (only scaled).
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">·</span>
                    Eigenvalues come from solving the characteristic polynomial.
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">·</span>
                    Diagonalizable matrices have a full basis of eigenvectors.
                  </li>
                </ul>
              )}
              {tab === "quiz" && (
                <div className="space-y-3 text-sm">
                  <div className="font-semibold">Q1. If Av = 5v, then 5 is the …</div>
                  {["eigenvector", "eigenvalue", "determinant"].map((o) => (
                    <button
                      key={o}
                      className="w-full text-left rounded-xl border border-border px-3 py-2 hover:border-primary/50 hover:bg-primary/5 transition"
                    >
                      {o}
                    </button>
                  ))}
                </div>
              )}
              {tab === "explain" && (
                <p className="text-sm leading-relaxed">
                  Think of a globe spinning. The axis that doesn't move is an eigenvector — every
                  other point rotates, but those on the axis only get stretched (or stay still).
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

