import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Search as SearchIcon, Sparkles } from "lucide-react";
import TopBar from "../components/TopBar";
import CategoryBadge from "../components/CategoryBadge";
import DocumentModal from "../components/DocumentModal";
import { PageLoader } from "../components/Loader";
import { StaggerGrid, StaggerItem } from "../components/Motion";
import { api } from "../lib/api";
import { useToast } from "../context/ToastContext";

const EXAMPLES = [
  "Show all my certificates",
  "Show my AI projects",
  "Show internship documents",
  "Show my latest resume",
  "Documents about leadership",
];

const easeOut = [0.16, 1, 0.3, 1];

export default function Search() {
  const toast = useToast();
  const [params, setParams] = useSearchParams();
  const [q, setQ] = useState(params.get("q") || "");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeDoc, setActiveDoc] = useState(null);

  async function runSearch(query) {
    if (!query.trim()) return;
    setLoading(true);
    setParams({ q: query });
    try {
      const res = await api.search(query, { limit: 15 });
      setResult(res);
    } catch {
      toast.error("Search failed — try again");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const initial = params.get("q");
    if (initial) runSearch(initial);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function onSubmit(e) {
    e.preventDefault();
    runSearch(q);
  }

  async function openResult(r) {
    try {
      const doc = await api.getDocument(r.document_id);
      setActiveDoc(doc);
    } catch {
      toast.error("Couldn't open that document");
    }
  }

  return (
    <>
      <TopBar title="Retrieve" subtitle="Ask for anything in plain language — no folders required" />

      <main className="px-4 sm:px-8 py-8 max-w-4xl mx-auto space-y-8">
        <motion.form
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: easeOut }}
          onSubmit={onSubmit}
          className="relative"
        >
          <SearchIcon size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-parchment-muted" />
          <input
            autoFocus
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="e.g. Show all my certificates from 2024"
            className="input-field pl-11 pr-28 py-4 text-base"
          />
          <motion.button
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 0.96 }}
            type="submit"
            className="btn-primary absolute right-2 top-1/2 -translate-y-1/2 py-2"
          >
            Search
          </motion.button>
        </motion.form>

        <AnimatePresence mode="wait">
          {!result && !loading && (
            <motion.div
              key="examples"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25 }}
            >
              <p className="stamp text-parchment-muted mb-3">Try asking</p>
              <div className="flex flex-wrap gap-2">
                {EXAMPLES.map((ex, i) => (
                  <motion.button
                    key={ex}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.05 }}
                    whileHover={{ scale: 1.03, y: -1 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => {
                      setQ(ex);
                      runSearch(ex);
                    }}
                    className="text-sm px-3.5 py-2 rounded-full border border-ink-500 text-parchment-dim hover:border-seal-gold/50 hover:text-seal-gold transition-colors"
                  >
                    {ex}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {loading && <PageLoader label="Searching your knowledge base…" />}

        <AnimatePresence>
          {result && !loading && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35, ease: easeOut }}
              className="space-y-5"
            >
              <div className="flex items-center justify-between">
                {result.low_confidence ? (
                  <p className="text-sm text-seal-coral">
                    Nothing matched well — showing the closest document I could find for{" "}
                    <span className="text-parchment">"{result.query}"</span>
                    <span className="stamp ml-2">{result.processing_time_ms}ms</span>
                  </p>
                ) : (
                  <p className="text-sm text-parchment-muted">
                    {result.total_results} result{result.total_results === 1 ? "" : "s"} for{" "}
                    <span className="text-parchment">"{result.query}"</span>
                    <span className="stamp ml-2">{result.processing_time_ms}ms</span>
                  </p>
                )}
              </div>

              {result.total_results === 0 && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.97 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="card p-8 text-center"
                >
                  <p className="text-parchment-dim">
                    Nothing matched yet. Documents need to be ingested before they're searchable.
                  </p>
                </motion.div>
              )}

              <StaggerGrid className="space-y-3">
                {result.results.map((r) => (
                  <StaggerItem key={r.document_id}>
                    <motion.button
                      onClick={() => openResult(r)}
                      whileHover={{ y: -2, transition: { duration: 0.15 } }}
                      className="card w-full text-left p-5 hover:border-seal-gold/40 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div className="flex items-center gap-2 mb-1.5">
                            <CategoryBadge category={r.category} />
                            {r.date && <span className="stamp text-parchment-muted">{r.date}</span>}
                          </div>
                          <h3 className="font-display text-lg text-parchment">{r.title}</h3>
                          <p className="text-sm text-parchment-muted mt-1.5 line-clamp-2">{r.snippet}</p>
                        </div>
                        <span className="stamp text-seal-gold shrink-0">
                          {Math.round((r.similarity_score || 0) * 100)}% match
                        </span>
                      </div>
                    </motion.button>
                  </StaggerItem>
                ))}
              </StaggerGrid>

              {result.suggestions?.length > 0 && (
                <div className="pt-2">
                  <p className="stamp text-parchment-muted mb-2 flex items-center gap-1.5">
                    <Sparkles size={12} /> Related searches
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {result.suggestions.map((s, i) => (
                      <motion.button
                        key={s}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.05 }}
                        whileHover={{ scale: 1.03, y: -1 }}
                        whileTap={{ scale: 0.97 }}
                        onClick={() => {
                          setQ(s);
                          runSearch(s);
                        }}
                        className="text-sm px-3.5 py-2 rounded-full border border-ink-500 text-parchment-dim hover:border-seal-gold/50 hover:text-seal-gold transition-colors"
                      >
                        {s}
                      </motion.button>
                    ))}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <DocumentModal doc={activeDoc} onClose={() => setActiveDoc(null)} />
    </>
  );
}