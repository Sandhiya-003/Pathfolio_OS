import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { FileStack, Layers, Sparkles, TrendingUp, UploadCloud, ArrowUpRight } from "lucide-react";
import TopBar from "../components/TopBar";
import StatCard from "../components/StatCard";
import DocumentCard from "../components/DocumentCard";
import DocumentModal from "../components/DocumentModal";
import EmptyState from "../components/EmptyState";
import ParticleField from "../components/ParticleField";
import { FadeInSection, StaggerGrid, StaggerItem } from "../components/Motion";
import { CardSkeleton } from "../components/Loader";
import { api } from "../lib/api";
import { useToast } from "../context/ToastContext";

export default function Dashboard() {
  const toast = useToast();
  const [stats, setStats] = useState(null);
  const [recent, setRecent] = useState(null);
  const [insights, setInsights] = useState(null);
  const [activeDoc, setActiveDoc] = useState(null);
  const [error, setError] = useState(false);

  async function load() {
    setError(false);
    try {
      const [statsRes, recentRes, insightsRes] = await Promise.all([
        api.getDocumentStats(),
        api.recentDocuments({ limit: 6 }),
        api.getInsights().catch(() => null),
      ]);
      setStats(statsRes);
      setRecent(recentRes.documents);
      setInsights(insightsRes);
    } catch (e) {
      setError(true);
      toast.error("Couldn't reach the backend. Is the API running?");
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleDelete(doc) {
    if (!confirm(`Remove "${doc.title || doc.original_filename}" from your archive?`)) return;
    try {
      await api.deleteDocument(doc.id);
      toast.success("Document removed");
      load();
    } catch {
      toast.error("Couldn't delete that document");
    }
  }

  const topCategory = stats?.documents_by_category
    ? Object.entries(stats.documents_by_category).sort((a, b) => b[1] - a[1])[0]
    : null;

  return (
    <>
      <div className="relative overflow-hidden border-b border-ink-600">
        <ParticleField count={28} className="opacity-70" />
        <div className="relative">
          <TopBar title="Overview" subtitle="Your digital identity, at a glance" />
        </div>
      </div>

      <main className="px-4 sm:px-8 py-8 max-w-7xl mx-auto space-y-10">
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="card border-seal-coral/40 px-5 py-4 text-sm text-seal-coral overflow-hidden"
            >
              Can't connect to the backend at <code className="font-mono">{api.baseUrl}</code>.
              Start the FastAPI server and refresh, or update <code className="font-mono">VITE_API_BASE_URL</code>.
            </motion.div>
          )}
        </AnimatePresence>

        <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          <StatCard
            index={0}
            label="Documents archived"
            value={stats?.total_documents ?? "—"}
            hint="Certificates, projects, letters & more"
            icon={FileStack}
            accent="#C9A24E"
          />
          <StatCard
            index={1}
            label="Skills identified"
            value={stats?.skills_count ?? "—"}
            hint="Extracted automatically by AI"
            icon={Layers}
            accent="#4FD1C5"
          />
          <StatCard
            index={2}
            label="Strongest category"
            value={topCategory ? topCategory[0] : "—"}
            hint={topCategory ? `${topCategory[1]} documents` : "Upload to see trends"}
            icon={TrendingUp}
            accent="#9B8AFB"
          />
          <StatCard
            index={3}
            label="Profile score"
            value={insights?.profile_score ? `${insights.profile_score.overall_score}/100` : "—"}
            hint={insights?.profile_score?.level || "Complete your archive"}
            icon={Sparkles}
            accent="#E8735C"
          />
        </section>

        {insights?.highlights?.length > 0 && (
          <FadeInSection>
            <SectionHeader title="AI highlights" subtitle="What your journey says about you" />
            <StaggerGrid className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {insights.highlights.slice(0, 3).map((h, i) => (
                <StaggerItem key={i}>
                  <motion.div whileHover={{ y: -3 }} className="card p-5 h-full">
                    <span className="text-2xl">{h.icon}</span>
                    <h3 className="font-display text-base text-parchment mt-3">{h.title}</h3>
                    <p className="text-sm text-parchment-muted mt-1.5 leading-relaxed">{h.detail}</p>
                  </motion.div>
                </StaggerItem>
              ))}
            </StaggerGrid>
          </FadeInSection>
        )}

        <FadeInSection delay={0.05}>
          <SectionHeader
            title="Recently ingested"
            subtitle="The latest additions to your archive"
            action={
              <Link to="/documents" className="text-sm text-seal-gold flex items-center gap-1 hover:underline">
                View archive <ArrowUpRight size={14} />
              </Link>
            }
          />

          {recent === null && !error && (
            <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <CardSkeleton key={i} />
              ))}
            </div>
          )}

          {recent?.length === 0 && (
            <EmptyState
              icon={UploadCloud}
              title="Your archive is empty"
              detail="Upload a certificate, resume, or project report and watch the AI build your digital identity."
              actionLabel="Ingest your first document"
              actionTo="/upload"
            />
          )}

          {recent?.length > 0 && (
            <StaggerGrid className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
              {recent.map((doc) => (
                <StaggerItem key={doc.id}>
                  <DocumentCard doc={doc} onOpen={setActiveDoc} onDelete={handleDelete} />
                </StaggerItem>
              ))}
            </StaggerGrid>
          )}
        </FadeInSection>
      </main>

      <DocumentModal doc={activeDoc} onClose={() => setActiveDoc(null)} />
    </>
  );
}

function SectionHeader({ title, subtitle, action }) {
  return (
    <div className="flex items-end justify-between gap-4 mb-4">
      <div>
        <h2 className="font-display text-xl text-parchment">{title}</h2>
        {subtitle && <p className="text-sm text-parchment-muted mt-0.5">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}