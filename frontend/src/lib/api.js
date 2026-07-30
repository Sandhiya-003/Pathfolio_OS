const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";
const TOKEN_KEY = "pathfolio_token";

class ApiError extends Error {
  constructor(message, status, details) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

// ---- Token storage ----
function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}
function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

// Notify the app (AuthContext) when a request comes back unauthorized,
// so it can clear state and redirect to /login.
function emitUnauthorized() {
  window.dispatchEvent(new CustomEvent("pathfolio:unauthorized"));
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(path, options = {}, { skipAuthRedirect = false } = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body && !(options.body instanceof FormData)
        ? { "Content-Type": "application/json" }
        : {}),
      ...authHeaders(),
      ...options.headers,
    },
  });

  let payload = null;
  const text = await res.text();
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }

  if (!res.ok) {
    if (res.status === 401 && !skipAuthRedirect) {
      setToken(null);
      emitUnauthorized();
    }
    const message =
      (payload && (payload.error || payload.detail)) ||
      `Request failed with status ${res.status}`;
    throw new ApiError(message, res.status, payload);
  }

  return payload;
}

function qs(params = {}) {
  const usp = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      usp.set(key, value);
    }
  });
  const str = usp.toString();
  return str ? `?${str}` : "";
}

export const api = {
  baseUrl: BASE_URL,
  getToken,
  setToken,

  // ---- Auth ----
  register({ username, email, password, fullName }) {
    return request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, email, password, full_name: fullName || undefined }),
    }, { skipAuthRedirect: true });
  },
  login({ identifier, password }) {
    return request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ identifier, password }),
    }, { skipAuthRedirect: true });
  },
  me() {
    return request("/auth/me", {}, { skipAuthRedirect: true });
  },

  // ---- Upload ----
  uploadSingle(file, onProgress) {
    const form = new FormData();
    form.append("file", file);
    return uploadWithProgress(`${BASE_URL}/upload/single`, form, onProgress);
  },
  uploadBatch(files, onProgress) {
    const form = new FormData();
    files.forEach((f) => form.append("files", f));
    return uploadWithProgress(`${BASE_URL}/upload/batch`, form, onProgress);
  },
  getUploadStats() {
    return request(`/upload/stats`);
  },

  // ---- Documents ----
  listDocuments({ category, limit = 100 } = {}) {
    return request(`/documents/${qs({ category, limit })}`);
  },
  getDocument(docId) {
    return request(`/documents/${docId}`);
  },
  async downloadDocument(docId, suggestedFilename) {
    const res = await fetch(`${BASE_URL}/documents/${docId}/download`, {
      headers: authHeaders(),
    });
    if (!res.ok) {
      if (res.status === 401) {
        setToken(null);
        emitUnauthorized();
      }
      throw new ApiError("Couldn't download the file", res.status);
    }
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = suggestedFilename || "document";
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  },
  deleteDocument(docId) {
    return request(`/documents/${docId}`, { method: "DELETE" });
  },
  getDocumentStats() {
    return request(`/documents/stats`);
  },

  // ---- Search ----
  search(query, { category, limit = 10 } = {}) {
    return request(`/search/${qs({ q: query, category, limit })}`);
  },
  recentDocuments({ limit = 10, category } = {}) {
    return request(`/search/recent${qs({ limit, category })}`);
  },
  documentsBySkill(skill) {
    return request(`/search/by-skill/${encodeURIComponent(skill)}`);
  },

  // ---- Timeline ----
  getTimeline() {
    return request(`/timeline/`);
  },
  getTimelineStats() {
    return request(`/timeline/stats`);
  },
  getTimelineYear(year) {
    return request(`/timeline/year/${year}`);
  },
  getSkillTimeline() {
    return request(`/timeline/skills`);
  },

  // ---- Relationships ----
  getDocumentRelationships(docId) {
    return request(`/relationships/document/${docId}`);
  },
  getRelationshipGraph() {
    return request(`/relationships/graph`);
  },
  getAllSkills() {
    return request(`/relationships/skills`);
  },
  getSkillDetails(skill) {
    return request(`/relationships/skills/${encodeURIComponent(skill)}`);
  },

  // ---- Chat (RAG assistant) ----
  askAssistant(message, history = []) {
    return request(`/chat/`, {
      method: "POST",
      body: JSON.stringify({ message, history }),
    });
  },

  // ---- Insights ----
  getInsights() {
    return request(`/insights/`);
  },
  getSkillInsights() {
    return request(`/insights/skills`);
  },
  getSkillGaps() {
    return request(`/insights/gaps`);
  },
  traceSkillJourney(skill) {
    return request(`/insights/journey/${encodeURIComponent(skill)}`);
  },
  rebuildGraph() {
    return request(`/insights/rebuild-graph`, { method: "POST" });
  },

  // ---- Health (root is outside /api prefix) ----
  async health() {
    const root = BASE_URL.replace(/\/api\/?$/, "");
    const res = await fetch(`${root}/health`);
    if (!res.ok) throw new ApiError("Backend unreachable", res.status);
    return res.json();
  },
};

function uploadWithProgress(url, formData, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url);
    const token = getToken();
    if (token) xhr.setRequestHeader("Authorization", `Bearer ${token}`);

    if (onProgress) {
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          onProgress(Math.round((e.loaded / e.total) * 100));
        }
      };
    }

    xhr.onload = () => {
      let payload = null;
      try {
        payload = JSON.parse(xhr.responseText);
      } catch {
        payload = xhr.responseText;
      }
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(payload);
      } else {
        if (xhr.status === 401) {
          setToken(null);
          emitUnauthorized();
        }
        const message =
          (payload && (payload.error || payload.detail)) ||
          `Upload failed with status ${xhr.status}`;
        reject(new ApiError(message, xhr.status, payload));
      }
    };

    xhr.onerror = () => reject(new ApiError("Network error during upload", 0));
    xhr.send(formData);
  });
}

export { ApiError };
