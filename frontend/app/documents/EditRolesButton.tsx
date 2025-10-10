"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const AVAILABLE_ROLES = ["Recruiter", "Team Lead", "Head"];

export default function EditRolesButton({ 
  documentId, 
  currentRoles 
}: { 
  documentId: string; 
  currentRoles: string[];
}) {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);
  const [selectedRoles, setSelectedRoles] = useState<string[]>(currentRoles.length > 0 ? currentRoles : ["Recruiter", "Team Lead", "Head"]);
  const [isSaving, setIsSaving] = useState(false);

  const handleRoleToggle = (role: string) => {
    setSelectedRoles(prev => 
      prev.includes(role) 
        ? prev.filter(r => r !== role)
        : [...prev, role]
    );
  };

  const handleSave = async () => {
    if (selectedRoles.length === 0) {
      alert("Выберите хотя бы одну роль");
      return;
    }

    setIsSaving(true);
    try {
      const response = await fetch(`/api/documents/${documentId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ allowed_roles: selectedRoles }),
      });

      if (response.ok) {
        setIsOpen(false);
        router.refresh();
      } else {
        alert("Не удалось обновить роли");
      }
    } catch (error) {
      console.error("Error updating roles:", error);
      alert("Ошибка при обновлении ролей");
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="btn btn-secondary"
        style={{ padding: "6px 12px", fontSize: "13px" }}
      >
        Изменить доступ
      </button>
    );
  }

  return (
    <div style={{
      position: "fixed",
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: "rgba(0,0,0,0.5)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      zIndex: 1000,
    }}>
      <div style={{
        background: "white",
        padding: "30px",
        borderRadius: "8px",
        maxWidth: "500px",
        width: "90%",
      }}>
        <h3 style={{ marginBottom: "20px" }}>Редактировать доступ к документу</h3>
        
        <div style={{ marginBottom: "20px" }}>
          <label style={{ display: "block", marginBottom: "10px", fontWeight: "500" }}>
            Доступ для ролей:
          </label>
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            {AVAILABLE_ROLES.map(role => (
              <label
                key={role}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  cursor: "pointer",
                  padding: "10px",
                  background: selectedRoles.includes(role) ? "#e3f2fd" : "#f5f5f5",
                  border: selectedRoles.includes(role) ? "2px solid #007bff" : "2px solid transparent",
                  borderRadius: "6px",
                  transition: "all 0.2s",
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedRoles.includes(role)}
                  onChange={() => handleRoleToggle(role)}
                  style={{
                    width: "18px",
                    height: "18px",
                    cursor: "pointer",
                  }}
                />
                <span style={{ fontWeight: selectedRoles.includes(role) ? "600" : "400" }}>
                  {role}
                </span>
              </label>
            ))}
          </div>
          <p style={{ fontSize: "12px", color: "#666", marginTop: "10px" }}>
            💡 Роль <strong>Head</strong> всегда имеет доступ ко всем документам
          </p>
        </div>

        <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
          <button
            onClick={() => {
              setSelectedRoles(currentRoles.length > 0 ? currentRoles : ["Recruiter", "Team Lead", "Head"]);
              setIsOpen(false);
            }}
            className="btn btn-secondary"
            disabled={isSaving}
          >
            Отмена
          </button>
          <button
            onClick={handleSave}
            className="btn btn-primary"
            disabled={isSaving}
          >
            {isSaving ? "Сохранение..." : "Сохранить"}
          </button>
        </div>
      </div>
    </div>
  );
}

