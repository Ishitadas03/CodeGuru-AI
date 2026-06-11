import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Providers from "@/components/providers/Providers";
import AetherBackground from "@/components/three/AetherBackground";
import AuroraOrbs from "@/components/layout/AuroraOrbs";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "CodeGuru AI — Your Intelligent Coding Mentor",
  description:
    "An AI-powered full-stack coding platform to review your code, teach DSA problems, simulate technical interviews, and track your study analytics.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} font-sans min-h-screen antialiased relative`}>
        <AetherBackground />
        <AuroraOrbs />
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
