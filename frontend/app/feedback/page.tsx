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
          <h1>🤖 Notion TG Admin Panel</h1>
          <nav className="nav">
            <Link href="/" className="nav-link">
              Dashboard
            </Link>
            <Link href="/documents" className="nav-link">
              Documents
            </Link>
            <Link href="/query-logs" className="nav-link">
              Query Logs
            </Link>
            <Link href="/feedback" className="nav-link active">
              Feedback
            </Link>
          </nav>
        </div>
      </header>

      <div className="container">
        <h2 style={{ marginBottom: "20px", fontSize: "24px" }}>
          ⭐ User Feedback ({feedback.length})
        </h2>

        {/* Stats */}
        <div className="stats">
          <div className="stat-card">
            <div className="stat-value">{feedback.length}</div>
            <div className="stat-label">Total Feedback</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{goodFeedback}</div>
            <div className="stat-label">👍 Positive</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{badFeedback}</div>
            <div className="stat-label">👎 Negative</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{satisfactionRate}%</div>
            <div className="stat-label">Satisfaction Rate</div>
          </div>
        </div>

        {feedback.length === 0 ? (
          <div className="empty-state">
            <h3>No feedback yet</h3>
            <p>User feedback will appear here</p>
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
                    {fb.rating === "good" ? "👍 Good" : "👎 Bad"}
                  </span>
                  <span className="card-meta">
                    <strong>ID:</strong> {fb.id}
                  </span>
                </div>
                <div className="card-meta">
                  <strong>Time:</strong> {new Date(fb.ts).toLocaleString()}
                  <br />
                  <strong>User ID:</strong> {fb.telegram_user_id}
                  <br />
                  {fb.message_id && (
                    <>
                      <strong>Message ID:</strong> {fb.message_id}
                      <br />
                    </>
                  )}
                  {fb.query_log_id && (
                    <>
                      <strong>Query Log ID:</strong> {fb.query_log_id}
                      <br />
                    </>
                  )}
                </div>
                {fb.comment && (
                  <div className="card-content">
                    <strong>Comment:</strong>
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

