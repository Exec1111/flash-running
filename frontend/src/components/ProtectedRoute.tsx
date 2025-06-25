"use client";

import { ReactNode, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";

interface ProtectedRouteProps {
  children: ReactNode;
}

/**
 * Composant de garde. Redirige vers /login si l'utilisateur n'est pas authentifié.
 */
export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { token } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!token) {
      router.replace("/login");
    }
  }, [token, router]);

  if (!token) return null;
  return <>{children}</>;
}
