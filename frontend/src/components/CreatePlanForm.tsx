"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function CreatePlanForm() {
  const router = useRouter();
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.post("/plans/generate", { prompt });
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
        <label htmlFor="prompt" className="block text-sm font-medium mb-1">Décrivez votre objectif</label>
        <textarea
          id="prompt"
          className="w-full rounded border p-2 min-h-[120px]"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Ex: Un plan pour courir mon premier marathon en 16 semaines, avec 3 séances par semaine."
          required
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
