import { useEffect, useRef, useState } from "react";
import { Send, X, Sparkles } from "lucide-react";
import { Panda } from "@/components/PandaCompanion";

type Message = { id: string; role: "user" | "bamboo"; text: string; streaming?: boolean };

const SUGGESTIONS = [
  "What should I study today?",
  "How's my focus this week?",
  "Tell me a fun eco fact",
];

const REPLIES = [
  "Great question! Based on your last session, I'd start with eigenvectors — you were on a roll. 🌱",
  "You've been focused for 3.5h this week. Beautiful consistency — the forest is loving it.",
  "Bamboo grows up to 91 cm in a single day. Some species are technically the fastest plants on Earth! 🌿",
  "Try a 25-minute focus block, then I'll quiz you. Sound good?",
];

function pickReply(text: string) {
  const t = text.toLowerCase();
  if (t.includes("study") || t.includes("today")) return REPLIES[0];
  if (t.includes("focus") || t.includes("week")) return REPLIES[1];
  if (t.includes("eco") || t.includes("fact") || t.includes("fun")) return REPLIES[2];
  return REPLIES[3];
}

export function FloatingBamboo() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "bamboo",
      text: "Hi! I'm Bamboo 🐼 your study companion. Ask me anything — I'll keep it short and useful.",
    },
  ]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState(false);
  const [bamboomood, setBamboomood] = useState<"waving" | "reading">("waving");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, thinking]);

  // ESC to close
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  const send = (textArg?: string) => {
    const text = (textArg ?? input).trim();
    if (!text) return;
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", text };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setThinking(true);
    setBamboomood("reading");

    setTimeout(() => {
      const reply = pickReply(text);
      const id = crypto.randomUUID();
      setThinking(false);
      setMessages((m) => [...m, { id, role: "bamboo", text: "", streaming: true }]);

      // word-by-word streaming
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
        if (i >= words.length) {
          clearInterval(interval);
          setBamboomood("waving");
        }
      }, 55);
    }, 900);
  };

  return (
    <>
      {/* Floating bubble */}
      <button
        onClick={() => setOpen(true)}
        aria-label="Open Bamboo assistant"
        className={`fixed bottom-6 right-6 z-40 h-16 w-16 rounded-full gradient-primary shadow-glow grid place-items-center transition-all duration-300 hover:scale-110 active:scale-95 ${
          open ? "opacity-0 scale-75 pointer-events-none" : "opacity-100 scale-100"
        }`}
        style={{ animation: "bamboo-breathe 3.5s ease-in-out infinite" }}
      >
        <div className="absolute inset-0 rounded-full bg-primary/30 animate-ping opacity-40" />
        <div className="relative h-12 w-12 rounded-full bg-card/40 grid place-items-center overflow-hidden">
          <Panda mood="reading" size={44} />
        </div>
        <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-warning grid place-items-center ring-2 ring-background">
          <Sparkles className="h-2.5 w-2.5 text-warning-foreground" />
        </span>
      </button>

      {/* Modal */}
      {open && (
        <div
          className="fixed inset-0 z-50 grid place-items-center p-4 animate-[fade-in-up_0.25s_ease-out]"
          onClick={() => setOpen(false)}
        >
          {/* glass backdrop */}
          <div className="absolute inset-0 bg-foreground/30 backdrop-blur-md" />

          <div
            className="relative w-full max-w-lg max-h-[80vh] flex flex-col rounded-3xl bg-card border border-border shadow-glow overflow-hidden"
            style={{ animation: "scale-in 0.25s cubic-bezier(0.34, 1.56, 0.64, 1)" }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="relative gradient-forest p-5 border-b border-border">
              <div className="flex items-start gap-4">
                <div className="h-16 w-16 rounded-2xl bg-card/60 grid place-items-center shrink-0">
                  <Panda mood={bamboomood} size={56} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-bold uppercase tracking-widest text-primary">
                    Bamboo · Online
                  </div>
                  <div className="font-display text-xl font-bold mt-0.5">
                    Hey there! Need a hand?
                  </div>
                  <div className="text-xs text-muted-foreground mt-0.5">
                    I learn from your sessions and grow with you 🌱
                  </div>
                </div>
                <button
                  onClick={() => setOpen(false)}
                  className="rounded-lg p-2 hover:bg-card/60 transition shrink-0"
                  aria-label="Close"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-5 space-y-3 min-h-[240px]">
              {messages.map((m) => (
                <ChatBubble key={m.id} role={m.role} text={m.text} streaming={m.streaming} />
              ))}
              {thinking && <TypingDots />}
            </div>

            {/* Suggestions */}
            <div className="px-4 pt-2 pb-1 flex gap-2 flex-wrap">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="text-xs font-medium rounded-full border border-border bg-muted/40 px-3 py-1.5 hover:border-primary/50 hover:bg-primary/5 transition"
                >
                  {s}
                </button>
              ))}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-border">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  send();
                }}
                className="flex items-center gap-2 rounded-2xl border border-border bg-background p-2 focus-within:border-ring transition"
              >
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  className="flex-1 bg-transparent px-2 py-1.5 text-sm focus:outline-none"
                  placeholder="Ask Bamboo..."
                  autoFocus
                />
                <button
                  type="submit"
                  className="h-9 w-9 rounded-xl gradient-primary grid place-items-center text-primary-foreground hover:scale-105 transition disabled:opacity-50"
                  disabled={!input.trim()}
                >
                  <Send className="h-4 w-4" />
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes bamboo-breathe {
          0%, 100% { transform: translateY(0) scale(1); }
          50% { transform: translateY(-4px) scale(1.04); }
        }
        @keyframes scale-in {
          0% { transform: scale(0.85); opacity: 0; }
          100% { transform: scale(1); opacity: 1; }
        }
      `}</style>
    </>
  );
}

export function ChatBubble({
  role,
  text,
  streaming,
}: {
  role: "user" | "bamboo";
  text: string;
  streaming?: boolean;
}) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} animate-[fade-in-up_0.25s_ease-out]`}>
      <div
        className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? "bg-primary text-primary-foreground rounded-br-md"
            : "bg-muted text-foreground rounded-bl-md"
        }`}
      >
        {text}
        {streaming && <span className="inline-block w-1.5 h-4 align-middle ml-0.5 bg-current animate-pulse" />}
      </div>
    </div>
  );
}

export function TypingDots() {
  return (
    <div className="flex justify-start animate-[fade-in-up_0.2s_ease-out]">
      <div className="bg-muted rounded-2xl rounded-bl-md px-4 py-3 flex items-center gap-1.5">
        <span className="h-2 w-2 rounded-full bg-muted-foreground/60 animate-bounce" style={{ animationDelay: "0ms" }} />
        <span className="h-2 w-2 rounded-full bg-muted-foreground/60 animate-bounce" style={{ animationDelay: "150ms" }} />
        <span className="h-2 w-2 rounded-full bg-muted-foreground/60 animate-bounce" style={{ animationDelay: "300ms" }} />
      </div>
    </div>
  );
}
