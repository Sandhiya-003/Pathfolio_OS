import { motion } from "framer-motion";
import { Download, Trash2, ExternalLink } from "lucide-react";
import CategoryBadge from "./CategoryBadge";
import { api } from "../lib/api";

export default function DocumentCard({ doc, onOpen, onDelete }) {
  const skills = doc.skills || [];
  const date = doc.date_extracted || doc.created_at?.slice(0, 10);

  return (
    <motion.div
      whileHover={{ y: -4, transition: { duration: 0.2, ease: "easeOut" } }}
      className="card group relative p-5 flex flex-col gap-4 hover:border-seal-gold/40 hover:shadow-lg transition-colors h-full"
    >
      <div className="flex items-start justify-between gap-3">
        <CategoryBadge category={doc.category} />
        <span className="stamp text-parchment-muted">{date || "undated"}</span>
      </div>

      <button
        onClick={() => onOpen?.(doc)}
        className="text-left"
      >
        <h3 className="font-display text-lg text-parchment leading-snug line-clamp-2 group-hover:text-seal-gold transition">
          {doc.title || doc.original_filename}
        </h3>
        <p className="text-xs text-parchment-muted mt-1 font-mono truncate">
          {doc.original_filename}
        </p>
      </button>

      {skills.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {skills.slice(0, 4).map((s) => (
            <span
              key={s}
              className="stamp px-2 py-1 rounded-full bg-ink-700 text-seal-teal border border-seal-teal/30"
            >
              {s}
            </span>
          ))}
          {skills.length > 4 && (
            <span className="stamp px-2 py-1 rounded-full bg-ink-700 text-parchment-muted">
              +{skills.length - 4}
            </span>
          )}
        </div>
      )}

      <div className="flex items-center gap-2 pt-1 border-t border-ink-600 -mx-5 px-5 mt-auto">
        <button
          onClick={() => api.downloadDocument(doc.id, doc.original_filename)}
          className="flex-1 mt-3 btn-secondary py-2 text-xs"
        >
          <Download size={14} /> Original
        </button>
        <button
          onClick={() => onOpen?.(doc)}
          className="mt-3 btn-secondary py-2 px-3 text-xs"
          aria-label="Open details"
        >
          <ExternalLink size={14} />
        </button>
        <button
          onClick={() => onDelete?.(doc)}
          className="mt-3 btn-secondary py-2 px-3 text-xs hover:!border-seal-coral/60 hover:!text-seal-coral"
          aria-label="Delete document"
        >
          <Trash2 size={14} />
        </button>
      </div>
    </motion.div>
  );
}