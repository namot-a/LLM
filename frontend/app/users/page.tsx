import Link from "next/link";
import { TelegramUser } from "@/types";
import AddUserForm from "./AddUserForm";
import UserRow from "./UserRow";

const API_URL = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getTelegramUsers() {
  try {
    const res = await fetch(`${API_URL}/api/telegram-users`, {
      cache: "no-store",
      next: { revalidate: 0 },
    });

    if (!res.ok) {
      throw new Error("Failed to fetch telegram users");
    }

    return await res.json();
  } catch (error) {
    console.error("Error fetching telegram users:", error);
    return [];
  }
}

export default async function UsersPage() {
  const users: TelegramUser[] = await getTelegramUsers();

  const activeUsers = users.filter((u) => u.is_active).length;
  const headUsers = users.filter((u) => u.role === "Head").length;

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
            <Link href="/users" className="nav-link active">
              Пользователи
            </Link>
          </nav>
        </div>
      </header>

      <div className="container">
        <h2 style={{ marginBottom: "20px", fontSize: "24px" }}>
          👥 Управление пользователями ({users.length})
        </h2>

        {/* Stats */}
        <div className="stats">
          <div className="stat-card">
            <div className="stat-value">{users.length}</div>
            <div className="stat-label">Всего пользователей</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{activeUsers}</div>
            <div className="stat-label">Активных</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{headUsers}</div>
            <div className="stat-label">Head</div>
          </div>
        </div>

        {/* Add User Form */}
        <div className="card" style={{ marginBottom: "30px" }}>
          <h3 style={{ marginBottom: "20px" }}>Добавить пользователя</h3>
          <AddUserForm />
        </div>

        {/* Users List */}
        {users.length === 0 ? (
          <div className="empty-state">
            <h3>Пользователей нет</h3>
            <p>Добавьте первого пользователя, чтобы он мог использовать бота</p>
          </div>
        ) : (
          <div className="table">
            <table>
              <thead>
                <tr>
                  <th>User ID</th>
                  <th>Username</th>
                  <th>Роль</th>
                  <th>Статус</th>
                  <th>Дата добавления</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <UserRow key={user.user_id} user={user} />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

