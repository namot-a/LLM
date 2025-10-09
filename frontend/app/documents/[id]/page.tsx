import Link from "next/link";
import { Document, Chunk } from "@/types";

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getDocument(id: string) {
  try {
    const res = await fetch(`${API_URL}/api/documents/${id}`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });

    if (!res.ok) {
      return null;
    }

    return await res.json();
  } catch (error) {
    console.error("Error fetching document:", error);
    return null;
  }
}

async function getChunks(documentId: string) {
  try {
    const res = await fetch(`${API_URL}/api/chunks/document/${documentId}`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });

    if (!res.ok) {
      return [];
    }

    return await res.json();
  } catch (error) {
    console.error("Error fetching chunks:", error);
    return [];
  }
}

export default async function DocumentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const document: Document | null = await getDocument(id);
  const chunks: Chunk[] = document ? await getChunks(id) : [];

  if (!document) {
    return (
      <div>
        <header className="header">
          <div className="container">
            <h1>🤖 Notion TG Admin Panel</h1>
            <nav className="nav">
              <Link href="/" className="nav-link">
                Dashboard
              </Link>
              <Link href="/documents" className="nav-link active">
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
          <div className="error">Document not found</div>
          <Link href="/documents" className="btn btn-primary">
            ← Back to Documents
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      <header className="header">
        <div className="container">
          <h1>🤖 Notion TG Admin Panel</h1>
          <nav className="nav">
            <Link href="/" className="nav-link">
              Dashboard
            </Link>
            <Link href="/documents" className="nav-link active">
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
        <Link href="/documents" className="btn btn-secondary" style={{ marginBottom: "20px" }}>
          ← Back to Documents
        </Link>

        <div className="card">
          <h2 style={{ marginBottom: "20px" }}>{document.title}</h2>
          <div className="card-meta">
            <strong>ID:</strong> {document.id}
            <br />
            <strong>Notion Page ID:</strong> {document.notion_page_id}
            <br />
            <strong>Last edited:</strong> {new Date(document.last_edited).toLocaleString()}
            <br />
            <strong>Created:</strong> {new Date(document.created_at).toLocaleString()}
            <br />
            <strong>Updated:</strong> {new Date(document.updated_at).toLocaleString()}
          </div>
          <div className="card-actions">
            <a
              href={document.url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
            >
              Open in Notion
            </a>
          </div>
        </div>

        <h3 style={{ marginTop: "40px", marginBottom: "20px", fontSize: "20px" }}>
          Text Chunks ({chunks.length})
        </h3>

        {chunks.length === 0 ? (
          <div className="empty-state">
            <h3>No chunks found</h3>
            <p>This document has no indexed chunks yet</p>
          </div>
        ) : (
          <div>
            {chunks.map((chunk) => (
              <div key={chunk.id} className="card">
                {chunk.heading_path && (
                  <div className="card-title">{chunk.heading_path}</div>
                )}
                <div className="card-meta">
                  <strong>Chunk #{chunk.chunk_index + 1}</strong> • ID: {chunk.id}
                </div>
                <div className="card-content">{chunk.content}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

