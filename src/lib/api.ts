export async function api(url: string, options: RequestInit = {}) {
  const base = "https://range-lvzt.onrender.com"; // ← твоє API
  const access = sessionStorage.getItem("access");

  const res = await fetch(`${base}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: access ? `Bearer ${access}` : "",
      ...(options.headers || {}),
    },
    body: options.body ? options.body : undefined,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "API error");
  }

  return res.json();
}
