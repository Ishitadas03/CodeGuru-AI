"use client";

import React, { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

interface PointsSetProps {
  color: string;
  count: number;
}

function PointsSet({ color, count }: PointsSetProps) {
  const pointsRef = useRef<THREE.Points>(null);

  // Generate random coordinates and movement factors
  const [positions, speeds] = useMemo(() => {
    const coords = new Float32Array(count * 3);
    const rates = new Float32Array(count);

    for (let i = 0; i < count; i++) {
      // Wide flat spread
      coords[i * 3] = (Math.random() - 0.5) * 16;     // x
      coords[i * 3 + 1] = (Math.random() - 0.5) * 12; // y
      coords[i * 3 + 2] = (Math.random() - 0.5) * 8;  // z
      rates[i] = 0.005 + Math.random() * 0.012;       // speed
    }

    return [coords, rates];
  }, [count]);

  useFrame(() => {
    if (!pointsRef.current) return;
    
    const geom = pointsRef.current.geometry;
    const positionsAttr = geom.getAttribute("position") as THREE.BufferAttribute;
    
    // Slow rotation
    pointsRef.current.rotation.y += 0.0004;

    // Drifts upward, reset at top boundary
    for (let i = 0; i < count; i++) {
      let y = positionsAttr.getY(i);
      y += speeds[i];
      if (y > 6) {
        y = -6; // reset at bottom
      }
      positionsAttr.setY(i, y);
    }
    positionsAttr.needsUpdate = true;
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        color={color}
        size={0.05}
        transparent={true}
        opacity={0.35}
        sizeAttenuation={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

function Particles() {
  return (
    <group>
      <PointsSet color="#5B6CF9" count={75} />
      <PointsSet color="#22D3EE" count={75} />
    </group>
  );
}

export default function ParticleField() {
  return (
    <div className="absolute inset-0 w-full h-full pointer-events-none select-none z-0">
      <Canvas
        camera={{ position: [0, 0, 5], fov: 60 }}
        gl={{ alpha: true, antialias: true }}
      >
        <Particles />
      </Canvas>
    </div>
  );
}
