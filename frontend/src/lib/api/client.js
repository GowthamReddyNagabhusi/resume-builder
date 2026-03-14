const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
    this.token = null;
  }

  setToken(token) {
    this.token = token;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}/api${endpoint}`;

    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(url, { ...options, headers });

    if (!response.ok) {
      let message = `HTTP ${response.status}`;
      try {
        const body = await response.json();
        message = body.detail || body.error?.message || message;
      } catch { /* non-JSON error body */ }
      const err = new Error(message);
      err.status = response.status;
      throw err;
    }

    // 204 No Content
    if (response.status === 204) return null;
    return response.json();
  }

  // ── Auth ────────────────────────────────────────────────────────
  register(email, password, name) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    });
  }

  login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  getCurrentUser() {
    return this.request('/auth/me');
  }

  refreshToken(refreshToken) {
    return this.request('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }

  // ── Career Data ─────────────────────────────────────────────────
  getCareerSummary() {
    return this.request('/career/summary');
  }

  createEducation(data) {
    return this.request('/career/education', { method: 'POST', body: JSON.stringify(data) });
  }
  getEducation() { return this.request('/career/education'); }
  deleteEducation(id) {
    return this.request(`/career/education/${id}`, { method: 'DELETE' });
  }

  createExperience(data) {
    return this.request('/career/experience', { method: 'POST', body: JSON.stringify(data) });
  }
  getExperience() { return this.request('/career/experience'); }
  deleteExperience(id) {
    return this.request(`/career/experience/${id}`, { method: 'DELETE' });
  }

  createSkill(data) {
    return this.request('/career/skills', { method: 'POST', body: JSON.stringify(data) });
  }
  getSkills() { return this.request('/career/skills'); }
  deleteSkill(id) {
    return this.request(`/career/skills/${id}`, { method: 'DELETE' });
  }

  createProject(data) {
    return this.request('/career/projects', { method: 'POST', body: JSON.stringify(data) });
  }
  getProjects() { return this.request('/career/projects'); }
  deleteProject(id) {
    return this.request(`/career/projects/${id}`, { method: 'DELETE' });
  }

  createCertification(data) {
    return this.request('/career/certifications', { method: 'POST', body: JSON.stringify(data) });
  }
  getCertifications() { return this.request('/career/certifications'); }
  deleteCertification(id) {
    return this.request(`/career/certifications/${id}`, { method: 'DELETE' });
  }

  // ── Achievements ────────────────────────────────────────────────
  createAchievement(data) {
    return this.request('/career/achievements', { method: 'POST', body: JSON.stringify(data) });
  }
  getAchievements() { return this.request('/career/achievements'); }
  deleteAchievement(id) {
    return this.request(`/career/achievements/${id}`, { method: 'DELETE' });
  }

  // ── Platform Links ─────────────────────────────────────────────
  createPlatform(data) {
    return this.request('/career/platforms', { method: 'POST', body: JSON.stringify(data) });
  }
  getPlatforms() { return this.request('/career/platforms'); }
  deletePlatform(id) {
    return this.request(`/career/platforms/${id}`, { method: 'DELETE' });
  }

  // ── Resumes ──────────────────────────────────────────────────────
  generateResume(jobDescription, templateId, title) {
    return this.request('/resume/generate', {
      method: 'POST',
      body: JSON.stringify({
        job_role: title || `Resume – ${new Date().toLocaleDateString()}`,
        job_description: jobDescription,
      }),
    });
  }

  getResumes() { return this.request('/resume/list'); }

  getResumeDownloadUrl(resumeId) {
    return `${this.baseURL}/api/resume/download/${resumeId}`;
  }

  // ── Dynamic Resume ──────────────────────────────────────────────
  generateDynamicResume(config) {
    return this.request('/dynamic-resume/generate', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  getResumeHistory() { return this.request('/dynamic-resume/history'); }

  getDynamicResumeDownloadUrl(resumeId) {
    return `${this.baseURL}/api/dynamic-resume/download/${resumeId}`;
  }

  // ── Integrations ─────────────────────────────────────────────────
  getIntegrations() { return this.request('/integrations/'); }
  connectPlatform(platform, accessToken) {
    return this.request(`/integrations/${platform}/connect`, {
      method: 'POST',
      body: JSON.stringify({ access_token: accessToken }),
    });
  }
  syncPlatform(platform) {
    return this.request(`/integrations/${platform}/sync`, { method: 'POST' });
  }

  // ── Templates ────────────────────────────────────────────────────
  getTemplates() { return this.request('/templates/'); }

  // ── AI ────────────────────────────────────────────────────────────
  getAIStatus() { return this.request('/ai/status'); }

  generateCoverLetter(data) {
    return this.request('/ai/cover-letter', { method: 'POST', body: JSON.stringify(data) });
  }

  improveResume(data) {
    return this.request('/ai/improve-resume', { method: 'POST', body: JSON.stringify(data) });
  }

  scoreResume(data) {
    return this.request('/ai/score-resume', { method: 'POST', body: JSON.stringify(data) });
  }
}

export const apiClient = new APIClient();
