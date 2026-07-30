import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { ToastProvider } from "./context/ToastContext";
import { AuthProvider } from "./context/AuthContext";
import { UploadQueueProvider } from "./context/UploadQueueContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Sidebar from "./components/Sidebar";
import ParticleField from "./components/ParticleField";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";
import Documents from "./pages/Documents";
import Search from "./pages/Search";
import Assistant from "./pages/Assistant";
import Timeline from "./pages/Timeline";
import Relationships from "./pages/Relationships";
import Insights from "./pages/Insights";

// Routes that already have enough going on visually -- skip the ambient particles here.
const NO_AMBIENT_PARTICLES = ["/relationships"];

function AppShell({ children }) {
  const location = useLocation();
  const showAmbient = !NO_AMBIENT_PARTICLES.includes(location.pathname);

  return (
    <div className="flex min-h-screen bg-ink-900">
      {showAmbient && <ParticleField count={26} fixed className="opacity-[0.15] z-0" />}
      <Sidebar />
      <div className="relative z-10 flex-1 min-w-0">{children}</div>
    </div>
  );
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <UploadQueueProvider>
              <AppShell>
                <AnimatedInnerRoutes />
              </AppShell>
            </UploadQueueProvider>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

/**
 * Fades/slides each page as you navigate between them. A single motion.div
 * keyed on the pathname is enough to animate every route -- no need to wrap
 * each individual page component in motion primitives.
 */
function AnimatedInnerRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
      >
        <Routes location={location}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/search" element={<Search />} />
          <Route path="/assistant" element={<Assistant />} />
          <Route path="/timeline" element={<Timeline />} />
          <Route path="/relationships" element={<Relationships />} />
          <Route path="/insights" element={<Insights />} />
        </Routes>
      </motion.div>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <BrowserRouter>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </BrowserRouter>
    </ToastProvider>
  );
}