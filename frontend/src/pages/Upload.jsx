import { useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { UploadCloud, FileText, CheckCircle2, XCircle, Loader2, ArrowRight, X } from "lucide-react";
import TopBar from "../components/TopBar";
import CategoryBadge from "../components/CategoryBadge";
import ParticleField from "../components/ParticleField";
import { useUploadQueue } from "../context/UploadQueueContext";
import { Link } from "react-router-dom";

const ACCEPTED = [".pdf", ".docx", ".doc", ".txt", ".png", ".jpg", ".jpeg"];
const easeOut = [0.16, 1, 0.3, 1];

export default function Upload() {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);
  const { queue, addFiles, clearItem } = useUploadQueue();

  function onDrop(e) {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer.files?.length) addFiles(e.dataTransfer.files);
  }

  const doneCount = queue.filter((q) => q.status === "done").length;

  return (
    <>
      <TopBar title="Ingest" subtitle="Drop in a document — AI reads, classifies, and connects it automatically" />

      <main className="px-4 sm:px-8 py-8 max-w-5xl mx-auto space-y-8">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, ease: easeOut }}
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          onClick={() => inputRef.current?.click()}
          whileHover={{ scale: 1.005 }}
          className={`relative overflow-hidden card border-2 border-dashed cursor-pointer px-8 py-16 flex flex-col items-center text-center gap-4 transition-colors ${
            dragging ? "border-seal-gold bg-ink-700/60" : "border-ink-500 hover:border-seal-gold/50"
          }`}
        >
          <ParticleField count={dragging ? 46 : 20} className={dragging ? "opacity-90" : "opacity-40"} />

          <motion.span
            animate={dragging ? { scale: 1.15, y: -4 } : { scale: 1, y: 0 }}
            transition={{ type: "spring", stiffness: 260, damping: 16 }}
            className="relative grid place-items-center w-14 h-14 rounded-full border border-seal-gold/50 text-seal-gold"
          >
            <UploadCloud size={24} />
          </motion.span>
          <div className="relative">
            <p className="font-display text-xl text-parchment">
              Drop files here, or click to browse
            </p>
            <p className="text-sm text-parchment-muted mt-1.5">
              Certificates · Resumes · Project reports · Internship letters · Academic records
            </p>
            <p className="stamp text-parchment-muted mt-3">
              {ACCEPTED.join("  ·  ").toUpperCase()}
            </p>
          </div>
          <input
            ref={inputRef}
            type="file"
            multiple
            accept={ACCEPTED.join(",")}
            className="hidden"
            onChange={(e) => e.target.files?.length && addFiles(e.target.files)}
          />
        </motion.div>

        {queue.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-display text-lg text-parchment">
                Processing queue
                <span className="stamp text-parchment-muted ml-3">
                  {doneCount}/{queue.length} classified
                </span>
              </h2>
              {doneCount > 0 && (
                <Link to="/documents" className="text-sm text-seal-gold hover:underline flex items-center gap-1">
                  View in archive <ArrowRight size={14} />
                </Link>
              )}
            </div>

            <div className="space-y-3">
              <AnimatePresence initial={false}>
                {queue.map((item) => (
                  <QueueRow key={item.id} item={item} onDismiss={() => clearItem(item.id)} />
                ))}
              </AnimatePresence>
            </div>
          </div>
        )}
      </main>
    </>
  );
}

function QueueRow({ item, onDismiss }) {
  const { file, status, progress, result, error } = item;
  const dismissable = status === "done" || status === "error";

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -12, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, x: 40, scale: 0.96, transition: { duration: 0.2 } }}
      transition={{ type: "spring", stiffness: 300, damping: 28 }}
      className="card p-4 sm:p-5 relative"
    >
      <div className="flex items-center gap-4">
        <motion.span
          animate={status === "uploading" ? { scale: [1, 1.08, 1] } : { scale: 1 }}
          transition={status === "uploading" ? { repeat: Infinity, duration: 1.6, ease: "easeInOut" } : {}}
          className="grid place-items-center w-10 h-10 rounded-lg bg-ink-700 text-parchment-muted shrink-0"
        >
          <FileText size={18} />
        </motion.span>

        <div className="min-w-0 flex-1">
          <p className="text-sm text-parchment truncate font-medium">{file.name}</p>
          <p className="stamp text-parchment-muted mt-0.5">
            {(file.size / 1024).toFixed(0)} KB
            {status === "uploading" && " · reading & classifying… this can take a moment"}
            {status === "done" && " · classified"}
            {status === "error" && " · failed"}
          </p>
        </div>

        <StatusIcon status={status} />

        {dismissable && (
          <button
            onClick={onDismiss}
            className="text-parchment-muted hover:text-parchment p-1"
            aria-label="Dismiss"
          >
            <X size={14} />
          </button>
        )}
      </div>

      {status === "uploading" && (
        <div className="mt-3 h-1.5 rounded-full bg-ink-700 overflow-hidden">
          <motion.div
            className="h-full bg-seal-gold"
            initial={{ width: 0 }}
            animate={{ width: `${Math.max(progress, 8)}%` }}
            transition={{ duration: 0.4, ease: easeOut }}
          />
        </div>
      )}

      <AnimatePresence>
        {status === "done" && result && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            transition={{ duration: 0.3, delay: 0.1 }}
            className="mt-4 pt-4 border-t border-ink-600 flex flex-wrap items-center gap-2 overflow-hidden"
          >
            <CategoryBadge category={result.category} />
            {result.skills_found?.slice(0, 5).map((s, i) => (
              <motion.span
                key={s}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.15 + i * 0.05 }}
                className="stamp px-2 py-1 rounded-full bg-ink-700 text-seal-teal border border-seal-teal/30"
              >
                {s}
              </motion.span>
            ))}
            {result.date_extracted && (
              <span className="stamp text-parchment-muted ml-auto">{result.date_extracted}</span>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {status === "error" && (
        <p className="mt-3 text-sm text-seal-coral">{error}</p>
      )}
    </motion.div>
  );
}

function StatusIcon({ status }) {
  if (status === "uploading")
    return <Loader2 size={18} className="animate-spin text-seal-gold shrink-0" />;
  if (status === "done") return <CheckCircle2 size={18} className="text-seal-teal shrink-0" />;
  if (status === "error") return <XCircle size={18} className="text-seal-coral shrink-0" />;
  return null;
}