"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";

export default function AddUserForm() {
  const router = useRouter();
  const [userId, setUserId] = useState("");
  const [username, setUsername] = useState("");
  const [role, setRole] = useState("Recruiter");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");

    if (!userId || isNaN(Number(userId))) {
      setError("User ID должен быть числом");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("/api/telegram-users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: Number(userId),
          username: username || null,
          role,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setUserId("");
        setUsername("");
        setRole("Recruiter");
        router.refresh();
      } else {
        setError(data.error || "Не удалось добавить пользователя");
      }
    } catch (err) {
      setError("Ошибка при добавлении пользователя");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr auto", gap: "10px", alignItems: "end" }}>
        <div>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "500" }}>
            User ID *
          </label>
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            required
            placeholder="123456789"
            style={{
              width: "100%",
              padding: "8px",
              border: "1px solid #ddd",
              borderRadius: "6px",
            }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "500" }}>
            Username
          </label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="@username"
            style={{
              width: "100%",
              padding: "8px",
              border: "1px solid #ddd",
              borderRadius: "6px",
            }}
          />
        </div>

        <div>
          <label style={{ display: "block", marginBottom: "5px", fontWeight: "500" }}>
            Роль
          </label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            style={{
              width: "100%",
              padding: "8px",
              border: "1px solid #ddd",
              borderRadius: "6px",
            }}
          >
            <option value="Recruiter">Recruiter</option>
            <option value="Team Lead">Team Lead</option>
            <option value="Head">Head</option>
          </select>
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

