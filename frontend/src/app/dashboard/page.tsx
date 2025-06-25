"use client";
import PlansList from "@/components/PlansList";
import Link from "next/link";

import ProtectedRoute from "@/components/ProtectedRoute";

export default function Dashboard() {
  return (
    <ProtectedRoute>
      <section className="space-y-6">
      <div className="flex justify-end">
        <Link
          href="/plans/new"
          className="bg-primary text-white rounded px-4 py-2 hover:opacity-90"
        >
          + Créer un plan
        </Link>
      </div>
      <h1 className="text-3xl font-bold tracking-tight">Tableau de bord</h1>
      <PlansList />
      <p className="text-muted-foreground">
        Ici apparaîtront vos plans d’entraînement. (À venir)
      </p>
    </section>
    </ProtectedRoute>
  );
}
