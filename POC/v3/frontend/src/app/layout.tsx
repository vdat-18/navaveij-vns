import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Sidebar } from "@/components/Sidebar";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Navaveij ROC Dashboard",
  description: "Clinical AI Recommendation Orchestration Center",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased selection:bg-teal-accent selection:text-navy-950`}
      >
        <Sidebar />
        <main className="pl-64 min-h-screen bg-white">
          <div className="w-full">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
