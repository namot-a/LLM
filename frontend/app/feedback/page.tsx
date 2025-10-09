import Link from "next/link";
import { Feedback } from "@/types";
import DeleteButton from "./DeleteButton";

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getFeedback() {
  try {
    const res = await fetch(`${API_URL}/api/feedback`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });

    if (!res.ok) {
      throw new Error("Failed to fetch feedback");
    }

    return await res.json();
  } catch (error) {
    console.error("Error fetching feedback:", error);
    return [];
  }
}

export default async function FeedbackPage() {
  const feedback: Feedback[] = await getFeedback();

  const goodFeedback = feedback.filter((f) => f.rating === "good").length;
  const badFeedback = feedback.filter((f) => f.rating === "bad").length;
  const satisfactionRate =
    feedback.length > 0
      ? Math.round((goodFeedback / feedback.length) * 100)
      : 0;

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
            <Link href="/query-logs" className="nav-link">
              Запросы
            </Link>
            <Link href="/feedback" className="nav-link active">
              Отзывы
            </Link>
          </nav>
        </div>
      </header>

      <div className="container">
        <h2 style={{ marginBottom: "20px", fontSize: "24px" }}>
          ⭐ Отзывы пользователей ({feedback.length})
        </h2>

        {/* Stats */}
        <div className="stats">
          <div className="stat-card">
            <div className="stat-value">{feedback.length}</div>
            <div className="stat-label">Всего отзывов</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{goodFeedback}</div>
            <div className="stat-label">👍 Положительных</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{badFeedback}</div>
            <div className="stat-label">👎 Отрицательных</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{satisfactionRate}%</div>
            <div className="stat-label">Уровень удовлетворенности</div>
          </div>
        </div>

        {feedback.length === 0 ? (
          <div className="empty-state">
            <h3>Отзывов пока нет</h3>
            <p>Отзывы пользователей появятся здесь</p>
          </div>
        ) : (
          <div>
            {feedback.map((fb) => (
              <div key={fb.id} className="card">
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "10px",
                    marginBottom: "10px",
                  }}
                >
                  <span
                    className={
                      fb.rating === "good"
                        ? "badge badge-success"
                        : "badge badge-danger"
                    }
                  >
                    {fb.rating === "good" ? "👍 Хорошо" : "👎 Плохо"}
                  </span>
                  <span className="card-meta">
                    <strong>ID:</strong> {fb.id}
                  </span>
                </div>
                <div className="card-meta">
                  <strong>Время:</strong> {new Date(fb.ts).toLocaleString('ru-RU')}
                  <br />
                  <strong>ID пользователя:</strong> {fb.telegram_user_id}
                  <br />
                  {fb.message_id && (
                    <>
                      <strong>ID сообщения:</strong> {fb.message_id}
                      <br />
                    </>
                  )}
                  {fb.query_log_id && (
                    <>
                      <strong>ID запроса:</strong> {fb.query_log_id}
                      <br />
                    </>
                  )}
                </div>
                {fb.comment && (
                  <div className="card-content">
                    <strong>Комментарий:</strong>
                    <br />
                    {fb.comment}
                  </div>
                )}
                <div className="card-actions">
                  <DeleteButton feedbackId={fb.id} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
