import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X, Download, GitBranch } from "lucide-react";
import CategoryBadge from "./CategoryBadge";
import { Spinner } from "./Loader";
import { api } from "../lib/api";

export default function DocumentModal({ doc, onClose }) {
  const [related, setRelated] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!doc) return;
    let cancelled = false;
    setLoading(true);
    api
      .getDocumentRelationships(doc.id)
      .then((data) => !cancelled && setRelated(data))
      .catch(() => !cancelled && setRelated(null))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [doc]);

  return (
    <AnimatePresence>
      {doc && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.94, y: 16 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 8, transition: { duration: 0.15 } }}
            transition={{ type: "spring", stiffness: 340, damping: 30 }}
            className="relative w-full max-w-2xl max-h-[85vh] overflow-y-auto card p-6 sm:p-8"
          >
            <button
              onClick={onClose}
              className="absolute right-5 top-5 text-parchment-muted hover:text-parchment"
              aria-label="Close"
            >
              <X size={20} />
            </button>

            <CategoryBadge category={doc.category} size="md" />
            <h2 className="font-display text-2xl sm:text-3xl text-parchment mt-3 leading-tight">
              {doc.title || doc.original_filename}
            </h2>
            <p className="stamp text-parchment-muted mt-2">
              {doc.original_filename} · {doc.date_extracted || "undated"} · doc_id {doc.id?.slice(0, 8)}
            </p>

            {doc.description && (
              <p className="text-sm text-parchment-dim mt-5 leading-relaxed">{doc.description}</p>
            )}

            {doc.skills?.length > 0 && (
              <div className="mt-6">
                <p className="stamp text-parchment-muted mb-2">Skills detected</p>
                <div className="flex flex-wrap gap-1.5">
                  {doc.skills.map((s) => (
                    <span
                      key={s}
                      className="stamp px-2.5 py-1.5 rounded-full bg-ink-700 text-seal-teal border border-seal-teal/30"
                    >
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {doc.organizations?.length > 0 && (
              <div className="mt-5">
                <p className="stamp text-parchment-muted mb-2">Organizations</p>
                <div className="flex flex-wrap gap-1.5">
                  {doc.organizations.map((o) => (
                    <span
                      key={o}
                      className="stamp px-2.5 py-1.5 rounded-full bg-ink-700 text-seal-violet border border-seal-violet/30"
                    >
                      {o}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="mt-7 pt-6 border-t border-ink-600">
              <p className="stamp text-parchment-muted mb-3 flex items-center gap-2">
                <GitBranch size={13} /> Connected documents
              </p>
              {loading ? (
                <div className="flex items-center gap-2 text-parchment-muted text-sm">
                  <Spinner size={14} /> Tracing relationships…
                </div>
              ) : related?.related_documents?.length ? (
                <div className="space-y-2">
                  {related.related_documents.map((r) => (
                    <div
                      key={r.id}
                      className="flex items-center justify-between gap-3 px-3 py-2.5 rounded-lg bg-ink-900 border border-ink-600"
                    >
                      <div className="min-w-0">
                        <p className="text-sm text-parchment truncate">{r.title}</p>
                        <p className="stamp text-parchment-muted">{r.category}</p>
                      </div>
                      <CategoryBadge category={r.category} />
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-parchment-muted">
                  No connections yet — related skills, projects, or internships will surface here as your archive grows.
                </p>
              )}
            </div>

            <button onClick={() => api.downloadDocument(doc.id, doc.original_filename)} className="btn-primary w-full mt-7">
              <Download size={16} /> Download original file
            </button>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}