import { motion } from "framer-motion";
import { Link } from "react-router-dom";

export default function EmptyState({ icon: Icon, title, detail, actionLabel, actionTo }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96, y: 10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="card flex flex-col items-center text-center gap-3 py-16 px-6"
    >
      {Icon && (
        <motion.span
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.1, type: "spring", stiffness: 260, damping: 16 }}
          className="grid place-items-center w-12 h-12 rounded-full border border-ink-500 text-parchment-muted"
        >
          <Icon size={20} />
        </motion.span>
      )}
      <h3 className="font-display text-xl text-parchment">{title}</h3>
      {detail && <p className="text-sm text-parchment-muted max-w-sm">{detail}</p>}
      {actionLabel && actionTo && (
        <Link to={actionTo} className="btn-primary mt-2">
          {actionLabel}
        </Link>
      )}
    </motion.div>
  );
}