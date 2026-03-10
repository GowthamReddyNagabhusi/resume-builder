// Shared API client for the CareerForge frontend
const API = "http://localhost:8000";

export function getToken() {
  if (typeof window === "undefined") return "";
  return localStorage.getItem("career_token") || "";
}

export function setToken(token) {
  if (typeof window === "undefined") return;
  localStorage.setItem("career_token", token || "");
}

export function clearToken() {
  if (typeof window === "undefined") return;
  localStorage.removeItem("career_token");
}

export async function apiFetch(path, options = {}) {
  const token = getToken();
  const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json", ...authHeaders, ...options.headers },
    ...options,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `HTTP ${res.status}`);
  }
  return res.json();
}

async function downloadWithAuth(path, fallbackFilename = "download.bin") {
  const token = getToken();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const res = await fetch(`${API}${path}`, { method: "GET", headers });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `HTTP ${res.status}`);
  }

  const blob = await res.blob();
  const disposition = res.headers.get("content-disposition") || "";
  const match = disposition.match(/filename="?([^";]+)"?/i);
  const filename = match?.[1] || fallbackFilename;

  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

export const api = {
  // Auth
  signup: (data) => apiFetch("/api/auth/signup", { method: "POST", body: data }),
  login: (data) => apiFetch("/api/auth/login", { method: "POST", body: data }),
  me: () => apiFetch("/api/auth/me"),
  logout: () => apiFetch("/api/auth/logout", { method: "POST" }),

  // Profile wizard
  getProfile: () => apiFetch("/api/profile/me"),
  saveSetup: (data) => apiFetch("/api/profile/setup", { method: "POST", body: data }),

  // Templates / dynamic resumes
  listTemplates: () => apiFetch("/api/templates"),
  uploadTemplate: async (file) => {
    const token = getToken();
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API}/api/templates/upload`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });
    if (!res.ok) {
      throw new Error(await res.text());
    }
    return res.json();
  },
  generateDynamicResume: (data) => apiFetch("/api/dynamic-resume/generate", { method: "POST", body: data }),
  resumeHistory: () => apiFetch("/api/dynamic-resume/history"),
  dynamicDownloadUrl: (id) => `${API}/api/dynamic-resume/download/${id}`,
  downloadDynamicResume: (id) => downloadWithAuth(`/api/dynamic-resume/download/${id}`, `resume_${id}.docx`),

  // Platform sync
  syncPlatforms: () => apiFetch("/api/platforms/sync", { method: "POST" }),
  getPlatformData: () => apiFetch("/api/platforms/data"),

  // Stats
  getStats:        () => apiFetch("/api/stats"),
  refreshStats:    () => apiFetch("/api/stats/refresh", { method: "POST" }),

  // AI
  aiStatus:        () => apiFetch("/api/ai/status"),
  aiGenerate:      (prompt, model) => apiFetch("/api/ai/generate", { method: "POST", body: { prompt, model: model || "" } }),
  aiCoverLetter:   (data) => apiFetch("/api/ai/cover-letter", { method: "POST", body: data }),
  aiImprove:       (data) => apiFetch("/api/ai/improve-resume", { method: "POST", body: data }),

  // Resume
  generateResume:  (data) => apiFetch("/api/resume/generate", { method: "POST", body: data }),
  listResumes:     () => apiFetch("/api/resume/list"),
  downloadUrl:     (id) => `${API}/api/resume/download/${id}`,

  // GitHub
  importGitHub:    (username) => apiFetch(`/api/github/import/${username}`),
  listProjects:    (all = false) => apiFetch(`/api/github/projects?all=${all}`),
  toggleProject:   (id, show) => apiFetch(`/api/github/projects/${id}`, { method: "PUT", body: { show } }),

  // Jobs
  listJobs:        () => apiFetch("/api/jobs"),
  createJob:       (data) => apiFetch("/api/jobs", { method: "POST", body: data }),
  updateJob:       (id, data) => apiFetch(`/api/jobs/${id}`, { method: "PUT", body: data }),
  deleteJob:       (id) => apiFetch(`/api/jobs/${id}`, { method: "DELETE" }),
};
