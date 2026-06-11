"use client";

import React, { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { useUIStore } from "@/store/uiStore";

interface AlgoVisualizerProps {
  mode?: "sorting" | "tree" | "graph";
  array?: number[];
  comparing?: number[];
  sorted?: number[];
}

// 1. Sorting Visualizer component
function SortingScene({ array = [4, 2, 7, 5, 1, 6, 3], comparing = [], sorted = [] }: { array?: number[]; comparing?: number[]; sorted?: number[] }) {
  const groupRef = useRef<THREE.Group>(null);
  const spacing = 1.2;
  const startX = -((array.length - 1) * spacing) / 2;

  useFrame((state) => {
    if (groupRef.current) {
      // Gentle floating sway
      groupRef.current.rotation.y = Math.sin(state.clock.getElapsedTime() * 0.4) * 0.25 + 0.3;
    }
  });

  return (
    <group ref={groupRef} position={[0, -1, 0]}>
      {array.map((value, idx) => {
        const xPos = startX + idx * spacing;
        const height = value * 0.6;
        
        // Color coding based on state
        let color = "rgba(244, 114, 182, 0.7)"; // Unsorted: Rose
        if (comparing.includes(idx)) color = "rgba(251, 191, 36, 0.8)"; // Comparing: Amber
        if (sorted.includes(idx)) color = "rgba(34, 211, 238, 0.8)"; // Sorted: Teal

        return (
          <mesh key={idx} position={[xPos, height / 2, 0]}>
            <boxGeometry args={[0.7, height, 0.7]} />
            <meshPhongMaterial
              color={color}
              emissive={color}
              emissiveIntensity={0.2}
              shininess={100}
            />
          </mesh>
        );
      })}
      {/* Platform ground */}
      <mesh position={[0, -0.1, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[14, 4]} />
        <meshStandardMaterial color="#0B0F20" roughness={0.8} />
      </mesh>
    </group>
  );
}

// 2. BST Tree Visualizer component
function TreeScene() {
  const groupRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.15;
    }
  });

  // Nodes positions [x, y, z]
  const nodes = [
    { pos: [0, 2, 0], val: "8" },
    { pos: [-2, 0.5, 0], val: "4" },
    { pos: [2, 0.5, 0], val: "12" },
    { pos: [-3, -1, 0], val: "2" },
    { pos: [-1, -1, 0], val: "6" },
    { pos: [1, -1, 0], val: "10" },
    { pos: [3, -1, 0], val: "14" },
  ];

  // Connections connecting nodes
  const lines = [
    { start: [0, 2, 0], end: [-2, 0.5, 0] },
    { start: [0, 2, 0], end: [2, 0.5, 0] },
    { start: [-2, 0.5, 0], end: [-3, -1, 0] },
    { start: [-2, 0.5, 0], end: [-1, -1, 0] },
    { start: [2, 0.5, 0], end: [1, -1, 0] },
    { start: [2, 0.5, 0], end: [3, -1, 0] },
  ];

  return (
    <group ref={groupRef}>
      {/* Connectors */}
      {lines.map((line, idx) => {
        const startVec = new THREE.Vector3(...line.start);
        const endVec = new THREE.Vector3(...line.end);
        const points = [startVec, endVec];
        const lineGeom = new THREE.BufferGeometry().setFromPoints(points);

        return (
          <line key={idx}>
            <bufferGeometry attach="geometry" {...lineGeom} />
            <lineBasicMaterial color="#5B6CF9" opacity={0.3} transparent={true} />
          </line>
        );
      })}

      {/* Nodes spheres */}
      {nodes.map((node, idx) => (
        <mesh key={idx} position={node.pos as any}>
          <sphereGeometry args={[0.35, 32, 32]} />
          <meshPhongMaterial
            color={idx === 0 ? "#9B59F5" : "#5B6CF9"}
            emissive={idx === 0 ? "#9B59F5" : "#5B6CF9"}
            emissiveIntensity={0.3}
          />
        </mesh>
      ))}
    </group>
  );
}

// 3. Force Directed Graph visualizer component
function GraphScene() {
  const groupRef = useRef<THREE.Group>(null);
  
  const points = useMemo(() => {
    const tempPoints = [];
    for (let i = 0; i < 35; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(Math.random() * 2 - 1);
      const r = 2.5 + Math.random() * 1.5;
      
      const x = r * Math.sin(phi) * Math.cos(theta);
      const y = r * Math.sin(phi) * Math.sin(theta);
      const z = r * Math.cos(phi);
      tempPoints.push(new THREE.Vector3(x, y, z));
    }
    return tempPoints;
  }, []);

  const connections = useMemo(() => {
    const tempConns: Array<{ start: THREE.Vector3; end: THREE.Vector3 }> = [];
    for (let i = 0; i < points.length; i++) {
      // Connect each point to 2 random nearby points
      const distances = points
        .map((p, idx) => ({ idx, dist: points[i].distanceTo(p) }))
        .filter((item) => item.idx !== i)
        .sort((a, b) => a.dist - b.dist);

      for (let c = 0; c < 2; c++) {
        const target = points[distances[c].idx];
        tempConns.push({ start: points[i], end: target });
      }
    }
    return tempConns;
  }, [points]);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.1;
      groupRef.current.rotation.z = state.clock.getElapsedTime() * 0.05;
    }
  });

  return (
    <group ref={groupRef}>
      {points.map((p, i) => (
        <mesh key={i} position={p}>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshBasicMaterial color={i % 3 === 0 ? "#34D399" : "#5B6CF9"} />
        </mesh>
      ))}

      {connections.map((c, i) => {
        const geom = new THREE.BufferGeometry().setFromPoints([c.start, c.end]);
        return (
          <line key={i}>
            <bufferGeometry attach="geometry" {...geom} />
            <lineBasicMaterial color="#9B59F5" opacity={0.2} transparent={true} />
          </line>
        );
      })}
    </group>
  );
}

export default function AlgoVisualizer({ mode = "sorting", array, comparing, sorted }: AlgoVisualizerProps) {
  const setCursorType = useUIStore((state) => state.setCursorType);

  return (
    <div 
      className="w-full h-full min-h-[350px] border border-aether bg-obsidian-depth/45 rounded-3xl relative overflow-hidden"
      onMouseEnter={() => setCursorType("hover")}
      onMouseLeave={() => setCursorType("default")}
    >
      <Canvas
        camera={{ position: [0, 0, 7.5], fov: 45 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.4} color="#0B0F20" />
        <pointLight position={[5, 10, 5]} intensity={1.5} color="#5B6CF9" />
        <pointLight position={[-5, -5, -5]} intensity={1} color="#9B59F5" />
        
        {mode === "sorting" && (
          <SortingScene array={array} comparing={comparing} sorted={sorted} />
        )}
        {mode === "tree" && <TreeScene />}
        {mode === "graph" && <GraphScene />}
      </Canvas>
    </div>
  );
}
