import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Pendaftaran Kapita Gereja",
  description: "Formulir pendaftaran kapita gereja",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}
