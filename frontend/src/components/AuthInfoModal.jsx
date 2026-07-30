import { AnimatePresence, motion } from "framer-motion";
import { X } from "lucide-react";

export default function AuthInfoModal({ title, subtitle, onClose, children }) {
  return (
    <AnimatePresence>
      {title && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
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
            className="relative w-full max-w-lg max-h-[80vh] overflow-y-auto bg-[#0d111a] border border-slate-800/80 rounded-3xl p-8"
          >
            <button
              onClick={onClose}
              className="absolute right-6 top-6 text-slate-500 hover:text-slate-300 transition-colors"
              aria-label="Close"
            >
              <X size={20} />
            </button>

            <span className="text-xs uppercase tracking-[0.25em] text-amber-500/80 font-medium">
              {subtitle}
            </span>
            <h2 className="text-3xl font-serif-title text-slate-100 mt-2 mb-6">{title}</h2>

            {children}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}