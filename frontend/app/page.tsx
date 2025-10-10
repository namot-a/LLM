import Link from "next/link";
import { Document, QueryLog, Feedback } from "@/types";
import LogoutButton from "./components/LogoutButton";

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getStats() {
  try {
    // Fetch documents
    const docsRes = await fetch(`${API_URL}/api/documents`, { 
      cache: "no-store",
      next: { revalidate: 0 }
    });
    const documents: Document[] = docsRes.ok ? await docsRes.json() : [];

    // Fetch recent query logs
    const logsRes = await fetch(`${API_URL}/api/query-logs?limit=10`, { 
      cache: "no-store",
      next: { revalidate: 0 }
    });
    const queryLogs: QueryLog[] = logsRes.ok ? await logsRes.json() : [];

    // Fetch feedback
    const feedbackRes = await fetch(`${API_URL}/api/feedback?limit=10`, { 
      cache: "no-store",
      next: { revalidate: 0 }
    });
    const feedback: Feedback[] = feedbackRes.ok ? await feedbackRes.json() : [];

    return { documents, queryLogs, feedback };
  } catch (error) {
    console.error("Error fetching stats:", error);
    return { documents: [], queryLogs: [], feedback: [] };
  }
}

export default async function Home() {
  const { documents, queryLogs, feedback } = await getStats();

  // Calculate stats
  const totalDocs = documents.length;
  const totalQueries = queryLogs.length;
  const totalFeedback = feedback.length;
  const goodFeedback = feedback.filter(f => f.rating === "good").length;

  return (
    <div>
      <header className="header">
        <div className="container" style={{ position: "relative" }}>
          <LogoutButton />
          <h1>🤖 Панель управления Notion TG</h1>
          <nav className="nav">
            <Link href="/" className="nav-link active">
              Главная
            </Link>
            <Link href="/documents" className="nav-link">
              Документы
            </Link>
            <Link href="/query-logs" className="nav-link">
              Запросы
            </Link>
            <Link href="/feedback" className="nav-link">
              Отзывы
            </Link>
            <Link href="/users" className="nav-link">
              Пользователи
            </Link>
            <Link href="/notion" className="nav-link">
              Регламенты
            </Link>
          </nav>
        </div>
      </header>

      <div className="container">
        {/* Stats */}
        <div className="stats">
          <div className="stat-card">
            <div className="stat-value">{totalDocs}</div>
            <div className="stat-label">Документов</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{totalQueries}</div>
            <div className="stat-label">Всего запросов</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{totalFeedback}</div>
            <div className="stat-label">Всего отзывов</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">
              {totalFeedback > 0
                ? `${Math.round((goodFeedback / totalFeedback) * 100)}%`
                : "0%"}
            </div>
            <div className="stat-label">Положительных</div>
          </div>
        </div>

        {/* Recent Documents */}
        <section>
          <h2 style={{ marginBottom: "20px", fontSize: "24px" }}>
            📄 Последние документы
          </h2>
          {documents.length === 0 ? (
            <div className="empty-state">
              <h3>Документов пока нет</h3>
              <p>Документы появятся здесь после синхронизации с Notion</p>
            </div>
          ) : (
            <div>
              {documents.slice(0, 5).map((doc) => (
                <div key={doc.id} className="card">
                  <div className="card-title">{doc.title}</div>
                  <div className="card-meta">
                    Последнее изменение: {new Date(doc.last_edited).toLocaleString('ru-RU')}
                  </div>
                  <div className="card-actions">
                    <a
                      href={doc.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-primary"
                    >
                      Открыть в Notion
                    </a>
                    <Link
                      href={`/documents/${doc.id}`}
                      className="btn btn-secondary"
                    >
                      Подробнее
                    </Link>
                  </div>
                </div>
              ))}
              {documents.length > 5 && (
                <Link href="/documents" className="btn btn-primary">
                  Все документы ({documents.length})
                </Link>
              )}
            </div>
          )}
        </section>

        {/* Recent Queries */}
        <section style={{ marginTop: "40px" }}>
          <h2 style={{ marginBottom: "20px", fontSize: "24px" }}>
            💬 Последние запросы
          </h2>
          {queryLogs.length === 0 ? (
            <div className="empty-state">
              <h3>Запросов пока нет</h3>
              <p>Запросы появятся здесь, когда пользователи начнут задавать вопросы</p>
            </div>
          ) : (
            <div>
              {queryLogs.slice(0, 5).map((log) => (
                <div key={log.id} className="card">
                  <div className="card-title">{log.question}</div>
                  <div className="card-meta">
                    {new Date(log.ts).toLocaleString('ru-RU')}
                    {log.username && (
                      <> • Пользователь: {log.username}</>
                    )}
                    {!log.username && log.telegram_user_id && (
                      <> • ID: {log.telegram_user_id}</>
                    )}
                    {log.model && <> • Модель: {log.model}</>}
                  </div>
                  <div className="card-content">
                    {log.answer.substring(0, 200)}
                    {log.answer.length > 200 ? "..." : ""}
                  </div>
                  {log.prompt_tokens && (
                    <div className="card-meta">
                      Токены: {log.prompt_tokens} + {log.completion_tokens} ={" "}
                      {(log.prompt_tokens || 0) + (log.completion_tokens || 0)}
                      {log.cost_usd && <> • Стоимость: ${Number(log.cost_usd).toFixed(4)}</>}
                      {log.processing_time_ms && (
                        <> • Время: {log.processing_time_ms}мс</>
                      )}
                    </div>
                  )}
                </div>
              ))}
              {queryLogs.length > 5 && (
                <Link href="/query-logs" className="btn btn-primary">
                  Все запросы
                </Link>
              )}
            </div>
          )}
        </section>

        {/* Recent Feedback */}
        <section style={{ marginTop: "40px", marginBottom: "40px" }}>
          <h2 style={{ marginBottom: "20px", fontSize: "24px" }}>
            ⭐ Последние отзывы
          </h2>
          {feedback.length === 0 ? (
            <div className="empty-state">
              <h3>Отзывов пока нет</h3>
              <p>Отзывы пользователей появятся здесь</p>
            </div>
          ) : (
            <div>
              {feedback.slice(0, 5).map((fb) => (
                <div key={fb.id} className="card">
                  <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                    <span
                      className={
                        fb.rating === "good" ? "badge badge-success" : "badge badge-danger"
                      }
                    >
                      {fb.rating === "good" ? "👍 Хорошо" : "👎 Плохо"}
                    </span>
                    <span className="card-meta">
                      {new Date(fb.ts).toLocaleString('ru-RU')}
                      {fb.username && <> • {fb.username}</>}
                      {!fb.username && <> • ID: {fb.telegram_user_id}</>}
                    </span>
                  </div>
                  {fb.comment && (
                    <div className="card-content" style={{ marginTop: "10px" }}>
                      {fb.comment}
                    </div>
                  )}
                </div>
              ))}
              {feedback.length > 5 && (
                <Link href="/feedback" className="btn btn-primary">
                  Все отзывы
                </Link>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

