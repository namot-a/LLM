"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export default function DeleteButton({ documentId }: { documentId: string }) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this document?")) {
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
        alert("Failed to delete document");
      }
    } catch (error) {
      console.error("Error deleting document:", error);
      alert("Error deleting document");
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

