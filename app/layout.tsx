import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "QuantumGuard | Control Center",
  description: "Post-Quantum Container Logging Proxy",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
