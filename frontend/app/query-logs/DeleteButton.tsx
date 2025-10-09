"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function DeleteButton({ logId }: { logId: number }) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!confirm("Вы уверены, что хотите удалить этот запрос?")) {
      return;
    }

    setIsDeleting(true);
    try {
      const response = await fetch(`/api/query-logs/${logId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        router.refresh();
      } else {
        alert("Не удалось удалить запрос");
      }
    } catch (error) {
      console.error("Error deleting query log:", error);
      alert("Ошибка при удалении запроса");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <button
      onClick={handleDelete}
      disabled={isDeleting}
      className="btn btn-danger"
    >
      {isDeleting ? "Удаление..." : "Удалить"}
    </button>
  );
}

