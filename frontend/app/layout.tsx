import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Notion TG Admin",
  description: "Admin panel for Notion Telegram Bot",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

