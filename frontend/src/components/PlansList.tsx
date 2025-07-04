"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface Session {
  id: number;
  date: string;
}

export interface TrainingPlan {
  id: number;
  name: string;
  goal: string;
  start_date: string;
  end_date: string;
  sessions: Session[];
}

export default function PlansList() {
  const [plans, setPlans] = useState<TrainingPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<TrainingPlan[]>("/plans")
      .then((res) => {
        setPlans(res.data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Chargement…</p>;
  if (error) return <p className="text-red-600">Erreur: {error}</p>;
  if (plans.length === 0) return <p>Aucun plan trouvé.</p>;

  return (
    <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {plans.map((plan) => (
        <Link href={`/plans/${plan.id}`} key={plan.id}>
          <li className="mb-2 p-4 border rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 cursor-pointer transition-colors">
            <h3 className="text-xl font-semibold">{plan.name}</h3>
            <p className="text-gray-600 dark:text-gray-400">{plan.goal}</p>
          </li>
        </Link>
      ))}
    </ul>
  );
}
