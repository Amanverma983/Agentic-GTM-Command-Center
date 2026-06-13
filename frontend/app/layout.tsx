import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Agentic GTM Command Center",
  description: "Autonomous SDR and Go-To-Market workspace. Research leads, evaluate ICP qualify criteria, prepare buyer personas, generate custom outreach, address objections, map CRM database logs, and forecast deal probabilities.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} min-h-screen text-slate-100 antialiased`}>
        {children}
      </body>
    </html>
  );
}
