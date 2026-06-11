"use client";

import React, { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

interface ScoreRingProps {
  score: number; // 0 to 100
  className?: string;
}

function TorusMesh({ score }: { score: number }) {
  const meshRef = useRef<THREE.Mesh>(null);

  // Normalize score
  const scoreVal = Math.max(0, Math.min(100, score));
  
  // Calculate arc angle (0 to 2*PI)
  const arc = (scoreVal / 100) * Math.PI * 2;

  // Determine color based on score
  const color = useMemo(() => {
    if (scoreVal <= 40) return "#F472B6"; // Rose
    if (scoreVal <= 70) return "#FBBF24"; // Amber
    return "#5B6CF9"; // Indigo
  }, [scoreVal]);

  useFrame((state) => {
    if (meshRef.current) {
      // Gentle spin
      meshRef.current.rotation.y = Math.sin(state.clock.getElapsedTime() * 0.5) * 0.15;
      meshRef.current.rotation.z = state.clock.getElapsedTime() * 0.2;
    }
  });

  return (
    <group rotation={[Math.PI / 2, 0, 0]}>
      {/* Background Torus (full ring) */}
      <mesh>
        <torusGeometry args={[1.5, 0.2, 16, 100, Math.PI * 2]} />
        <meshBasicMaterial color="#0B0F20" transparent={true} opacity={0.65} />
      </mesh>

      {/* Foreground Torus (score length) */}
      <mesh ref={meshRef}>
        <torusGeometry args={[1.5, 0.22, 16, 100, arc]} />
        <meshPhongMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.5}
          shininess={100}
        />
      </mesh>
    </group>
  );
}

export default function ScoreRing({ score = 85, className }: ScoreRingProps) {
  return (
    <div className={`w-full h-full flex items-center justify-center relative select-none ${className || "min-h-[200px]"}`}>
      <Canvas
        camera={{ position: [0, 0, 4.5], fov: 45 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.3} />
        <pointLight position={[5, 5, 5]} intensity={1.5} color="#F0F4FF" />
        <TorusMesh score={score} />
      </Canvas>
    </div>
  );
}
