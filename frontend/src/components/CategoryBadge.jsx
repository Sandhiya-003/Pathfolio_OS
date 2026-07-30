import { categoryMeta } from "../lib/categories";

export default function CategoryBadge({ category, size = "sm" }) {
  const meta = categoryMeta(category);
  const pad = size === "sm" ? "px-2 py-1 text-[10px]" : "px-2.5 py-1.5 text-xs";

  return (
    <span
      className={`stamp inline-flex items-center gap-1.5 rounded-full border ${pad}`}
      style={{ borderColor: `${meta.accent}55`, color: meta.accent, background: `${meta.accent}12` }}
    >
      <span aria-hidden>{meta.emoji}</span>
      {meta.label}
    </span>
  );
}
