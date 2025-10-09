"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { TelegramUser } from "@/types";

export default function UserRow({ user }: { user: TelegramUser }) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  const handleDelete = async () => {
    if (!confirm(`Удалить пользователя ${user.username || user.user_id}?`)) {
      return;
    }

    setIsDeleting(true);
    try {
      const response = await fetch(`/api/telegram-users/${user.user_id}`, {
        method: "DELETE",
      });

      if (response.ok) {
        router.refresh();
      } else {
        alert("Не удалось удалить пользователя");
      }
    } catch (error) {
      console.error("Error deleting user:", error);
      alert("Ошибка при удалении пользователя");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleToggleStatus = async () => {
    setIsToggling(true);
    try {
      const response = await fetch(`/api/telegram-users/${user.user_id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !user.is_active }),
      });

      if (response.ok) {
        router.refresh();
      } else {
        alert("Не удалось изменить статус");
      }
    } catch (error) {
      console.error("Error toggling status:", error);
      alert("Ошибка при изменении статуса");
    } finally {
      setIsToggling(false);
    }
  };

  return (
    <tr>
      <td>{user.user_id}</td>
      <td>{user.username || "—"}</td>
      <td>
        <span className={user.role === "admin" ? "badge badge-info" : "badge badge-success"}>
          {user.role === "admin" ? "Администратор" : "Пользователь"}
        </span>
      </td>
      <td>
        <span className={user.is_active ? "badge badge-success" : "badge badge-danger"}>
          {user.is_active ? "Активен" : "Заблокирован"}
        </span>
      </td>
      <td>{new Date(user.created_at).toLocaleString('ru-RU')}</td>
      <td>
        <div style={{ display: "flex", gap: "5px" }}>
          <button
            onClick={handleToggleStatus}
            disabled={isToggling}
            className="btn btn-secondary"
            style={{ padding: "6px 12px", fontSize: "13px" }}
          >
            {isToggling ? "..." : (user.is_active ? "Заблокировать" : "Активировать")}
          </button>
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="btn btn-danger"
            style={{ padding: "6px 12px", fontSize: "13px" }}
          >
            {isDeleting ? "..." : "Удалить"}
          </button>
        </div>
      </td>
    </tr>
  );
}

