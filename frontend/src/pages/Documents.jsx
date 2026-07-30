import { useEffect, useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { FolderOpen } from "lucide-react";
import TopBar from "../components/TopBar";
import DocumentCard from "../components/DocumentCard";
import DocumentModal from "../components/DocumentModal";
import EmptyState from "../components/EmptyState";
import { StaggerGrid, StaggerItem } from "../components/Motion";
import { CardSkeleton } from "../components/Loader";
import { CATEGORY_LIST, categoryMeta } from "../lib/categories";
import { api } from "../lib/api";
import { useToast } from "../context/ToastContext";

export default function Documents() {
  const toast = useToast();
  const [docs, setDocs] = useState(null);
  const [category, setCategory] = useState("all");
  const [query, setQuery] = useState("");
  const [activeDoc, setActiveDoc] = useState(null);

  async function load() {
    try {
      const res = await api.listDocuments({ category: category === "all" ? undefined : category });
      setDocs(res.documents);
    } catch {
      toast.error("Couldn't load your archive");
      setDocs([]);
    }
  }

  useEffect(() => {
    setDocs(null);
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [category]);

  async function handleDelete(doc) {
    if (!confirm(`Remove "${doc.title || doc.original_filename}" from your archive?`)) return;
    try {
      await api.deleteDocument(doc.id);
      toast.success("Document removed");
      load();
    } catch {
      toast.error("Couldn't delete that document");
    }
  }

  const filtered = useMemo(() => {
    if (!docs) return null;
    if (!query.trim()) return docs;
    const q = query.toLowerCase();
    return docs.filter(
      (d) =>
        d.title?.toLowerCase().includes(q) ||
        d.original_filename?.toLowerCase().includes(q) ||
        (d.skills || []).some((s) => s.toLowerCase().includes(q))
    );
  }, [docs, query]);

  return (
    <>
      <TopBar title="Archive" subtitle="Every document you've ever ingested, organized automatically" />

      <main className="px-4 sm:px-8 py-8 max-w-7xl mx-auto space-y-6">
        <div className="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
          <div className="flex flex-wrap gap-2">
            <FilterChip active={category === "all"} onClick={() => setCategory("all")}>
              All
            </FilterChip>
            {CATEGORY_LIST.map((c) => {
              const meta = categoryMeta(c);
              return (
                <FilterChip key={c} active={category === c} onClick={() => setCategory(c)} accent={meta.accent}>
                  {meta.emoji} {meta.label}
                </FilterChip>
              );
            })}
          </div>

          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Filter by title or skill…"
            className="input-field sm:w-64"
          />
        </div>

        {filtered === null && (
          <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <CardSkeleton key={i} />
            ))}
          </div>
        )}

        {filtered?.length === 0 && (
          <EmptyState
            icon={FolderOpen}
            title={query || category !== "all" ? "No matches" : "Your archive is empty"}
            detail={
              query || category !== "all"
                ? "Try a different filter or search term."
                : "Upload your first certificate, project, or resume to get started."
            }
            actionLabel={!(query || category !== "all") ? "Ingest a document" : undefined}
            actionTo={!(query || category !== "all") ? "/upload" : undefined}
          />
        )}

        {filtered?.length > 0 && (
          <StaggerGrid className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
            <AnimatePresence>
              {filtered.map((doc) => (
                <StaggerItem key={doc.id}>
                  <DocumentCard doc={doc} onOpen={setActiveDoc} onDelete={handleDelete} />
                </StaggerItem>
              ))}
            </AnimatePresence>
          </StaggerGrid>
        )}
      </main>

      <DocumentModal doc={activeDoc} onClose={() => setActiveDoc(null)} />
    </>
  );
}

function FilterChip({ active, onClick, children, accent = "#C9A24E" }) {
  return (
    <motion.button
      onClick={onClick}
      whileTap={{ scale: 0.96 }}
      className="relative stamp px-3 py-1.5 rounded-full border overflow-hidden"
      style={
        active
          ? { borderColor: accent, color: accent }
          : { borderColor: "#2B2F3F", color: "#9195AA" }
      }
    >
      {active && (
        <motion.span
          layoutId="filter-chip-bg"
          className="absolute inset-0 -z-10"
          style={{ background: `${accent}14` }}
          transition={{ type: "spring", stiffness: 380, damping: 32 }}
        />
      )}
      {children}
    </motion.button>
  );
}