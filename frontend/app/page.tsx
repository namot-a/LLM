import Link from "next/link";
import { Document, QueryLog, Feedback } from "@/types";

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
        <div className="container">
          <h1>🤖 Notion TG Admin Panel</h1>
          <nav className="nav">
            <Link href="/" className="nav-link active">
              Dashboard
            </Link>
            <Link href="/documents" className="nav-link">
              Documents
            </Link>
            <Link href="/query-logs" className="nav-link">
              Query Logs
            </Link>
            <Link href="/feedback" className="nav-link">
              Feedback
            </Link>
          </nav>
        </div>
      </header>

      <div className="container">
        {/* Stats */}
        <div className="stats">
          <div className="stat-card">
            <div className="stat-value">{totalDocs}</div>
            <div className="stat-label">Documents</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{totalQueries}</div>
            <div className="stat-label">Total Queries</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{totalFeedback}</div>
            <div className="stat-label">Total Feedback</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">
              {totalFeedback > 0
                ? `${Math.round((goodFeedback / totalFeedback) * 100)}%`
                : "0%"}
            </div>
            <div className="stat-label">Positive Feedback</div>
          </div>
        </div>

        {/* Recent Documents */}
        <section>
          <h2 style={{ marginBottom: "20px", fontSize: "24px" }}>
            📄 Recent Documents
          </h2>
          {documents.length === 0 ? (
            <div className="empty-state">
              <h3>No documents yet</h3>
              <p>Documents will appear here after Notion sync</p>
            </div>
          ) : (
            <div>
              {documents.slice(0, 5).map((doc) => (
                <div key={doc.id} className="card">
                  <div className="card-title">{doc.title}</div>
                  <div className="card-meta">
                    Last edited: {new Date(doc.last_edited).toLocaleString()}
                  </div>
                  <div className="card-actions">
                    <a
                      href={doc.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn btn-primary"
                    >
                      Open in Notion
                    </a>
                    <Link
                      href={`/documents/${doc.id}`}
                      className="btn btn-secondary"
                    >
                      View Details
                    </Link>
                  </div>
                </div>
              ))}
              {documents.length > 5 && (
                <Link href="/documents" className="btn btn-primary">
                  View All Documents ({documents.length})
                </Link>
              )}
            </div>
          )}
        </section>

        {/* Recent Queries */}
        <section style={{ marginTop: "40px" }}>
          <h2 style={{ marginBottom: "20px", fontSize: "24px" }}>
            💬 Recent Queries
          </h2>
          {queryLogs.length === 0 ? (
            <div className="empty-state">
              <h3>No queries yet</h3>
              <p>Query logs will appear here when users ask questions</p>
            </div>
          ) : (
            <div>
              {queryLogs.slice(0, 5).map((log) => (
                <div key={log.id} className="card">
                  <div className="card-title">{log.question}</div>
                  <div className="card-meta">
                    {new Date(log.ts).toLocaleString()}
                    {log.telegram_user_id && (
                      <> • User ID: {log.telegram_user_id}</>
                    )}
                    {log.model && <> • Model: {log.model}</>}
                  </div>
                  <div className="card-content">
                    {log.answer.substring(0, 200)}
                    {log.answer.length > 200 ? "..." : ""}
                  </div>
                  {log.prompt_tokens && (
                    <div className="card-meta">
                      Tokens: {log.prompt_tokens} + {log.completion_tokens} ={" "}
                      {(log.prompt_tokens || 0) + (log.completion_tokens || 0)}
                      {log.cost_usd && <> • Cost: ${Number(log.cost_usd).toFixed(4)}</>}
                      {log.processing_time_ms && (
                        <> • Time: {log.processing_time_ms}ms</>
                      )}
                    </div>
                  )}
                </div>
              ))}
              {queryLogs.length > 5 && (
                <Link href="/query-logs" className="btn btn-primary">
                  View All Queries
                </Link>
              )}
            </div>
          )}
        </section>

        {/* Recent Feedback */}
        <section style={{ marginTop: "40px", marginBottom: "40px" }}>
          <h2 style={{ marginBottom: "20px", fontSize: "24px" }}>
            ⭐ Recent Feedback
          </h2>
          {feedback.length === 0 ? (
            <div className="empty-state">
              <h3>No feedback yet</h3>
              <p>User feedback will appear here</p>
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
                      {fb.rating === "good" ? "👍 Good" : "👎 Bad"}
                    </span>
                    <span className="card-meta">
                      {new Date(fb.ts).toLocaleString()} • User ID:{" "}
                      {fb.telegram_user_id}
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
                  View All Feedback
                </Link>
              )}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

