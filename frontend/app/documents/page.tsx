import Link from "next/link";
import { Document } from "@/types";
import DeleteButton from "./DeleteButton";

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getDocuments() {
  try {
    const res = await fetch(`${API_URL}/api/documents`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });

    if (!res.ok) {
      throw new Error("Failed to fetch documents");
    }

    return await res.json();
  } catch (error) {
    console.error("Error fetching documents:", error);
    return [];
  }
}

export default async function DocumentsPage() {
  const documents: Document[] = await getDocuments();

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
        <h2 style={{ marginBottom: "20px", fontSize: "24px" }}>
          📄 All Documents ({documents.length})
        </h2>

        {documents.length === 0 ? (
          <div className="empty-state">
            <h3>No documents found</h3>
            <p>Documents will appear here after Notion sync</p>
          </div>
        ) : (
          <div>
            {documents.map((doc) => (
              <div key={doc.id} className="card">
                <div className="card-title">{doc.title}</div>
                <div className="card-meta">
                  <strong>ID:</strong> {doc.id}
                  <br />
                  <strong>Notion Page ID:</strong> {doc.notion_page_id}
                  <br />
                  <strong>Last edited:</strong>{" "}
                  {new Date(doc.last_edited).toLocaleString()}
                  <br />
                  <strong>Created:</strong>{" "}
                  {new Date(doc.created_at).toLocaleString()}
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
                  <DeleteButton documentId={doc.id} />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

