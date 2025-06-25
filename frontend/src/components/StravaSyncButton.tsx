"use client";

import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";

interface StravaSyncResult {
  imported: number;
  updated: number;
}

export default function StravaSyncButton() {
  const { token } = useAuth();
  const { toast } = useToast();
  const [isLoading, setIsLoading] = useState(false);

  const handleSync = async () => {
    if (!token) {
      toast({ title: "Erreur", description: "Vous devez être connecté.", variant: "destructive" });
      return;
    }

    setIsLoading(true);
    try {
      const response = await api.post<StravaSyncResult>("/strava/sync", {}, { headers: { Authorization: `Bearer ${token}` } });
      const { imported, updated } = response.data;
      toast({
        title: "Synchronisation Strava réussie",
        description: `${imported} activité(s) importée(s), ${updated} mise(s) à jour.`,
      });
    } catch (error: any) {
      console.error("Erreur de synchronisation Strava:", error);
      const errorMessage = error.response?.data?.detail || "Une erreur est survenue.";
      toast({ title: "Échec de la synchronisation", description: errorMessage, variant: "destructive" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button onClick={handleSync} disabled={isLoading}>
      {isLoading ? "Synchronisation..." : "Synchroniser avec Strava"}
    </Button>
  );
}
