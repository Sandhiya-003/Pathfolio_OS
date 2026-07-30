import { motion } from "framer-motion";
import AnimatedCounter from "./AnimatedCounter";

export default function StatCard({ label, value, hint, icon: Icon, accent = "#C9A24E", index = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, delay: index * 0.06, ease: [0.16, 1, 0.3, 1] }}
      whileHover={{ y: -3, transition: { duration: 0.2 } }}
      className="card p-5 flex items-start justify-between gap-3"
    >
      <div className="min-w-0">
        <p className="stamp text-parchment-muted">{label}</p>
        <p className="font-display text-3xl text-parchment mt-2 leading-none">
          <AnimatedCounter value={value} />
        </p>
        {hint && <p className="text-xs text-parchment-muted mt-2">{hint}</p>}
      </div>
      {Icon && (
        <motion.span
          initial={{ scale: 0, rotate: -20 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ delay: index * 0.06 + 0.15, type: "spring", stiffness: 260, damping: 18 }}
          className="grid place-items-center w-10 h-10 rounded-full border shrink-0"
          style={{ borderColor: `${accent}55`, color: accent }}
        >
          <Icon size={17} />
        </motion.span>
      )}
    </motion.div>
  );
}