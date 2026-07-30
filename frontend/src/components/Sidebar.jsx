import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  LayoutGrid,
  UploadCloud,
  FolderOpen,
  GitBranch,
  Sparkles,
  Search,
  ScrollText,
  MessageCircle,
  LogOut,
} from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useUploadQueue } from "../context/UploadQueueContext";
import ParticleField from "./ParticleField";

const NAV = [
  { to: "/", label: "Overview", icon: LayoutGrid, end: true },
  { to: "/upload", label: "Ingest", icon: UploadCloud },
  { to: "/documents", label: "Archive", icon: FolderOpen },
  { to: "/search", label: "Retrieve", icon: Search },
  { to: "/assistant", label: "Ask", icon: MessageCircle },
  { to: "/timeline", label: "Timeline", icon: ScrollText },
  { to: "/relationships", label: "Knowledge Map", icon: GitBranch },
  { to: "/insights", label: "Insights", icon: Sparkles },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const { inFlightCount } = useUploadQueue();
  const navigate = useNavigate();
  const location = useLocation();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <aside className="z-10 hidden lg:flex flex-col w-64 shrink-0 border-r border-ink-600 bg-ink-950/70 min-h-screen sticky top-0 overflow-hidden">
      <ParticleField count={14} className="opacity-30" />

      <div className="relative px-6 py-7 border-b border-ink-600">
        <div className="flex items-center gap-2.5">
          <motion.span
            initial={{ rotate: -8, scale: 0.9 }}
            animate={{
              rotate: 0,
              scale: 1,
              boxShadow: [
                "0 0 0px 0px rgba(201,162,78,0.0)",
                "0 0 14px 2px rgba(201,162,78,0.35)",
                "0 0 0px 0px rgba(201,162,78,0.0)",
              ],
            }}
            transition={{
              rotate: { type: "spring", stiffness: 200, damping: 14 },
              scale: { type: "spring", stiffness: 200, damping: 14 },
              boxShadow: { repeat: Infinity, duration: 3.2, ease: "easeInOut" },
            }}
            className="grid place-items-center w-9 h-9 rounded-full border border-seal-gold/50 text-seal-gold font-display font-semibold"
          >
            P
          </motion.span>
          <div>
            <p className="font-display text-lg leading-none text-parchment">Pathfolio</p>
            <p className="stamp text-parchment-muted mt-1">Digital Identity OS</p>
          </div>
        </div>
      </div>

      <nav className="relative flex-1 px-3 py-5 space-y-1">
        {NAV.map(({ to, label, icon: Icon, end }, i) => {
          const isActive = end ? location.pathname === to : location.pathname.startsWith(to);
          return (
            <motion.div
              key={to}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.04, duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
            >
              <NavLink
                to={to}
                end={end}
                className={`relative group flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "text-seal-gold"
                    : "text-parchment-dim hover:text-parchment"
                }`}
              >
                {isActive && (
                  <motion.span
                    layoutId="sidebar-active-pill"
                    className="absolute inset-0 bg-ink-700 rounded-lg"
                    transition={{ type: "spring", stiffness: 380, damping: 32 }}
                  />
                )}
                {!isActive && (
                  <span className="absolute inset-0 rounded-lg bg-ink-800 opacity-0 group-hover:opacity-100 transition-opacity" />
                )}
                <motion.span
                  whileHover={{ scale: 1.15, rotate: -6 }}
                  transition={{ type: "spring", stiffness: 400, damping: 12 }}
                  className="relative"
                >
                  <Icon size={17} strokeWidth={2} />
                </motion.span>
                <span className="relative flex-1">{label}</span>
                {to === "/upload" && inFlightCount > 0 && (
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="relative grid place-items-center min-w-[20px] h-5 px-1.5 rounded-full bg-seal-gold text-ink-950 text-[10px] font-mono font-semibold"
                  >
                    <motion.span
                      animate={{ opacity: [1, 0.4, 1] }}
                      transition={{ repeat: Infinity, duration: 1.4 }}
                    >
                      {inFlightCount}
                    </motion.span>
                  </motion.span>
                )}
              </NavLink>
            </motion.div>
          );
        })}
      </nav>

      <div className="relative px-4 py-4 border-t border-ink-600">
        <div className="flex items-center gap-3 px-2 py-2">
          <motion.span
            animate={{
              boxShadow: [
                "0 0 0px 0px rgba(79,209,197,0.0)",
                "0 0 10px 1px rgba(79,209,197,0.3)",
                "0 0 0px 0px rgba(79,209,197,0.0)",
              ],
            }}
            transition={{ repeat: Infinity, duration: 3.6, ease: "easeInOut" }}
            className="grid place-items-center w-8 h-8 rounded-full bg-ink-700 text-seal-gold font-mono text-xs shrink-0 uppercase"
          >
            {(user?.full_name || user?.username || "?").slice(0, 1)}
          </motion.span>
          <div className="min-w-0 flex-1">
            <p className="text-sm text-parchment truncate">{user?.full_name || user?.username}</p>
            <p className="stamp text-parchment-muted truncate">@{user?.username}</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.1, rotate: -8 }}
            whileTap={{ scale: 0.92 }}
            onClick={handleLogout}
            className="text-parchment-muted hover:text-seal-coral transition p-1.5"
            aria-label="Log out"
            title="Log out"
          >
            <LogOut size={16} />
          </motion.button>
        </div>
      </div>
    </aside>
  );
}