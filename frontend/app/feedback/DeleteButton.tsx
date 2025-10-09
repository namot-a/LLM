"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function DeleteButton({ feedbackId }: { feedbackId: number }) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this feedback?")) {
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
        alert("Failed to delete feedback");
      }
    } catch (error) {
      console.error("Error deleting feedback:", error);
      alert("Error deleting feedback");
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
      {isDeleting ? "Deleting..." : "Delete"}
    </button>
  );
}

