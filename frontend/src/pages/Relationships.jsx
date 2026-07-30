import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { GitBranch, Layers } from "lucide-react";
import TopBar from "../components/TopBar";
import DocumentModal from "../components/DocumentModal";
import EmptyState from "../components/EmptyState";
import { PageLoader } from "../components/Loader";
import { categoryMeta } from "../lib/categories";
import { api } from "../lib/api";
import { useToast } from "../context/ToastContext";

const WIDTH = 720;
const HEIGHT = 720;
const CENTER = { x: WIDTH / 2, y: HEIGHT / 2 };
const SKILL_RADIUS = 190;
const DOC_RADIUS = 320;

export default function Relationships() {
  const toast = useToast();
  const [graph, setGraph] = useState(null);
  const [skills, setSkills] = useState(null);
  const [activeId, setActiveId] = useState(null);
  const [activeDoc, setActiveDoc] = useState(null);

  useEffect(() => {
    Promise.all([api.getRelationshipGraph(), api.getAllSkills()])
      .then(([g, s]) => {
        setGraph(g);
        setSkills(s.skills || []);
      })
      .catch(() => {
        toast.error("Couldn't build the knowledge map");
        setGraph({ nodes: [], edges: [] });
        setSkills([]);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const layout = useMemo(() => {
    if (!graph) return null;
    const skillNodes = graph.nodes.filter((n) => n.type === "skill");
    const docNodes = graph.nodes.filter((n) => n.type === "document");

    const positioned = {};
    skillNodes.forEach((n, i) => {
      const angle = (i / Math.max(skillNodes.length, 1)) * Math.PI * 2 - Math.PI / 2;
      positioned[n.id] = {
        ...n,
        x: CENTER.x + SKILL_RADIUS * Math.cos(angle),
        y: CENTER.y + SKILL_RADIUS * Math.sin(angle),
      };
    });
    docNodes.forEach((n, i) => {
      const angle = (i / Math.max(docNodes.length, 1)) * Math.PI * 2 - Math.PI / 2;
      positioned[n.id] = {
        ...n,
        x: CENTER.x + DOC_RADIUS * Math.cos(angle),
        y: CENTER.y + DOC_RADIUS * Math.sin(angle),
      };
    });

    return { nodes: positioned, edges: graph.edges };
  }, [graph]);

  async function openDoc(nodeId) {
    try {
      const doc = await api.getDocument(nodeId);
      setActiveDoc(doc);
    } catch {
      toast.error("Couldn't open that document");
    }
  }

  const isEmpty = graph && graph.nodes.length === 0;

  return (
    <>
      <TopBar title="Knowledge Map" subtitle="How your certifications, skills, and projects connect" />

      <main className="px-4 sm:px-8 py-8 max-w-7xl mx-auto">
        {!graph && <PageLoader label="Mapping your knowledge graph…" />}

        {isEmpty && (
          <EmptyState
            icon={GitBranch}
            title="No connections yet"
            detail="As you ingest certificates, projects, and internship letters, Pathfolio automatically links the skills and experiences between them."
            actionLabel="Ingest a document"
            actionTo="/upload"
          />
        )}

        {layout && !isEmpty && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4 }}
            className="grid lg:grid-cols-[1fr,280px] gap-6"
          >
            <div className="card p-2 sm:p-4 overflow-x-auto">
              <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="w-full h-auto min-w-[480px]">
                {layout.edges.map((e, i) => {
                  const a = layout.nodes[e.source];
                  const b = layout.nodes[e.target];
                  if (!a || !b) return null;
                  const dim =
                    activeId && activeId !== e.source && activeId !== e.target ? 0.08 : 0.35;
                  return (
                    <motion.line
                      key={i}
                      x1={a.x}
                      y1={a.y}
                      x2={b.x}
                      y2={b.y}
                      stroke="#4FD1C5"
                      strokeWidth={1.5}
                      initial={{ pathLength: 0, opacity: 0 }}
                      animate={{ pathLength: 1, opacity: dim }}
                      transition={{ pathLength: { duration: 0.8, delay: 0.1 + i * 0.01 }, opacity: { duration: 0.3 } }}
                    />
                  );
                })}

                {Object.values(layout.nodes).map((n, i) => {
                  const isSkill = n.type === "skill";
                  const meta = categoryMeta(n.category);
                  const r = isSkill ? 7 + Math.min(n.size || 1, 4) * 1.5 : 9;
                  const dim = activeId && activeId !== n.id ? 0.35 : 1;
                  const color = isSkill ? "#4FD1C5" : meta.accent;

                  return (
                    // Static positioning lives on a plain <g> that framer-motion never touches.
                    <g key={n.id} transform={`translate(${n.x},${n.y})`}>
                      <motion.g
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: dim, scale: 1 }}
                        transition={{
                          scale: { type: "spring", stiffness: 260, damping: 18, delay: i * 0.015 },
                          opacity: { duration: 0.25 },
                        }}
                        whileHover={{ scale: 1.25 }}
                        style={{ transformOrigin: "0px 0px" }}
                        className="cursor-pointer"
                        onMouseEnter={() => setActiveId(n.id)}
                        onMouseLeave={() => setActiveId(null)}
                        onClick={() => (isSkill ? setActiveId(n.id) : openDoc(n.id))}
                      >
                        <circle r={r} fill={isSkill ? "#12141C" : color} stroke={color} strokeWidth={1.5} />
                        <text
                          y={-r - 6}
                          textAnchor="middle"
                          fontSize={isSkill ? 11 : 9}
                          fontFamily="IBM Plex Mono, monospace"
                          fill={isSkill ? "#ECE7DA" : "#9195AA"}
                        >
                          {truncate(n.label, isSkill ? 16 : 14)}
                        </text>
                      </motion.g>
                    </g>
                  );
                })}
              </svg>

              <div className="flex items-center gap-5 justify-center pt-3 pb-1 flex-wrap">
                <Legend swatch="#4FD1C5" label="Skill" ring />
                <Legend swatch="#C9A24E" label="Document" />
                <p className="stamp text-parchment-muted">Hover a node · click a document to open it</p>
              </div>
            </div>

            <aside className="card p-5 h-fit lg:sticky lg:top-24">
              <p className="stamp text-parchment-muted mb-3 flex items-center gap-1.5">
                <Layers size={13} /> Skills ({skills?.length || 0})
              </p>
              <div className="space-y-1.5 max-h-[520px] overflow-y-auto pr-1">
                {skills?.map((s, i) => {
                  const skillId = `skill_${s.skill.toLowerCase().replace(/\s+/g, "_")}`;
                  return (
                    <motion.div
                      key={s.skill}
                      initial={{ opacity: 0, x: 10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.2 + i * 0.03 }}
                      onMouseEnter={() => setActiveId(skillId)}
                      onMouseLeave={() => setActiveId(null)}
                      className="flex items-center justify-between px-2.5 py-2 rounded-lg hover:bg-ink-700 text-sm"
                    >
                      <span className="text-parchment-dim truncate">{s.skill}</span>
                      <span className="stamp text-seal-teal shrink-0 ml-2">{s.document_count}</span>
                    </motion.div>
                  );
                })}
              </div>
            </aside>
          </motion.div>
        )}
      </main>

      <DocumentModal doc={activeDoc} onClose={() => setActiveDoc(null)} />
    </>
  );
}

function Legend({ swatch, label, ring }) {
  return (
    <div className="flex items-center gap-2">
      <span
        className="w-2.5 h-2.5 rounded-full"
        style={{
          background: ring ? "transparent" : swatch,
          border: `1.5px solid ${swatch}`,
        }}
      />
      <span className="stamp text-parchment-muted">{label}</span>
    </div>
  );
}

function truncate(str = "", n) {
  return str.length > n ? str.slice(0, n - 1) + "…" : str;
}