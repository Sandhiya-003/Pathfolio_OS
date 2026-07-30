import { createContext, useCallback, useContext, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, XCircle, Info, X } from "lucide-react";

const ToastContext = createContext(null);

const ICONS = {
  success: CheckCircle2,
  error: XCircle,
  info: Info,
};

const ACCENTS = {
  success: "border-seal-teal/40 text-seal-teal",
  error: "border-seal-coral/40 text-seal-coral",
  info: "border-seal-gold/40 text-seal-gold",
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const idRef = useRef(0);

  const dismiss = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const push = useCallback(
    (message, type = "info", timeout = 4200) => {
      const id = ++idRef.current;
      setToasts((prev) => [...prev, { id, message, type }]);
      if (timeout) {
        setTimeout(() => dismiss(id), timeout);
      }
      return id;
    },
    [dismiss]
  );

  const toast = {
    success: (msg, t) => push(msg, "success", t),
    error: (msg, t) => push(msg, "error", t),
    info: (msg, t) => push(msg, "info", t),
  };

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <div className="fixed bottom-5 right-5 z-[100] flex flex-col gap-2 w-[min(360px,calc(100vw-2.5rem))]">
        <AnimatePresence initial={false}>
          {toasts.map((t) => {
            const Icon = ICONS[t.type];
            return (
              <motion.div
                key={t.id}
                layout
                initial={{ opacity: 0, x: 40, scale: 0.95 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 40, scale: 0.95, transition: { duration: 0.2 } }}
                transition={{ type: "spring", stiffness: 300, damping: 26 }}
                className={`card border ${ACCENTS[t.type]} px-4 py-3 flex items-start gap-3`}
              >
                <Icon size={18} className="mt-0.5 shrink-0" />
                <p className="text-sm text-parchment leading-snug flex-1">{t.message}</p>
                <button
                  onClick={() => dismiss(t.id)}
                  className="text-parchment-muted hover:text-parchment"
                  aria-label="Dismiss"
                >
                  <X size={14} />
                </button>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx;
}