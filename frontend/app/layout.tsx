"use client";

import React, { useEffect } from "react";
import "./globals.css";
import { useFleetStore } from "../lib/store/useFleetStore";
import { Header } from "../components/layout/Header";
import { Sidebar } from "../components/layout/Sidebar";
import { CopilotDrawer } from "../components/copilot/CopilotDrawer";
import { OfflineBanner } from "../components/ui/OfflineBanner";
import { FallbackAuditDrawer } from "../components/ui/FallbackAuditDrawer";
import { usePathname } from "next/navigation";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { theme } = useFleetStore();
  const pathname = usePathname();
  const isDashboard = pathname.startsWith("/dashboard");
  const [mounted, setMounted] = React.useState(false);

  useEffect(() => {
    setMounted(true);
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [theme]);

  return (
    <html lang="en" suppressHydrationWarning className={mounted && theme === "dark" ? "dark" : ""}>
      <head>
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <title>EV Battery Intelligence Platform</title>
      </head>
      <body suppressHydrationWarning className="min-h-screen flex flex-col antialiased transition-colors selection:bg-cyan-500/20 selection:text-cyan-800 dark:selection:text-cyan-200">
        <OfflineBanner />
        {isDashboard ? (
          <>
            <Header />
            <div className="flex-1 flex">
              <Sidebar />
              <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full overflow-y-auto">
                {children}
              </main>
            </div>
            <CopilotDrawer />
            <FallbackAuditDrawer />
          </>
        ) : (
          // Landing page renders without dashboard sidebar
          <main className="flex-1 w-full">{children}</main>
        )}
      </body>
    </html>
  );
}
