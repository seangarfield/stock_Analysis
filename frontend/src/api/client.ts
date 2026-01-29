const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000/api";

export const apiGet = async <T>(path: string): Promise<T> => {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error("数据源异常");
  }
  return (await response.json()) as T;
};

export const apiPost = async <T, B>(path: string, body: B): Promise<T> => {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error("数据源异常");
  }
  return (await response.json()) as T;
};
