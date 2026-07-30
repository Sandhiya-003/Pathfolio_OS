export const OS_FEATURES = [
  {
    title: "AI Ingestion",
    detail:
      "Drop in certificates, resumes, project reports, or internship letters. Text is extracted automatically — PDF, DOCX, or image — with OCR fallback for scanned documents.",
  },
  {
    title: "Intelligent Categorization",
    detail:
      "Every document is classified into Certification, Project, Internship, Achievement, Academic, Resume, or Portfolio — with a visible confidence score, not a black box.",
  },
  {
    title: "Relationship Engine",
    detail:
      "Skills and documents are linked into a knowledge graph. A certification connects to the project it enabled, which connects to the internship that used it.",
  },
  {
    title: "Digital Journey Timeline",
    detail:
      "Documents are grouped by the year extracted from their content, turning a folder of files into a visual career timeline — automatically, with no manual dates to enter.",
  },
  {
    title: "Smart Retrieval",
    detail:
      "Semantic search finds documents by meaning, not just keywords — \"AI projects\" surfaces a document titled something completely different if the content matches.",
  },
  {
    title: "Ask Your Archive",
    detail:
      "A retrieval-augmented assistant answers questions about your own documents in plain language, and cites exactly which ones it used to answer.",
  },
];

export const SECURITY_POINTS = [
  {
    title: "Password hashing",
    detail: "Passwords are hashed with PBKDF2-SHA256. Plaintext is never stored, ever.",
  },
  {
    title: "Per-user data isolation",
    detail:
      "Every document, search, and conversation is scoped to your account at the database layer — not just hidden in the interface. One account can never see another's archive.",
  },
  {
    title: "Session tokens",
    detail: "Authentication uses signed, expiring JWTs. Sessions don't live forever by default.",
  },
  {
    title: "OAuth accounts",
    detail:
      "Signing in with Google or GitHub creates an account with an unusable random password — it can only ever be accessed through that provider, never guessed or brute-forced.",
  },
  {
    title: "Upload limits",
    detail: "File size is capped on every upload to prevent abuse of storage and processing.",
  },
  {
    title: "Original files, untouched",
    detail:
      "Your documents are stored exactly as uploaded. Nothing is re-encoded, compressed, or altered — you can always download the original.",
  },
];

export const MANIFESTO = [
  "Every certificate you've earned, every project you've shipped, every internship that taught you something real — it's scattered. A folder here, an email attachment there, a cloud drive you haven't opened in a year.",
  "Storage platforms can hold those files. None of them understand what they mean, or how they connect to each other, or what story they tell about who you've become.",
  "Pathfolio reads what you upload. It figures out what it is. It connects it to everything else you've built — the certification that led to the project, the project that led to the internship. And when you need any of it back, you don't dig through folders. You just ask.",
  "This is not a place to store your past. It's a system that understands it.",
];