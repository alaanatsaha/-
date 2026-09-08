// Central place for every call to the FastAPI backend.
// Override the backend URL at build time with VITE_API_BASE_URL if the
// API isn't on localhost:8000 (see frontend/.env.example).
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    let detail = "حدث خطأ غير متوقع";
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      // response wasn't JSON — keep the generic message
    }
    throw new ApiError(detail, response.status);
  }

  return response.json();
}

export function fetchCards() {
  return request("/api/cards");
}

export function fetchEmployers() {
  return request("/api/employers");
}

export function createAssessment(payload) {
  return request("/api/assessments", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchAssessment(id) {
  return request(`/api/assessments/${id}`);
}

export function wordReportUrl(id) {
  return `${API_BASE}/api/assessments/${id}/report.docx`;
}

export function pdfReportUrl(id) {
  return `${API_BASE}/api/assessments/${id}/report.pdf`;
}

export { ApiError };
