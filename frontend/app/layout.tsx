import type { Metadata } from "next";
import "./globals.css";
import { Header } from "../components/layout/Header";
import { Sidebar } from "../components/layout/Sidebar";
import { CopilotDrawer } from "../components/copilot/CopilotDrawer";

export const metadata: Metadata = {
  title: "EV Battery Intelligence Platform | Tri-Pillar Diagnostic Suite",
  description: "AI-Driven EV Battery State Estimation, Thermal Safety, and Knee-Point Degradation Prognostics",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0A0D14] text-slate-100 min-h-screen flex flex-col antialiased radial-bg selection:bg-cyan-500/30 selection:text-cyan-200">
        <Header />
        <div className="flex-1 flex">
          <Sidebar />
          <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full overflow-y-auto">
            {children}
          </main>
        </div>
        <CopilotDrawer />
      </body>
    </html>
  );
}
