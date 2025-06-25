"use client";
import CreatePlanForm from "@/components/CreatePlanForm";

import ProtectedRoute from "@/components/ProtectedRoute";

export default function NewPlanPage() {
  return (
    <ProtectedRoute>
      <section className="space-y-6 py-8">
      <h1 className="text-3xl font-bold tracking-tight">Créer un plan</h1>
      <CreatePlanForm />
    </section>
    </ProtectedRoute>
  );
}
