import { useState } from "react";
import { motion } from "framer-motion";
import { ShieldCheck, Sparkles, ScrollText } from "lucide-react";
import AuthInfoModal from "./AuthInfoModal";
import { OS_FEATURES, SECURITY_POINTS, MANIFESTO } from "../data/authInfoContent";

const LINKS = [
  { key: "features", label: "OS Features" },
  { key: "security", label: "Security" },
  { key: "manifesto", label: "Manifesto" },
];

export default function AuthTopNav() {
  const [active, setActive] = useState(null); // "features" | "security" | "manifesto" | null

  return (
    <>
      <div className="flex justify-end space-x-6 text-xs text-slate-400 font-medium tracking-wider uppercase">
        {LINKS.map((l) => (
          <motion.button
            key={l.key}
            type="button"
            whileHover={{ y: -1 }}
            onClick={() => setActive(l.key)}
            className="hover:text-amber-500 transition-colors"
          >
            {l.label}
          </motion.button>
        ))}
      </div>

      <AuthInfoModal
        title={active === "features" ? "What Pathfolio Actually Does" : null}
        subtitle="OS Features"
        onClose={() => setActive(null)}
      >
        <div className="space-y-5">
          {OS_FEATURES.map((f) => (
            <div key={f.title} className="flex gap-3">
              <Sparkles size={16} className="text-amber-500 mt-0.5 shrink-0" />
              <div>
                <p className="text-sm text-slate-200 font-medium">{f.title}</p>
                <p className="text-sm text-slate-400 mt-1 leading-relaxed">{f.detail}</p>
              </div>
            </div>
          ))}
        </div>
      </AuthInfoModal>

      <AuthInfoModal
        title={active === "security" ? "How Your Data Is Protected" : null}
        subtitle="Security"
        onClose={() => setActive(null)}
      >
        <div className="space-y-5">
          {SECURITY_POINTS.map((s) => (
            <div key={s.title} className="flex gap-3">
              <ShieldCheck size={16} className="text-amber-500 mt-0.5 shrink-0" />
              <div>
                <p className="text-sm text-slate-200 font-medium">{s.title}</p>
                <p className="text-sm text-slate-400 mt-1 leading-relaxed">{s.detail}</p>
              </div>
            </div>
          ))}
        </div>
      </AuthInfoModal>

      <AuthInfoModal
        title={active === "manifesto" ? "The Manifesto" : null}
        subtitle="Why Pathfolio Exists"
        onClose={() => setActive(null)}
      >
        <div className="space-y-4">
          {MANIFESTO.map((p, i) => (
            <p
              key={i}
              className={`text-sm leading-relaxed ${
                i === MANIFESTO.length - 1
                  ? "text-amber-500 font-serif-title text-base italic"
                  : "text-slate-400"
              }`}
            >
              {p}
            </p>
          ))}
        </div>
      </AuthInfoModal>
    </>
  );
}