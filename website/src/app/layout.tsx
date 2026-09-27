import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Hermes — Data infrastructure for the modern world",
    template: "%s · Hermes",
  },
  description:
    "Hermes is a data infrastructure SDK for acquiring, normalizing, validating and serving structured and unstructured data — from 10 built-in connectors, through one canonical schema.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
return (
  <html
    lang="en"
    className={`${inter.variable} ${jetbrainsMono.variable}`}
  >
    <body className="min-h-screen bg-midnight text-offwhite antialiased">
      {children}
    </body>
  </html>
);
}
