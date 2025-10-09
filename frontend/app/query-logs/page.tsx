import Link from "next/link";
import { QueryLog } from "@/types";
import DeleteButton from "./DeleteButton";

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
            <Link href="/query-logs" className="nav-link active">
              Query Logs
            </Link>
            <Link href="/feedback" className="nav-link">
              Feedback
            </Link>
          </nav>
        </div>
      </header>

      <div className="container">
        <h2 style={{ marginBottom: "20px", fontSize: "24px" }}>
          💬 Query Logs ({queryLogs.length})
        </h2>

        {/* Stats */}
        <div className="stats">
          <div className="stat-card">
            <div className="stat-value">{queryLogs.length}</div>
            <div className="stat-label">Total Queries</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{totalTokens.toLocaleString()}</div>
            <div className="stat-label">Total Tokens</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">${totalCost.toFixed(2)}</div>
            <div className="stat-label">Total Cost</div>
          </div>
        </div>

        {queryLogs.length === 0 ? (
          <div className="empty-state">
            <h3>No query logs found</h3>
            <p>Query logs will appear here when users ask questions</p>
          </div>
        ) : (
          <div>
            {queryLogs.map((log) => (
              <div key={log.id} className="card">
                <div className="card-title">{log.question}</div>
                <div className="card-meta">
                  <strong>ID:</strong> {log.id}
                  <br />
                  <strong>Time:</strong> {new Date(log.ts).toLocaleString()}
                  <br />
                  {log.telegram_user_id && (
                    <>
                      <strong>User ID:</strong> {log.telegram_user_id}
                      <br />
                    </>
                  )}
                  {log.model && (
                    <>
                      <strong>Model:</strong> {log.model}
                      <br />
                    </>
                  )}
                </div>
                <div className="card-content">
                  <strong>Answer:</strong>
                  <br />
                  {log.answer}
                </div>
                {log.prompt_tokens && (
                  <div className="card-meta">
                    <strong>Tokens:</strong> {log.prompt_tokens} prompt +{" "}
                    {log.completion_tokens} completion ={" "}
                    {(log.prompt_tokens || 0) + (log.completion_tokens || 0)}{" "}
                    total
                    {log.cost_usd && (
                      <>
                        {" "}
                        • <strong>Cost:</strong> ${Number(log.cost_usd).toFixed(4)}
                      </>
                    )}
                    {log.processing_time_ms && (
                      <>
                        {" "}
                        • <strong>Time:</strong> {log.processing_time_ms}ms
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
      </div>
    </div>
  );
}

