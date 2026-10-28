import type { Metadata, Viewport } from "next";
import { ThemeProvider } from "next-themes";
import { IBM_Plex_Sans } from "next/font/google";
import "./globals.css";

const plex = IBM_Plex_Sans({ subsets: ["latin"], weight: ["400", "500", "600", "700"], variable: "--font-sans", display: "swap" });
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
  title: "Sieve: repair copilot for hospital equipment technicians",
  description:
    "Photograph a dead oxygen concentrator. Sieve finds the manual page, walks the fix with safety stops, checks recalls and files the work order. Offline-capable, open NVIDIA Nemotron models on Nebius Token Factory.",
  manifest: "/manifest.webmanifest",
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#f8f9fa" },
    { media: "(prefers-color-scheme: dark)", color: "#0f1419" },
  ],
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className={plex.variable}>
      <body className="min-h-dvh bg-bg text-fg antialiased">
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:left-2 focus:top-2 focus:z-50 focus:rounded focus:bg-accent focus:px-3 focus:py-2 focus:text-white">
            Skip to content
          </a>
          <SiteHeader />
          <main id="main" className="mx-auto min-h-dvh w-full max-w-[1100px] px-4 pb-24 sm:px-6">
            {children}
          </main>
          <SiteFooter />
        </ThemeProvider>
      </body>
    </html>
  );
}
