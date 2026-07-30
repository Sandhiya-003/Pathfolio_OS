import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Sparkles, Send, FileText } from "lucide-react";
import TopBar from "../components/TopBar";
import DocumentModal from "../components/DocumentModal";
import { api, ApiError } from "../lib/api";
import { useToast } from "../context/ToastContext";

const EXAMPLES = [
  "What certificates do I have?",
  "Summarize my internship experience",
  "What skills come up most across my documents?",
  "Which project would be strongest to lead with in an interview?",
];

let msgId = 0;

export default function Assistant() {
  const toast = useToast();
  const [messages, setMessages] = useState([]); // {id, role, content, sources?}
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeDoc, setActiveDoc] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(text) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    const userMsg = { id: ++msgId, role: "user", content: trimmed };
    const history = messages.map((m) => ({ role: m.role, content: m.content }));

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.askAssistant(trimmed, history);
      setMessages((prev) => [
        ...prev,
        { id: ++msgId, role: "assistant", content: res.answer, sources: res.sources },
      ]);
    } catch (e) {
      const message =
        e instanceof ApiError && e.status === 503
          ? e.message
          : "Couldn't reach the assistant. Try again in a moment.";
      setMessages((prev) => [
        ...prev,
        { id: ++msgId, role: "assistant", content: message, isError: true },
      ]);
      if (!(e instanceof ApiError && e.status === 503)) {
        toast.error("Assistant request failed");
      }
    } finally {
      setLoading(false);
    }
  }

  function onSubmit(e) {
    e.preventDefault();
    send(input);
  }

  async function openSource(source) {
    try {
      const doc = await api.getDocument(source.document_id);
      setActiveDoc(doc);
    } catch {
      toast.error("Couldn't open that document");
    }
  }

  return (
    <>
      <TopBar title="Ask your archive" subtitle="A conversation with everything you've ever uploaded" />

      <main className="flex flex-col h-[calc(100vh-73px)] max-w-3xl mx-auto w-full px-4 sm:px-6">
        <div className="flex-1 overflow-y-auto py-6 space-y-5">
          <AnimatePresence>
            {messages.length === 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{ duration: 0.4 }}
                className="card p-6 sm:p-8"
              >
                <motion.span
                  animate={{
                    boxShadow: [
                      "0 0 0px 0px rgba(201,162,78,0.0)",
                      "0 0 16px 2px rgba(201,162,78,0.3)",
                      "0 0 0px 0px rgba(201,162,78,0.0)",
                    ],
                  }}
                  transition={{ repeat: Infinity, duration: 2.6, ease: "easeInOut" }}
                  className="grid place-items-center w-11 h-11 rounded-full border border-seal-gold/50 text-seal-gold mb-4"
                >
                  <Sparkles size={19} />
                </motion.span>
                <h2 className="font-display text-xl text-parchment">
                  Ask anything about your archive
                </h2>
                <p className="text-sm text-parchment-muted mt-1.5 leading-relaxed">
                  The assistant reads your certificates, projects, and internship letters to
                  answer in plain language — and always tells you which documents it used.
                </p>
                <div className="flex flex-wrap gap-2 mt-5">
                  {EXAMPLES.map((ex, i) => (
                    <motion.button
                      key={ex}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.06 }}
                      whileHover={{ scale: 1.03, y: -1 }}
                      whileTap={{ scale: 0.97 }}
                      onClick={() => send(ex)}
                      className="text-sm px-3.5 py-2 rounded-full border border-ink-500 text-parchment-dim hover:border-seal-gold/50 hover:text-seal-gold transition-colors"
                    >
                      {ex}
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <AnimatePresence initial={false}>
            {messages.map((m) => (
              <MessageBubble key={m.id} message={m} onOpenSource={openSource} />
            ))}
          </AnimatePresence>

          <AnimatePresence>
            {loading && (
              <motion.div
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="flex justify-start"
              >
                <div className="bg-ink-800 border border-ink-600 rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1.5">
                  {[0, 1, 2].map((i) => (
                    <motion.span
                      key={i}
                      className="w-1.5 h-1.5 rounded-full bg-seal-gold"
                      animate={{ y: [0, -5, 0], opacity: [0.4, 1, 0.4] }}
                      transition={{ repeat: Infinity, duration: 0.9, delay: i * 0.15, ease: "easeInOut" }}
                    />
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div ref={bottomRef} />
        </div>

        <form onSubmit={onSubmit} className="py-4 border-t border-ink-600">
          <div className="relative">
            <input
              autoFocus
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about your certificates, projects, skills…"
              className="input-field pr-12 py-3.5"
              disabled={loading}
            />
            <motion.button
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.9 }}
              type="submit"
              disabled={loading || !input.trim()}
              className="absolute right-2 top-1/2 -translate-y-1/2 grid place-items-center w-9 h-9 rounded-lg bg-seal-gold text-ink-950 disabled:opacity-40 transition-colors hover:brightness-110"
              aria-label="Send"
            >
              <Send size={15} />
            </motion.button>
          </div>
        </form>
      </main>

      <DocumentModal doc={activeDoc} onClose={() => setActiveDoc(null)} />
    </>
  );
}

function MessageBubble({ message, onOpenSource }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <motion.div
        initial={{ opacity: 0, x: 30, scale: 0.96 }}
        animate={{ opacity: 1, x: 0, scale: 1 }}
        transition={{ type: "spring", stiffness: 400, damping: 30 }}
        className="flex justify-end"
      >
        <div className="max-w-[80%] bg-seal-gold text-ink-950 rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm font-medium">
          {message.content}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -20, scale: 0.97 }}
      animate={{ opacity: 1, x: 0, scale: 1 }}
      transition={{ type: "spring", stiffness: 300, damping: 28 }}
      className="flex justify-start"
    >
      <div
        className={`max-w-[85%] rounded-2xl rounded-tl-sm px-4 py-3 text-sm leading-relaxed ${
          message.isError
            ? "bg-ink-800 border border-seal-coral/40 text-seal-coral"
            : "bg-ink-800 border border-ink-600 text-parchment"
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>

        {message.sources?.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-ink-600">
            {message.sources.map((s, i) => (
              <motion.button
                key={s.document_id}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 + i * 0.06 }}
                whileHover={{ scale: 1.05 }}
                onClick={() => onOpenSource(s)}
                className="stamp inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-full bg-ink-900 border border-ink-500 text-parchment-dim hover:border-seal-gold/50 hover:text-seal-gold transition-colors"
              >
                <FileText size={11} />
                {s.title}
              </motion.button>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}