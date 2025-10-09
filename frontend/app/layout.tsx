import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Providers from "./providers";
import { Analytics } from "@vercel/analytics/react";
import { ColorModeScript } from "@chakra-ui/react";
import { themeConfig } from "@/theme/config";
import Navbar from "@/components/Navbar";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AI Data Analytics Platform",
  description: "AI-powered data analytics with natural language queries and intelligent visualizations",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Only enable Vercel Web Analytics when running on Vercel.
  // This avoids 404s for /_vercel/insights/script.js on other platforms.
  const enableVercelAnalytics = process.env.VERCEL === '1' || Boolean(process.env.VERCEL_ANALYTICS_ID);
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        <ColorModeScript initialColorMode={themeConfig.initialColorMode} />
        <Providers>
          <Navbar />
          {children}
          {enableVercelAnalytics && <Analytics />}
        </Providers>
      </body>
    </html>
  );
}
