import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { Sparkles, TrendingUp, AlertTriangle, Route } from "lucide-react";
import TopBar from "../components/TopBar";
import { PageLoader } from "../components/Loader";
import AnimatedCounter from "../components/AnimatedCounter";
import { FadeInSection, StaggerGrid, StaggerItem } from "../components/Motion";
import { api } from "../lib/api";
import { useToast } from "../context/ToastContext";

const STRENGTH_COLOR = {
  strong: "#4FD1C5",
  developing: "#C9A24E",
  emerging: "#9195AA",
};

const PRIORITY_COLOR = {
  high: "#E8735C",
  medium: "#C9A24E",
  low: "#9195AA",
};

export default function Insights() {
  const toast = useToast();
  const [data, setData] = useState(null);
  const [journeySkill, setJourneySkill] = useState("");
  const [journey, setJourney] = useState(null);
  const [journeyLoading, setJourneyLoading] = useState(false);

  useEffect(() => {
    api
      .getInsights()
      .then(setData)
      .catch(() => {
        toast.error("Couldn't generate insights yet");
        setData(false);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function traceJourney(e) {
    e.preventDefault();
    if (!journeySkill.trim()) return;
    setJourneyLoading(true);
    try {
      const res = await api.traceSkillJourney(journeySkill.trim());
      setJourney(res);
    } catch {
      toast.error("Couldn't trace that skill's journey");
    } finally {
      setJourneyLoading(false);
    }
  }

  if (data === null) {
    return (
      <>
        <TopBar title="Insights" subtitle="What your archive reveals about your growth" />
        <PageLoader label="Analyzing your journey…" />
      </>
    );
  }

  if (data === false || !data) {
    return (
      <>
        <TopBar title="Insights" subtitle="What your archive reveals about your growth" />
        <main className="px-4 sm:px-8 py-16 max-w-3xl mx-auto text-center text-parchment-muted">
          Ingest a few documents first — insights need data to work with.
        </main>
      </>
    );
  }

  const chartData = data.growth_metrics?.map((g) => ({
    year: g.year,
    documents: g.documents_added,
    skills: g.new_skills.length,
  }));

  return (
    <>
      <TopBar title="Insights" subtitle="What your archive reveals about your growth" />

      <main className="px-4 sm:px-8 py-8 max-w-5xl mx-auto space-y-10">
        {/* Profile score */}
        <motion.section
          initial={{ opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="card p-6 sm:p-8 flex flex-col sm:flex-row items-center gap-8"
        >
          <ScoreRing score={data.profile_score.overall_score} />
          <div className="flex-1">
            <p className="stamp text-parchment-muted">Profile completeness</p>
            <h2 className="font-display text-3xl text-parchment mt-1">{data.profile_score.level}</h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-5">
              {Object.entries(data.profile_score.breakdown || {}).map(([k, v], i) => (
                <motion.div
                  key={k}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 + i * 0.08 }}
                >
                  <p className="stamp text-parchment-muted">{k.replace(/_/g, " ")}</p>
                  <p className="text-parchment font-display text-lg mt-0.5">
                    <AnimatedCounter value={v} />
                  </p>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.section>

        {/* Highlights */}
        {data.highlights?.length > 0 && (
          <FadeInSection>
            <SectionHeader icon={Sparkles} title="AI highlights" />
            <StaggerGrid className="grid sm:grid-cols-2 gap-4">
              {data.highlights.map((h, i) => (
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

        {/* Growth chart */}
        {chartData?.length > 0 && (
          <FadeInSection delay={0.05}>
            <SectionHeader icon={TrendingUp} title="Growth over time" />
            <div className="card p-5 h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid stroke="#2B2F3F" vertical={false} />
                  <XAxis dataKey="year" stroke="#9195AA" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#9195AA" fontSize={12} tickLine={false} axisLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{
                      background: "#171A23",
                      border: "1px solid #2B2F3F",
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                    labelStyle={{ color: "#ECE7DA" }}
                  />
                  <Bar dataKey="documents" name="Documents" fill="#C9A24E" radius={[4, 4, 0, 0]} animationDuration={800} />
                  <Bar dataKey="skills" name="New skills" fill="#4FD1C5" radius={[4, 4, 0, 0]} animationDuration={800} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </FadeInSection>
        )}

        {/* Skill strengths */}
        {data.skill_insights?.length > 0 && (
          <FadeInSection delay={0.1}>
            <SectionHeader icon={Sparkles} title="Skill strength" />
            <StaggerGrid className="grid sm:grid-cols-2 gap-3">
              {data.skill_insights.map((s) => (
                <StaggerItem key={s.skill}>
                  <div className="card p-4 flex items-center justify-between gap-3 h-full">
                    <div className="min-w-0">
                      <p className="text-parchment font-medium truncate">{s.skill}</p>
                      <p className="stamp text-parchment-muted mt-0.5">
                        {s.document_count} document{s.document_count === 1 ? "" : "s"} ·{" "}
                        {s.categories.join(", ")}
                      </p>
                    </div>
                    <span
                      className="stamp px-2.5 py-1 rounded-full border shrink-0"
                      style={{
                        color: STRENGTH_COLOR[s.strength] || "#9195AA",
                        borderColor: `${STRENGTH_COLOR[s.strength] || "#9195AA"}55`,
                      }}
                    >
                      {s.strength}
                    </span>
                  </div>
                </StaggerItem>
              ))}
            </StaggerGrid>
          </FadeInSection>
        )}

        {/* Skill gaps */}
        {data.skill_gaps?.length > 0 && (
          <FadeInSection delay={0.1}>
            <SectionHeader icon={AlertTriangle} title="Gaps worth closing" />
            <StaggerGrid className="space-y-3">
              {data.skill_gaps.map((g, i) => (
                <StaggerItem key={i}>
                  <div className="card p-5">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span
                        className="stamp px-2 py-0.5 rounded-full border"
                        style={{
                          color: PRIORITY_COLOR[g.priority] || "#9195AA",
                          borderColor: `${PRIORITY_COLOR[g.priority] || "#9195AA"}55`,
                        }}
                      >
                        {g.priority} priority
                      </span>
                    </div>
                    <h3 className="font-display text-base text-parchment">{g.title}</h3>
                    <p className="text-sm text-parchment-muted mt-1.5">{g.description}</p>
                    <p className="text-sm text-seal-gold mt-2">→ {g.recommendation}</p>
                  </div>
                </StaggerItem>
              ))}
            </StaggerGrid>
          </FadeInSection>
        )}

        {/* Skill journey tracer */}
        <FadeInSection delay={0.1}>
          <SectionHeader icon={Route} title="Trace a skill's journey" />
          <p className="text-sm text-parchment-muted -mt-2 mb-4">
            See how a single skill evolved from certification to project to internship.
          </p>
          <form onSubmit={traceJourney} className="flex gap-2 mb-5">
            <input
              value={journeySkill}
              onChange={(e) => setJourneySkill(e.target.value)}
              placeholder="e.g. Python, React, Leadership…"
              className="input-field"
            />
            <button className="btn-primary shrink-0" disabled={journeyLoading}>
              Trace
            </button>
          </form>

          {journeyLoading && <p className="text-sm text-parchment-muted">Tracing…</p>}

          <AnimatePresence>
            {journey && !journeyLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-3"
              >
                {journey.journey_length === 0 ? (
                  <p className="text-sm text-parchment-muted">
                    No documents found for "{journey.skill}" yet.
                  </p>
                ) : (
                  journey.path.map((step, i) => (
                    <motion.div
                      key={step.step}
                      initial={{ opacity: 0, x: -14 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.12 }}
                      className="flex gap-4"
                    >
                      <div className="flex flex-col items-center">
                        <span className="grid place-items-center w-7 h-7 rounded-full border border-seal-gold text-seal-gold font-mono text-xs shrink-0">
                          {step.step}
                        </span>
                        {step.step !== journey.journey_length && (
                          <span className="w-px flex-1 bg-ink-500 my-1" />
                        )}
                      </div>
                      <div className="card p-4 flex-1 mb-1">
                        <p className="stamp text-parchment-muted">
                          {step.category} · {step.date || "undated"}
                        </p>
                        <p className="text-parchment font-medium mt-1">{step.title}</p>
                        {step.narrative && (
                          <p className="text-sm text-parchment-muted mt-1.5">{step.narrative}</p>
                        )}
                      </div>
                    </motion.div>
                  ))
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </FadeInSection>
      </main>
    </>
  );
}

function SectionHeader({ icon: Icon, title }) {
  return (
    <h2 className="font-display text-xl text-parchment mb-4 flex items-center gap-2">
      <Icon size={18} className="text-seal-gold" /> {title}
    </h2>
  );
}

function ScoreRing({ score }) {
  const r = 42;
  const c = 2 * Math.PI * r;
  const offset = c - (score / 100) * c;

  return (
    <svg width={110} height={110} className="shrink-0 -rotate-90">
      <circle cx={55} cy={55} r={r} stroke="#2B2F3F" strokeWidth={8} fill="none" />
      <motion.circle
        cx={55}
        cy={55}
        r={r}
        stroke="#C9A24E"
        strokeWidth={8}
        fill="none"
        strokeLinecap="round"
        strokeDasharray={c}
        initial={{ strokeDashoffset: c }}
        animate={{ strokeDashoffset: offset }}
        transition={{ duration: 1.1, ease: [0.16, 1, 0.3, 1], delay: 0.2 }}
      />
      <text
        x={55}
        y={60}
        textAnchor="middle"
        fill="#ECE7DA"
        fontSize={22}
        fontFamily="Fraunces, serif"
        transform="rotate(90 55 55)"
      >
        <AnimatedCounter value={score} duration={1.1} as="tspan" />
      </text>
    </svg>
  );
}