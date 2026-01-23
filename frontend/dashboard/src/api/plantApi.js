const API_URL = "http://localhost:8001";

async function handleResponse(res) {
  const json = await res.json();

  if (!res.ok) {
    const message = json?.error?.message || `Request failed (${res.status})`;
    throw new Error(message);
  }

  return json.data;
}

export async function getPlantInfo() {
  const res = await fetch(`${API_URL}/plant`);
  const data = await handleResponse(res);
  return data;
}

export async function waterPlant(durationSeconds) {
  const res = await fetch(`${API_URL}/water`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ duration_seconds: durationSeconds }),
  });

  return handleResponse(res);
}