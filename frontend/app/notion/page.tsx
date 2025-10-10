import Link from "next/link";
import { NotionPage } from "@/types";
import AddPageForm from "./AddPageForm";
import PageRow from "./PageRow";

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getNotionPages() {
  try {
    const res = await fetch(`${API_URL}/api/notion-pages`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });

    if (!res.ok) {
      throw new Error("Failed to fetch notion pages");
    }

    return await res.json();
  } catch (error) {
    console.error("Error fetching notion pages:", error);
    return [];
  }
}

export default async function NotionPagesPage() {
  const pages: NotionPage[] = await getNotionPages();

  const syncedPages = pages.filter((p) => p.status === "synced").length;
  const pendingPages = pages.filter((p) => p.status === "pending").length;
  const errorPages = pages.filter((p) => p.status === "error").length;

  return (
    <div>
      <header className="header">
        <div className="container" style={{ position: "relative" }}>
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
            <Link href="/feedback" className="nav-link">
              Отзывы
            </Link>
            <Link href="/users" className="nav-link">
              Пользователи
            </Link>
            <Link href="/notion" className="nav-link active">
              Регламенты
            </Link>
          </nav>
        </div>
      </header>

      <div className="container">
        <h2 style={{ marginBottom: "20px", fontSize: "24px" }}>
          📚 Управление регламентами ({pages.length})
        </h2>

        {/* Stats */}
        <div className="stats">
          <div className="stat-card">
            <div className="stat-value">{pages.length}</div>
            <div className="stat-label">Всего регламентов</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{syncedPages}</div>
            <div className="stat-label">Синхронизировано</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{pendingPages}</div>
            <div className="stat-label">Ожидают синхронизации</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{errorPages}</div>
            <div className="stat-label">Ошибок</div>
          </div>
        </div>

        {/* Add Page Form */}
        <div className="card" style={{ marginBottom: "30px" }}>
          <h3 style={{ marginBottom: "15px" }}>Добавить регламент</h3>
          <p style={{ color: "#666", marginBottom: "15px", fontSize: "14px" }}>
            Вставьте ссылку на страницу Notion, чтобы добавить её в систему
          </p>
          <AddPageForm />
        </div>

        {/* Pages List */}
        {pages.length === 0 ? (
          <div className="empty-state">
            <h3>Регламентов нет</h3>
            <p>Добавьте первый регламент, вставив ссылку на страницу Notion</p>
          </div>
        ) : (
          <div className="table">
            <table>
              <thead>
                <tr>
                  <th>Название и доступные роли</th>
                  <th>Статус</th>
                  <th>Последняя синхронизация</th>
                  <th>Дата добавления</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {pages.map((page) => (
                  <PageRow key={page.id} page={page} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

