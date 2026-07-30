# Document Categories
DOCUMENT_CATEGORIES = {
    "certification": {
        "emoji": "📜",
        "color": "#10b981",
        "keywords": ["certificate", "certification", "certified", "completion", "diploma"]
    },
    "project": {
        "emoji": "🚀",
        "color": "#3b82f6",
        "keywords": ["project", "implementation", "development", "built", "created"]
    },
    "internship": {
        "emoji": "💼",
        "color": "#8b5cf6",
        "keywords": ["intern", "internship", "training", "placement", "apprenticeship"]
    },
    "achievement": {
        "emoji": "🏆",
        "color": "#f59e0b",
        "keywords": ["award", "achievement", "won", "recognition", "honor", "prize"]
    },
    "academic": {
        "emoji": "🎓",
        "color": "#06b6d4",
        "keywords": ["university", "college", "school", "degree", "gpa", "subject", "course"]
    },
    "resume": {
        "emoji": "📄",
        "color": "#64748b",
        "keywords": ["resume", "cv", "curriculum vitae", "bio", "summary"]
    },
    "portfolio": {
        "emoji": "🖼️",
        "color": "#ec4899",
        "keywords": ["portfolio", "showcase", "gallery", "collection"]
    },
    "other": {
        "emoji": "📁",
        "color": "#7c8195",
        "keywords": []
    }
}

# Relationship Types
RELATIONSHIP_TYPES = {
    "certification_to_skill": {"source": "certification", "target": "skill", "weight": 1.0},
    "skill_to_project": {"source": "skill", "target": "project", "weight": 0.9},
    "project_to_internship": {"source": "project", "target": "internship", "weight": 0.8},
    "internship_to_career": {"source": "internship", "target": "career_path", "weight": 0.85},
    "academic_to_skill": {"source": "academic", "target": "skill", "weight": 0.7},
    "achievement_to_recognition": {"source": "achievement", "target": "recognition", "weight": 1.0}
}

# Timeline Event Types
TIMELINE_EVENT_TYPES = ["certification", "project", "internship", "achievement", "academic"]