"use client";

import { useRouter } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function StravaConnectButton() {
  const handleConnect = async () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    if (!token) return;
    const res = await fetch(`${API_BASE}/strava/connect-url`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) {
      alert("Erreur d'authentification Strava");
      return;
    }
    const data: { url: string } = await res.json();
    window.location.href = data.url;
  };

  return (
    <button
      onClick={handleConnect}
      className="bg-orange-600 text-white rounded px-4 py-2 hover:opacity-90"
    >
      Connecter Strava
    </button>
  );
}
