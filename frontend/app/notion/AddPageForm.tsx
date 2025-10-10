"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";

const AVAILABLE_ROLES = ["Recruiter", "Team Lead", "Head"];

export default function AddPageForm() {
  const router = useRouter();
  const [pageUrl, setPageUrl] = useState("");
  const [selectedRoles, setSelectedRoles] = useState<string[]>(["Recruiter", "Team Lead", "Head"]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleRoleToggle = (role: string) => {
    setSelectedRoles(prev => 
      prev.includes(role) 
        ? prev.filter(r => r !== role)
        : [...prev, role]
    );
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");

    if (!pageUrl.includes("notion.so")) {
      setError("Неверный формат URL. Используйте ссылку на страницу Notion");
      return;
    }

    if (selectedRoles.length === 0) {
      setError("Выберите хотя бы одну роль");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("/api/notion-pages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          page_url: pageUrl,
          allowed_roles: selectedRoles,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setPageUrl("");
        setSelectedRoles(["Recruiter", "Team Lead", "Head"]);
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
      <div style={{ marginBottom: "15px" }}>
        <label style={{ display: "block", marginBottom: "5px", fontWeight: "500" }}>
          Ссылка на страницу Notion
        </label>
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

      <div style={{ marginBottom: "15px" }}>
        <label style={{ display: "block", marginBottom: "10px", fontWeight: "500" }}>
          Доступ для ролей (роль Head автоматически имеет доступ ко всем регламентам)
        </label>
        <div style={{ display: "flex", gap: "15px", flexWrap: "wrap" }}>
          {AVAILABLE_ROLES.map(role => (
            <label
              key={role}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                cursor: "pointer",
                padding: "8px 12px",
                background: selectedRoles.includes(role) ? "#e3f2fd" : "#f5f5f5",
                border: selectedRoles.includes(role) ? "2px solid #007bff" : "2px solid transparent",
                borderRadius: "6px",
                transition: "all 0.2s",
              }}
            >
              <input
                type="checkbox"
                checked={selectedRoles.includes(role)}
                onChange={() => handleRoleToggle(role)}
                style={{
                  width: "18px",
                  height: "18px",
                  cursor: "pointer",
                }}
              />
              <span style={{ fontWeight: selectedRoles.includes(role) ? "600" : "400" }}>
                {role}
              </span>
            </label>
          ))}
        </div>
        <p style={{ fontSize: "12px", color: "#666", marginTop: "8px" }}>
          💡 Роль <strong>Head</strong> всегда имеет доступ ко всем регламентам, независимо от выбранных ролей
        </p>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="btn btn-primary"
      >
        {loading ? "Добавление..." : "Добавить регламент"}
      </button>

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
