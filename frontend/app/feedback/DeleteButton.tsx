"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function DeleteButton({ feedbackId }: { feedbackId: number }) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!confirm("Вы уверены, что хотите удалить этот отзыв?")) {
      return;
    }

    setIsDeleting(true);
    try {
      const response = await fetch(`/api/feedback/${feedbackId}`, {
        method: "DELETE",
      });

      if (response.ok) {
        router.refresh();
      } else {
        alert("Не удалось удалить отзыв");
      }
    } catch (error) {
      console.error("Error deleting feedback:", error);
      alert("Ошибка при удалении отзыва");
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

