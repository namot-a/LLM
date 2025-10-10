"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { QueryLog } from "@/types";

export default function FailedQueriesPage() {
  const [failedLogs, setFailedLogs] = useState<QueryLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchFailed() {
      try {
        const response = await fetch("/api/query-logs?failed_only=true");
        const data = await response.json();
        setFailedLogs(data);
      } catch (error) {
        console.error("Error fetching failed logs:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchFailed();
  }, []);

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: "20px", display: "flex", gap: "10px", alignItems: "center" }}>
        <Link href="/query-logs" className="btn btn-secondary">
          ← Все запросы
        </Link>
        <h3 style={{ margin: 0 }}>Запросы без ответа ({failedLogs.length})</h3>
      </div>

      {failedLogs.length === 0 ? (
        <div className="empty-state">
          <h3>🎉 Нет запросов без ответа!</h3>
          <p>Все пользователи получили ответы на свои вопросы</p>
        </div>
      ) : (
        <div>
          {failedLogs.map((log) => (
            <div key={log.id} className="card" style={{ borderLeft: "4px solid #dc3545" }}>
              <div className="card-title">{log.question}</div>
              <div className="card-meta">
                <strong>Время:</strong> {new Date(log.ts).toLocaleString('ru-RU')}
                <br />
                {log.username ? (
                  <>
                    <strong>Пользователь:</strong> {log.username}
                    <br />
                  </>
                ) : log.telegram_user_id ? (
                  <>
                    <strong>ID пользователя:</strong> {log.telegram_user_id}
                    <br />
                  </>
                ) : null}
              </div>
              <div className="card-content">
                <strong>Ответ бота:</strong>
                <br />
                {log.answer}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

