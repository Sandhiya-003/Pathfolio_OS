import { motion } from "framer-motion";

const easeOut = [0.16, 1, 0.3, 1];

/** Fades + slides a section up as it scrolls into view (only triggers once). */
export function FadeInSection({ children, delay = 0, className = "" }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.5, delay, ease: easeOut }}
      className={className}
    >
      {children}
    </motion.section>
  );
}

/** Wraps a grid of cards; children should be <StaggerItem> for the stagger to apply. */
export function StaggerGrid({ children, className = "" }) {
  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={{
        hidden: {},
        show: { transition: { staggerChildren: 0.06 } },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export function StaggerItem({ children, className = "" }) {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y: 16, scale: 0.98 },
        show: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.4, ease: easeOut } },
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}