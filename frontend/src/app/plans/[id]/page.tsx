"use client";
import { notFound } from "next/navigation";

interface PlanPageProps {
  params: { id: string };
}

import ProtectedRoute from "@/components/ProtectedRoute";

export default function PlanPage({ params }: PlanPageProps) {
  const { id } = params;

  // TODO: fetch plan data via API when backend route is ready
  if (!id) {
    notFound();
  }

  return (
    <ProtectedRoute>
      <section className="space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Plan #{id}</h1>
      <p className="text-muted-foreground">Détails du plan en cours de développement…</p>
    </section>
    </ProtectedRoute>
  );
}
