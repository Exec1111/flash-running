"use client";
import { createContext, useContext, useEffect, useState } from "react";
import { api } from "@/lib/api";

interface User {
  id: number;
  email: string;
  name?: string | null;
}

interface AuthContextValue {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, name: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() =>
    typeof window !== "undefined" ? localStorage.getItem("token") : null
  );
  const [user, setUser] = useState<User | null>(() => {
    if (typeof window !== "undefined") {
      const saved = localStorage.getItem("user");
      return saved ? (JSON.parse(saved) as User) : null;
    }
    return null;
  });

  useEffect(() => {
    if (token) localStorage.setItem("token", token);
    else localStorage.removeItem("token");
  }, [token]);

  useEffect(() => {
    if (user) localStorage.setItem("user", JSON.stringify(user));
    else localStorage.removeItem("user");
  }, [user]);

  async function login(email: string, password: string) {
    const response = await api.post<{ access_token: string; user: User }>(
      "/login",
      { email, password }
    );
    setToken(response.data.access_token);
    setUser(response.data.user);
  }

  async function register(email: string, name: string, password: string) {
    const response = await api.post<{ access_token: string; user: User }>(
      "/register",
      { email, name, password }
    );
    setToken(response.data.access_token);
    setUser(response.data.user);
  }

  function logout() {
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
