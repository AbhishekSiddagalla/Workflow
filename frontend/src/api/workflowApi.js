import { BASE_URL, API_ENDPOINTS } from "./config";

export async function fetchTemplates() {
  const response = await fetch(`${BASE_URL}${API_ENDPOINTS.TEMPLATES}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch templates");
  }

  return response.json();
}

export async function saveWorkflow(payload) {
  const response = await fetch(`${BASE_URL}${API_ENDPOINTS.WORKFLOWS}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify(payload),
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.message || "Failed to save workflow");
  }

  return data;
}
