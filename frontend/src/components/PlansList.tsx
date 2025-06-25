"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetcher } from "@/lib/api";

interface Session {
  id: number;
  date: string;
}

export interface TrainingPlan {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  sessions: Session[];
}

export default function PlansList() {
  const [plans, setPlans] = useState<TrainingPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetcher<TrainingPlan[]>("/plans")
      .then((data) => setPlans(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Chargement…</p>;
  if (error) return <p className="text-red-600">Erreur: {error}</p>;
  if (plans.length === 0) return <p>Aucun plan trouvé.</p>;

  return (
    <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {plans.map((plan) => (
        <li
          key={plan.id}
          className="rounded border p-4 hover:shadow transition cursor-pointer"
        >
          <h3 className="font-semibold mb-2">{plan.name}</h3>
        </li>
      ))}
    </ul>
  );
}
