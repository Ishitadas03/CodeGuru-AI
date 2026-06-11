"use client";

import React, { useEffect, useRef } from "react";
import { ReactLenis } from "@studio-freight/react-lenis";
import { useMousePosition } from "@/hooks/useMousePosition";
import { useUIStore } from "@/store/uiStore";
import { motion } from "framer-motion";
import { usePathname } from "next/navigation";
import { gsap } from "gsap";

const Lenis = ReactLenis as any;

export default function PageWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const mouse = useMousePosition();
  const cursorType = useUIStore((state) => state.cursorType);
  const ringRef = useRef<HTMLDivElement>(null);
  const dotRef = useRef<HTMLDivElement>(null);

  // Position cursor using requestAnimationFrame for smooth movement
  useEffect(() => {
    const ring = ringRef.current;
    const dot = dotRef.current;
    if (!ring || !dot) return;

    let ringX = 0;
    let ringY = 0;
    let dotX = 0;
    let dotY = 0;

    const tick = () => {
      // Lerp ring position (lag behind mouse by 0.15)
      ringX += (mouse.x - ringX) * 0.15;
      ringY += (mouse.y - ringY) * 0.15;

      // Snappy dot position
      dotX += (mouse.x - dotX) * 0.45;
      dotY += (mouse.y - dotY) * 0.45;

      ring.style.transform = `translate3d(${ringX}px, ${ringY}px, 0) translate(-50%, -50%)`;
      dot.style.transform = `translate3d(${dotX}px, ${dotY}px, 0) translate(-50%, -50%)`;

      requestAnimationFrame(tick);
    };

    const animId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animId);
  }, [mouse]);

  // Page fade transition effect using GSAP when pathname changes
  useEffect(() => {
    gsap.fromTo(
      ".page-transition-container",
      { opacity: 0, scale: 0.99 },
      { opacity: 1, scale: 1, duration: 0.4, ease: "power2.out" }
    );
  }, [pathname]);

  return (
    <Lenis root options={{ lerp: 0.1, duration: 1.2, smoothWheel: true }}>
      {/* Custom Cursor Ring & Dot */}
      <div 
        ref={ringRef} 
        className={`custom-cursor-ring hidden md:block ${cursorType !== "default" ? "active" : ""}`}
      />
      <div 
        ref={dotRef} 
        className="custom-cursor-dot hidden md:block"
      />

      {/* Main Page Layout Wrapper */}
      <div className="page-transition-container min-h-screen flex flex-col relative z-10">
        {children}
      </div>
    </Lenis>
  );
}
