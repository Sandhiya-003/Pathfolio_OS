import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ScrollText } from "lucide-react";
import TopBar from "../components/TopBar";
import CategoryBadge from "../components/CategoryBadge";
import DocumentModal from "../components/DocumentModal";
import EmptyState from "../components/EmptyState";
import { PageLoader } from "../components/Loader";
import { FadeInSection, StaggerGrid, StaggerItem } from "../components/Motion";
import { categoryMeta } from "../lib/categories";
import { api } from "../lib/api";
import { useToast } from "../context/ToastContext";

export default function Timeline() {
  const toast = useToast();
  const [timeline, setTimeline] = useState(null);
  const [activeDoc, setActiveDoc] = useState(null);

  useEffect(() => {
    api
      .getTimeline()
      .then((res) => setTimeline(res.timeline || []))
      .catch(() => {
        toast.error("Couldn't build your timeline");
        setTimeline([]);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function openEvent(ev) {
    try {
      const doc = await api.getDocument(ev.document_id);
      setActiveDoc(doc);
    } catch {
      toast.error("Couldn't open that document");
    }
  }

  return (
    <>
      <TopBar title="Timeline" subtitle="Your growth, year by year — automatically assembled" />

      <main className="px-4 sm:px-8 py-8 max-w-3xl mx-auto">
        {timeline === null && <PageLoader label="Reconstructing your journey…" />}

        {timeline?.length === 0 && (
          <EmptyState
            icon={ScrollText}
            title="No timeline yet"
            detail="Ingest a few dated documents — certificates, internship letters, project reports — and your journey will appear here."
            actionLabel="Ingest a document"
            actionTo="/upload"
          />
        )}

        {timeline?.length > 0 && (
          <div className="relative pl-8 sm:pl-10">
            <motion.div
              initial={{ scaleY: 0 }}
              animate={{ scaleY: 1 }}
              transition={{ duration: 1, ease: [0.16, 1, 0.3, 1] }}
              style={{ transformOrigin: "top" }}
              className="absolute left-[11px] sm:left-[15px] top-2 bottom-2 w-px bg-gradient-to-b from-seal-gold/60 via-ink-500 to-transparent"
            />

            {timeline.map((yearBlock, yi) => (
              <FadeInSection key={yearBlock.year} delay={yi * 0.05} className="relative mb-12 last:mb-0">
                <motion.div
                  initial={{ scale: 0 }}
                  whileInView={{ scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ type: "spring", stiffness: 260, damping: 16, delay: 0.1 }}
                  className="absolute -left-8 sm:-left-10 top-0 grid place-items-center w-6 h-6 sm:w-8 sm:h-8 rounded-full bg-ink-900 border-2 border-seal-gold text-seal-gold font-mono text-[10px] sm:text-xs"
                >
                  {String(yearBlock.year).slice(-2)}
                </motion.div>

                <div className="pl-2">
                  <h2 className="font-display text-2xl text-parchment">{yearBlock.year}</h2>
                  {yearBlock.summary && (
                    <p className="text-sm text-parchment-muted mt-1 mb-5">{yearBlock.summary}</p>
                  )}

                  <StaggerGrid className="space-y-3">
                    {yearBlock.events.map((ev) => {
                      const meta = categoryMeta(ev.category);
                      return (
                        <StaggerItem key={ev.id}>
                          <motion.button
                            onClick={() => openEvent(ev)}
                            whileHover={{ y: -2, transition: { duration: 0.15 } }}
                            className="card w-full text-left p-4 sm:p-5 flex items-start gap-4 hover:border-seal-gold/40 transition-colors"
                          >
                            <span
                              className="grid place-items-center w-9 h-9 rounded-full text-base shrink-0"
                              style={{ background: `${meta.accent}18`, border: `1px solid ${meta.accent}55` }}
                            >
                              {ev.emoji || meta.emoji}
                            </span>
                            <div className="min-w-0 flex-1">
                              <div className="flex items-center gap-2 flex-wrap mb-1">
                                <CategoryBadge category={ev.category} />
                                <span className="stamp text-parchment-muted">{ev.date}</span>
                              </div>
                              <p className="text-parchment font-medium">{ev.title}</p>
                              {ev.description && (
                                <p className="text-sm text-parchment-muted mt-1 line-clamp-2">
                                  {ev.description}
                                </p>
                              )}
                              {ev.skills?.length > 0 && (
                                <div className="flex flex-wrap gap-1.5 mt-2">
                                  {ev.skills.slice(0, 4).map((s) => (
                                    <span
                                      key={s}
                                      className="stamp px-2 py-0.5 rounded-full bg-ink-700 text-seal-teal border border-seal-teal/30"
                                    >
                                      {s}
                                    </span>
                                  ))}
                                </div>
                              )}
                            </div>
                          </motion.button>
                        </StaggerItem>
                      );
                    })}
                  </StaggerGrid>
                </div>
              </FadeInSection>
            ))}
          </div>
        )}
      </main>

      <DocumentModal doc={activeDoc} onClose={() => setActiveDoc(null)} />
    </>
  );
}