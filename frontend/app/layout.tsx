import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Virgo-Eye — Chain-of-Visual-Thought Diagnostic Engine",
  description:
    "Reasoning-first multimodal diagnostics. Spatial mapping → CoVT deliberation → critic verification → calibrated verdict.",
  icons: {
    icon: [
      { url: "/icon.svg", type: "image/svg+xml" },
      { url: "/favicon.ico", sizes: "any" },
    ],
    apple: "/apple-icon.png",
  },
  themeColor: "#16a34a",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}