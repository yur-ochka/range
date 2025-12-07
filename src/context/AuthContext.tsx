"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { api } from "@/lib/api";

interface User {
  email: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // ------------------------------
  // LOAD PROFILE
  // ------------------------------
  async function loadProfile() {
    try {
      const profile = await api("/api/users/profile/");
      setUser(profile);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadProfile();
  }, []);

  // ------------------------------
  // LOGIN
  // ------------------------------
  async function login(email: string, password: string) {
    const res = await api("/api/users/login/", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    sessionStorage.setItem("access", res.access);
    localStorage.setItem("refresh", res.refresh);

    await loadProfile();
  }

  // ------------------------------
  // LOGOUT
  // ------------------------------
  function logout() {
    sessionStorage.removeItem("access");
    localStorage.removeItem("refresh");
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be inside <AuthProvider>");
  return ctx;
}
