"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";

export default function AddPageForm() {
  const router = useRouter();
  const [pageUrl, setPageUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");

    if (!pageUrl.includes("notion.so")) {
      setError("Неверный формат URL. Используйте ссылку на страницу Notion");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("/api/notion-pages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ page_url: pageUrl }),
      });

      const data = await response.json();

      if (response.ok) {
        setPageUrl("");
        router.refresh();
      } else {
        setError(data.error || "Не удалось добавить страницу");
      }
    } catch (err) {
      setError("Ошибка при добавлении страницы");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ display: "flex", gap: "10px", alignItems: "end" }}>
        <div style={{ flex: 1 }}>
          <input
            type="url"
            value={pageUrl}
            onChange={(e) => setPageUrl(e.target.value)}
            required
            placeholder="https://www.notion.so/Page-Title-abc123..."
            style={{
              width: "100%",
              padding: "10px",
              border: "1px solid #ddd",
              borderRadius: "6px",
              fontSize: "14px",
            }}
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn btn-primary"
          style={{ marginBottom: "0" }}
        >
          {loading ? "Добавление..." : "Добавить"}
        </button>
      </div>

      {error && (
        <div style={{
          marginTop: "10px",
          padding: "10px",
          background: "#fee",
          color: "#c33",
          borderRadius: "6px",
          fontSize: "14px",
        }}>
          {error}
        </div>
      )}
    </form>
  );
}

