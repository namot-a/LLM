"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        router.push("/");
        router.refresh();
      } else {
        setError(data.error || "Неверный логин или пароль");
      }
    } catch (err) {
      setError("Ошибка подключения");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    }}>
      <div style={{
        background: "white",
        padding: "40px",
        borderRadius: "12px",
        boxShadow: "0 10px 40px rgba(0,0,0,0.1)",
        width: "100%",
        maxWidth: "400px",
      }}>
        <h1 style={{
          fontSize: "28px",
          fontWeight: "600",
          marginBottom: "10px",
          textAlign: "center",
          color: "#1a1a1a",
        }}>
          🤖 Admin Panel
        </h1>
        <p style={{
          textAlign: "center",
          color: "#666",
          marginBottom: "30px",
        }}>
          Notion Telegram Bot
        </p>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: "20px" }}>
            <label style={{
              display: "block",
              marginBottom: "8px",
              fontWeight: "500",
              color: "#333",
            }}>
              Логин
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "12px",
                border: "1px solid #ddd",
                borderRadius: "6px",
                fontSize: "16px",
              }}
              placeholder="Введите логин"
            />
          </div>

          <div style={{ marginBottom: "20px" }}>
            <label style={{
              display: "block",
              marginBottom: "8px",
              fontWeight: "500",
              color: "#333",
            }}>
              Пароль
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: "100%",
                padding: "12px",
                border: "1px solid #ddd",
                borderRadius: "6px",
                fontSize: "16px",
              }}
              placeholder="Введите пароль"
            />
          </div>

          {error && (
            <div style={{
              background: "#fee",
              color: "#c33",
              padding: "12px",
              borderRadius: "6px",
              marginBottom: "20px",
              fontSize: "14px",
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: "100%",
              padding: "12px",
              background: loading ? "#ccc" : "#667eea",
              color: "white",
              border: "none",
              borderRadius: "6px",
              fontSize: "16px",
              fontWeight: "500",
              cursor: loading ? "not-allowed" : "pointer",
            }}
          >
            {loading ? "Вход..." : "Войти"}
          </button>
        </form>

        <p style={{
          marginTop: "20px",
          textAlign: "center",
          fontSize: "14px",
          color: "#999",
        }}>
          Доступ только для администраторов
        </p>
      </div>
    </div>
  );
}

