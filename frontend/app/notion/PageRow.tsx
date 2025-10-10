"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { NotionPage } from "@/types";

export default function PageRow({ page }: { page: NotionPage }) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  const handleDelete = async () => {
    if (!confirm(`Удалить "${page.title}" из списка?`)) {
      return;
    }

    setIsDeleting(true);
    try {
      const response = await fetch(`/api/notion-pages/${page.id}`, {
        method: "DELETE",
      });

      if (response.ok) {
        router.refresh();
      } else {
        alert("Не удалось удалить страницу");
      }
    } catch (error) {
      console.error("Error deleting page:", error);
      alert("Ошибка при удалении страницы");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleSync = async () => {
    setIsSyncing(true);
    try {
      const response = await fetch(`/api/notion-pages/${page.id}/sync`, {
        method: "POST",
      });

      if (response.ok) {
        router.refresh();
      } else {
        const data = await response.json();
        alert(data.error || "Не удалось синхронизировать страницу");
      }
    } catch (error) {
      console.error("Error syncing page:", error);
      alert("Ошибка при синхронизации страницы");
    } finally {
      setIsSyncing(false);
    }
  };

  const getStatusBadge = () => {
    switch (page.status) {
      case "synced":
        return <span className="badge badge-success">Синхронизировано</span>;
      case "syncing":
        return <span className="badge badge-info">Синхронизация...</span>;
      case "pending":
        return <span className="badge" style={{ background: "#ffc107", color: "#000" }}>Ожидает</span>;
      case "error":
        return <span className="badge badge-danger">Ошибка</span>;
      default:
        return <span className="badge">{page.status}</span>;
    }
  };

  return (
    <tr>
      <td>
        <div>{page.title}</div>
        {page.error_message && (
          <div style={{ fontSize: "12px", color: "#c33", marginTop: "5px" }}>
            {page.error_message}
          </div>
        )}
      </td>
      <td>{getStatusBadge()}</td>
      <td>
        {page.last_synced
          ? new Date(page.last_synced).toLocaleString("ru-RU")
          : "—"}
      </td>
      <td>{new Date(page.created_at).toLocaleString("ru-RU")}</td>
      <td>
        <div style={{ display: "flex", gap: "5px" }}>
          <button
            onClick={handleSync}
            disabled={isSyncing || page.status === "syncing"}
            className="btn btn-primary"
            style={{ padding: "6px 12px", fontSize: "13px" }}
          >
            {isSyncing || page.status === "syncing" ? "..." : "Синхронизировать"}
          </button>
          <a
            href={page.page_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-secondary"
            style={{ padding: "6px 12px", fontSize: "13px" }}
          >
            Открыть
          </a>
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

