import { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Menu, X, Search, LayoutGrid, UploadCloud, FolderOpen, GitBranch, Sparkles, ScrollText, MessageCircle, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useUploadQueue } from "../context/UploadQueueContext";

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

export default function TopBar({ title, subtitle }) {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { inFlightCount } = useUploadQueue();

  function submitSearch(e) {
    e.preventDefault();
    if (!q.trim()) return;
    navigate(`/search?q=${encodeURIComponent(q.trim())}`);
  }

  function handleLogout() {
    setOpen(false);
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <header className="sticky top-0 z-40 bg-ink-900/85 backdrop-blur border-b border-ink-600">
      <div className="flex items-center gap-4 px-4 sm:px-8 py-4">
        <button
          className="lg:hidden relative text-parchment-dim"
          onClick={() => setOpen(true)}
          aria-label="Open menu"
        >
          <Menu size={22} />
          {inFlightCount > 0 && (
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-seal-gold"
            />
          )}
        </button>

        <div className="flex-1 min-w-0">
          <motion.h1
            key={title}
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="font-display text-xl sm:text-2xl text-parchment truncate"
          >
            {title}
          </motion.h1>
          {subtitle && <p className="text-sm text-parchment-muted mt-0.5">{subtitle}</p>}
        </div>

        <form onSubmit={submitSearch} className="hidden md:block relative w-72">
          <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-parchment-muted" />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Ask: show my AI projects…"
            className="input-field pl-9 py-2 text-sm"
          />
        </form>
      </div>

      <AnimatePresence>
        {open && (
          <div className="fixed inset-0 z-50 lg:hidden">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/60"
              onClick={() => setOpen(false)}
            />
            <motion.div
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ type: "spring", stiffness: 320, damping: 32 }}
              className="absolute left-0 top-0 bottom-0 w-72 bg-ink-900 border-r border-ink-600 p-5"
            >
              <div className="flex items-center justify-between mb-6">
                <span className="font-display text-lg text-parchment">Pathfolio</span>
                <button onClick={() => setOpen(false)} className="text-parchment-dim" aria-label="Close menu">
                  <X size={20} />
                </button>
              </div>
              <nav className="space-y-1">
                {NAV.map(({ to, label, icon: Icon, end }) => (
                  <NavLink
                    key={to}
                    to={to}
                    end={end}
                    onClick={() => setOpen(false)}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                        isActive ? "bg-ink-700 text-seal-gold" : "text-parchment-dim hover:bg-ink-800"
                      }`
                    }
                  >
                    <Icon size={17} />
                    <span className="flex-1">{label}</span>
                    {to === "/upload" && inFlightCount > 0 && (
                      <span className="grid place-items-center min-w-[20px] h-5 px-1.5 rounded-full bg-seal-gold text-ink-950 text-[10px] font-mono font-semibold">
                        {inFlightCount}
                      </span>
                    )}
                  </NavLink>
                ))}
              </nav>

              <div className="mt-6 pt-4 border-t border-ink-600">
                <p className="text-sm text-parchment truncate px-3">{user?.full_name || user?.username}</p>
                <p className="stamp text-parchment-muted truncate px-3 mb-3">@{user?.username}</p>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-parchment-dim hover:bg-ink-800 hover:text-seal-coral transition w-full"
                >
                  <LogOut size={17} /> Log out
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </header>
  );
}