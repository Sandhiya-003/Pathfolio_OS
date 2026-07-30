export const CATEGORIES = {
  certification: { label: "Certification", emoji: "📜", accent: "#C9A24E" },
  project: { label: "Project", emoji: "🚀", accent: "#4FD1C5" },
  internship: { label: "Internship", emoji: "💼", accent: "#9B8AFB" },
  achievement: { label: "Achievement", emoji: "🏆", accent: "#E8735C" },
  academic: { label: "Academic", emoji: "🎓", accent: "#5EA8E0" },
  resume: { label: "Resume", emoji: "📄", accent: "#9195AA" },
  portfolio: { label: "Portfolio", emoji: "🖼️", accent: "#E893C4" },
  other: { label: "Other", emoji: "📁", accent: "#7C8195" },
};

export function categoryMeta(category) {
  const key = (category || "other").toLowerCase();
  return CATEGORIES[key] || CATEGORIES.other;
}

export const CATEGORY_LIST = Object.keys(CATEGORIES);
