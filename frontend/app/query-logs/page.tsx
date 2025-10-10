import Link from "next/link";
import { QueryLog } from "@/types";
import DeleteButton from "./DeleteButton";
import FailedQueriesPage from "./FailedQueriesPage";

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getQueryLogs() {
  try {
    const res = await fetch(`${API_URL}/api/query-logs`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });

    if (!res.ok) {
      throw new Error("Failed to fetch query logs");
    }

    return await res.json();
  } catch (error) {
    console.error("Error fetching query logs:", error);
    return [];
  }
}

export default async function QueryLogsPage() {
  const queryLogs: QueryLog[] = await getQueryLogs();

  // Calculate totals
  const totalTokens = queryLogs.reduce(
    (sum, log) => sum + (log.prompt_tokens || 0) + (log.completion_tokens || 0),
    0
  );
  const totalCost = queryLogs.reduce(
    (sum, log) => sum + Number(log.cost_usd || 0),
    0
  );
  const failedQueries = queryLogs.filter(log => log.has_answer === false).length;

  return (
    <div>
      <header className="header">
        <div className="container">
          <h1>🤖 Панель управления Notion TG</h1>
          <nav className="nav">
            <Link href="/" className="nav-link">
              Главная
            </Link>
            <Link href="/documents" className="nav-link">
              Документы
            </Link>
            <Link href="/query-logs" className="nav-link active">
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
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
          <h2 style={{ fontSize: "24px", margin: 0 }}>
            💬 Журнал запросов ({queryLogs.length})
          </h2>
          {failedQueries > 0 && (
            <Link 
              href="#failed" 
              className="btn btn-danger"
              style={{ textDecoration: "none" }}
            >
              ⚠️ Без ответа: {failedQueries}
            </Link>
          )}
        </div>

        {/* Stats */}
        <div className="stats">
          <div className="stat-card">
            <div className="stat-value">{queryLogs.length}</div>
            <div className="stat-label">Всего запросов</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{failedQueries}</div>
            <div className="stat-label">Без ответа</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{totalTokens.toLocaleString('ru-RU')}</div>
            <div className="stat-label">Всего токенов</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">${totalCost.toFixed(2)}</div>
            <div className="stat-label">Общая стоимость</div>
          </div>
        </div>

        {queryLogs.length === 0 ? (
          <div className="empty-state">
            <h3>Запросов не найдено</h3>
            <p>Запросы появятся здесь, когда пользователи начнут задавать вопросы</p>
          </div>
        ) : (
          <div>
            {queryLogs.map((log) => (
              <div key={log.id} className="card">
                <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "10px", flexWrap: "wrap" }}>
                  <div className="card-title" style={{ marginBottom: 0, flex: 1 }}>{log.question}</div>
                  {log.has_answer === false && (
                    <span className="badge badge-danger" style={{ fontSize: "12px" }}>
                      ⚠️ Без ответа
                    </span>
                  )}
                </div>
                <div className="card-meta">
                  <strong>ID:</strong> {log.id}
                  <br />
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
                  {log.model && (
                    <>
                      <strong>Модель:</strong> {log.model}
                      <br />
                    </>
                  )}
                </div>
                <div className="card-content">
                  <strong>Ответ:</strong>
                  <br />
                  {log.answer}
                </div>
                {log.prompt_tokens && (
                  <div className="card-meta">
                    <strong>Токены:</strong> {log.prompt_tokens} промпт +{" "}
                    {log.completion_tokens} ответ ={" "}
                    {(log.prompt_tokens || 0) + (log.completion_tokens || 0)}{" "}
                    всего
                    {log.cost_usd && (
                      <>
                        {" "}
                        • <strong>Стоимость:</strong> ${Number(log.cost_usd).toFixed(4)}
                      </>
                    )}
                    {log.processing_time_ms && (
                      <>
                        {" "}
                        • <strong>Время:</strong> {log.processing_time_ms}мс
                      </>
                    )}
                  </div>
                )}
                <div className="card-actions">
                  <DeleteButton logId={log.id} />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Failed Queries Section */}
        {failedQueries > 0 && (
          <section id="failed" style={{ marginTop: "60px" }}>
            <FailedQueriesPage />
          </section>
        )}
      </div>
    </div>
  );
}
