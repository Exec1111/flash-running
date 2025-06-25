"use client";

import Link from "next/link";
import { useAuth } from "@/context/AuthContext";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "Accueil" },
  { href: "/dashboard", label: "Dashboard" },
];

export default function Navbar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  return (
    <header className="w-full border-b bg-background/60 backdrop-blur supports-[backdrop-filter]:bg-background/40 sticky top-0 z-50">
      <nav className="container mx-auto flex h-14 items-center gap-6 px-4 sm:px-6 lg:px-8">
        <span className="font-semibold text-lg">Flash Running</span>
        <ul className="flex gap-4 text-sm font-medium text-muted-foreground">
          {links.map(({ href, label }) => (
            <li key={href}>
              <Link
                href={href}
                className={cn(
                  "transition-colors hover:text-foreground",
                  pathname === href && "text-foreground"
                )}
              >
                {label}
              </Link>
            </li>
          ))}
        </ul>
        <div className="ml-auto text-sm flex items-center gap-4">
          {!user ? (
            <>
              <Link href="/login" className="hover:underline">
                Connexion
              </Link>
              <Link href="/register" className="hover:underline">
                Inscription
              </Link>
            </>
          ) : (
            <>
              <span>Bonjour {user.name ?? user.email}</span>
              <button onClick={logout} className="hover:underline">
                Déconnexion
              </button>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
