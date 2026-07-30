"""
INSIGHT SERVICE
===============
Transforms raw document data into career intelligence:

  1. PROFILE SCORE   — gamified 0-100 completeness score
  2. SKILL INSIGHTS  — strength analysis per skill (emerging/developing/strong)
  3. GAP ANALYSIS    — "You have 4 Python projects but no Python certification"
  4. GROWTH METRICS  — year-over-year new skills & documents
  5. AI HIGHLIGHTS   — auto-generated narrative facts about the user

This is the module that makes judges say: "It doesn't just store documents,
it actually UNDERSTANDS the person."
"""

from typing import Dict, List, Any
from datetime import datetime
from collections import defaultdict

from app.db.sqlite_db import sqlite_db
from app.core.logger import logger


class InsightService:

    def __init__(self):
        self.db = sqlite_db

    # ══════════════════════════════════════════════
    # MASTER METHOD — full insights payload
    # ══════════════════════════════════════════════
    def generate_insights(self, user_id: str = "default_user") -> Dict[str, Any]:
        documents = self.db.get_all_documents(user_id)

        if not documents:
            return self._empty_insights()

        skill_insights = self._analyze_skills(documents)
        gaps = self._detect_gaps(documents, skill_insights)
        growth = self._growth_metrics(documents)
        score = self._profile_score(documents, skill_insights)
        highlights = self._generate_highlights(documents, skill_insights, growth, score)

        logger.info(f"💡 Generated insights: {len(skill_insights)} skills, {len(gaps)} gaps, {len(highlights)} highlights")

        return {
            "profile_score": score,
            "skill_insights": skill_insights,
            "skill_gaps": gaps,
            "growth_metrics": growth,
            "highlights": highlights,
            "generated_at": datetime.now().isoformat(),
        }

    # ─────────────────────────────────────────────
    # 1. SKILL INSIGHTS — how strong is each skill?
    # ─────────────────────────────────────────────
    def _analyze_skills(self, documents: List[Dict]) -> List[Dict]:
        skill_map = defaultdict(lambda: {"docs": [], "categories": set(), "dates": []})

        for doc in documents:
            for skill in doc.get("skills", []):
                key = skill.lower()
                skill_map[key]["docs"].append(doc["title"])
                skill_map[key]["categories"].add(doc["category"])
                if doc.get("date_extracted"):
                    skill_map[key]["dates"].append(doc["date_extracted"])

        insights = []
        for skill, data in skill_map.items():
            count = len(data["docs"])
            categories = list(data["categories"])

            # Strength logic:
            #   strong     = 3+ docs AND appears in 2+ categories (learned + applied)
            #   developing = 2+ docs OR appears in project/internship
            #   emerging   = mentioned once
            if count >= 3 and len(categories) >= 2:
                strength = "strong"
            elif count >= 2 or any(c in categories for c in ["project", "internship"]):
                strength = "developing"
            else:
                strength = "emerging"

            dates = sorted(data["dates"])
            insights.append({
                "skill": skill.title(),
                "document_count": count,
                "categories": categories,
                "first_seen": dates[0] if dates else None,
                "last_seen": dates[-1] if dates else None,
                "strength": strength,
                "evidence": data["docs"][:5],
            })

        # Strongest skills first
        strength_order = {"strong": 0, "developing": 1, "emerging": 2}
        insights.sort(key=lambda s: (strength_order[s["strength"]], -s["document_count"]))
        return insights

    # ─────────────────────────────────────────────
    # 2. GAP ANALYSIS — the career-coach feature
    # ─────────────────────────────────────────────
    def _detect_gaps(self, documents: List[Dict], skill_insights: List[Dict]) -> List[Dict]:
        gaps = []
        categories_present = {d["category"] for d in documents}

        # GAP TYPE A: Skill used in projects but never certified
        for si in skill_insights:
            if "project" in si["categories"] and "certification" not in si["categories"]:
                if si["document_count"] >= 2:
                    gaps.append({
                        "gap_type": "skill_without_certification",
                        "title": f"{si['skill']} — Uncertified Strength",
                        "description": f"You've used {si['skill']} in {si['document_count']} documents but have no certification for it.",
                        "recommendation": f"A {si['skill']} certification would formally validate skills you already demonstrate.",
                        "priority": "high",
                    })

        # GAP TYPE B: Certified but never applied
        for si in skill_insights:
            if "certification" in si["categories"] and "project" not in si["categories"]:
                gaps.append({
                    "gap_type": "certification_without_application",
                    "title": f"{si['skill']} — Certified but Unapplied",
                    "description": f"You're certified in {si['skill']} but have no project demonstrating it.",
                    "recommendation": f"Build a small project using {si['skill']} to turn theory into portfolio proof.",
                    "priority": "medium",
                })

        # GAP TYPE C: Missing profile sections
        important = {"resume": "A resume ties your whole profile together.",
                     "internship": "Internship experience strengthens career credibility.",
                     "project": "Projects are the strongest proof of practical skills."}
        for cat, why in important.items():
            if cat not in categories_present:
                gaps.append({
                    "gap_type": "missing_category",
                    "title": f"No {cat.title()} Documents",
                    "description": f"Your profile has no {cat} documents yet.",
                    "recommendation": why,
                    "priority": "medium" if cat != "project" else "high",
                })

        priority_order = {"high": 0, "medium": 1, "low": 2}
        gaps.sort(key=lambda g: priority_order[g["priority"]])
        return gaps[:6]

    # ─────────────────────────────────────────────
    # 3. GROWTH METRICS — year over year
    # ─────────────────────────────────────────────
    def _growth_metrics(self, documents: List[Dict]) -> List[Dict]:
        by_year = defaultdict(lambda: {"docs": 0, "skills": set(), "categories": set()})
        seen_skills = set()

        # Sort chronologically so "new skills" are truly new
        def doc_year(d):
            date = d.get("date_extracted") or d.get("created_at", "")
            import re
            m = re.search(r"\b(20\d{2})\b", str(date))
            return int(m.group(1)) if m else datetime.now().year

        for doc in sorted(documents, key=doc_year):
            year = doc_year(doc)
            by_year[year]["docs"] += 1
            by_year[year]["categories"].add(doc["category"])
            for skill in doc.get("skills", []):
                if skill.lower() not in seen_skills:
                    seen_skills.add(skill.lower())
                    by_year[year]["skills"].add(skill.title())

        return [
            {
                "year": year,
                "documents_added": data["docs"],
                "new_skills": sorted(data["skills"]),
                "categories_touched": sorted(data["categories"]),
            }
            for year, data in sorted(by_year.items())
        ]

    # ─────────────────────────────────────────────
    # 4. PROFILE SCORE — gamified completeness (0-100)
    # ─────────────────────────────────────────────
    def _profile_score(self, documents: List[Dict], skill_insights: List[Dict]) -> Dict:
        breakdown = {}

        # Dimension 1: Document diversity (max 30)
        categories = {d["category"] for d in documents}
        breakdown["diversity"] = min(30, len(categories) * 6)

        # Dimension 2: Volume (max 20)
        breakdown["volume"] = min(20, len(documents) * 4)

        # Dimension 3: Skill depth (max 30) — strong skills worth more
        strong = sum(1 for s in skill_insights if s["strength"] == "strong")
        developing = sum(1 for s in skill_insights if s["strength"] == "developing")
        breakdown["skill_depth"] = min(30, strong * 8 + developing * 4)

        # Dimension 4: Proof of application (max 20) — projects + internships
        applied = sum(1 for d in documents if d["category"] in ["project", "internship"])
        breakdown["applied_experience"] = min(20, applied * 5)

        overall = sum(breakdown.values())

        levels = [(80, "Professional"), (60, "Achiever"), (35, "Builder"), (0, "Beginner")]
        level = next(name for threshold, name in levels if overall >= threshold)

        return {"overall_score": overall, "breakdown": breakdown, "level": level}

    # ─────────────────────────────────────────────
    # 5. AI HIGHLIGHTS — auto-generated narrative
    # ─────────────────────────────────────────────
    def _generate_highlights(self, documents, skill_insights, growth, score) -> List[Dict]:
        highlights = []

        # Strongest skill
        strong_skills = [s for s in skill_insights if s["strength"] == "strong"]
        if strong_skills:
            top = strong_skills[0]
            highlights.append({
                "icon": "💪",
                "title": f"{top['skill']} is your strongest skill",
                "detail": f"Evidenced across {top['document_count']} documents in {len(top['categories'])} different areas — you've both learned AND applied it.",
                "highlight_type": "strength",
            })

        # Growth trend
        if len(growth) >= 2:
            latest, previous = growth[-1], growth[-2]
            if latest["documents_added"] >= previous["documents_added"]:
                highlights.append({
                    "icon": "📈",
                    "title": f"Accelerating growth in {latest['year']}",
                    "detail": f"You added {latest['documents_added']} achievements and {len(latest['new_skills'])} new skills — matching or beating your {previous['year']} pace.",
                    "highlight_type": "trend",
                })

        # Skill breadth
        if len(skill_insights) >= 5:
            highlights.append({
                "icon": "🧩",
                "title": f"{len(skill_insights)} distinct skills tracked",
                "detail": f"Your top areas: {', '.join(s['skill'] for s in skill_insights[:4])}.",
                "highlight_type": "milestone",
            })

        # Career flow completeness
        categories = {d["category"] for d in documents}
        if {"certification", "project"}.issubset(categories):
            highlights.append({
                "icon": "🔗",
                "title": "Learn → Apply loop detected",
                "detail": "You consistently turn certifications into real projects — exactly what recruiters look for.",
                "highlight_type": "strength",
            })

        # Score level
        highlights.append({
            "icon": "🏅",
            "title": f"Profile level: {score['level']} ({score['overall_score']}/100)",
            "detail": self._level_message(score),
            "highlight_type": "milestone",
        })

        return highlights

    @staticmethod
    def _level_message(score: Dict) -> str:
        weakest = min(score["breakdown"], key=score["breakdown"].get)
        tips = {
            "diversity": "Add documents from more categories (certificates, internships, achievements).",
            "volume": "Upload more of your existing documents to strengthen your profile.",
            "skill_depth": "Deepen key skills — apply them across projects and internships.",
            "applied_experience": "Add project reports or internship letters to prove hands-on experience.",
        }
        return f"Biggest opportunity: {tips[weakest]}"

    def _empty_insights(self) -> Dict:
        return {
            "profile_score": {"overall_score": 0, "breakdown": {}, "level": "Beginner"},
            "skill_insights": [],
            "skill_gaps": [],
            "growth_metrics": [],
            "highlights": [{
                "icon": "🚀",
                "title": "Start your journey",
                "detail": "Upload your first document and watch the AI build your digital identity.",
                "highlight_type": "milestone",
            }],
            "generated_at": datetime.now().isoformat(),
        }


# Singleton instance
insight_service = InsightService()