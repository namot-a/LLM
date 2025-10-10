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
            <h1>🤖 Панель управления Notion TG</h1>
            <nav className="nav">
              <Link href="/" className="nav-link">
                Главная
              </Link>
              <Link href="/documents" className="nav-link active">
                Документы
              </Link>
              <Link href="/query-logs" className="nav-link">
                Запросы
              </Link>
              <Link href="/feedback" className="nav-link">
                Отзывы
              </Link>
            </nav>
          </div>
        </header>

        <div className="container">
          <div className="error">Документ не найден</div>
          <Link href="/documents" className="btn btn-primary">
            ← Назад к документам
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div>
      <header className="header">
        <div className="container">
          <h1>🤖 Панель управления Notion TG</h1>
          <nav className="nav">
            <Link href="/" className="nav-link">
              Главная
            </Link>
            <Link href="/documents" className="nav-link active">
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
        <Link href="/documents" className="btn btn-secondary" style={{ marginBottom: "20px" }}>
          ← Назад к документам
        </Link>

        <div className="card">
          <h2 style={{ marginBottom: "20px" }}>{document.title}</h2>
          <div className="card-meta">
            <strong>ID:</strong> {document.id}
            <br />
            <strong>Notion Page ID:</strong> {document.notion_page_id}
            <br />
            <strong>Последнее изменение:</strong> {new Date(document.last_edited).toLocaleString('ru-RU')}
            <br />
            <strong>Создан:</strong> {new Date(document.created_at).toLocaleString('ru-RU')}
            <br />
            <strong>Обновлен:</strong> {new Date(document.updated_at).toLocaleString('ru-RU')}
          </div>
          <div className="card-actions">
            <a
              href={document.url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
            >
              Открыть в Notion
            </a>
          </div>
        </div>

        <h3 style={{ marginTop: "40px", marginBottom: "20px", fontSize: "20px" }}>
          Текстовые фрагменты ({chunks.length})
        </h3>

        {chunks.length === 0 ? (
          <div className="empty-state">
            <h3>Фрагменты не найдены</h3>
            <p>У этого документа пока нет проиндексированных фрагментов</p>
          </div>
        ) : (
          <div>
            {chunks.map((chunk) => (
              <div key={chunk.id} className="card">
                {chunk.heading_path && (
                  <div className="card-title">{chunk.heading_path}</div>
                )}
                <div className="card-meta">
                  <strong>Фрагмент #{chunk.chunk_index + 1}</strong> • ID: {chunk.id}
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

