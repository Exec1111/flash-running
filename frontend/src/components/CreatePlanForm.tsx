"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { fetcher } from "@/lib/api";

export default function CreatePlanForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [goal, setGoal] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await fetcher("/plans", {
        method: "POST",
        body: JSON.stringify({ name, goal }),
      });
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-md mx-auto">
      <div>
        <label className="block text-sm font-medium mb-1">Nom du plan</label>
        <input
          className="w-full rounded border p-2"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Objectif</label>
        <textarea
          className="w-full rounded border p-2"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
        />
      </div>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <button
        type="submit"
        className="bg-primary text-white rounded px-4 py-2 disabled:opacity-50"
        disabled={loading}
      >
        {loading ? "En cours…" : "Créer"}
      </button>
    </form>
  );
}
