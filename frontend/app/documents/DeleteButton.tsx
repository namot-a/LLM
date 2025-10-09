"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function DeleteButton({ documentId }: { documentId: string }) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!confirm("Вы уверены, что хотите удалить этот документ?")) {
      return;
    }

    setIsDeleting(true);
    try {
      const response = await fetch(`/api/documents/${documentId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        router.refresh();
      } else {
        alert("Не удалось удалить документ");
      }
    } catch (error) {
      console.error("Error deleting document:", error);
      alert("Ошибка при удалении документа");
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

