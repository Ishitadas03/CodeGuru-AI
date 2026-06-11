"use client";

import React, { useRef, useMemo } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { useMousePosition } from "@/hooks/useMousePosition";

// Component representing the inner nodes, connections, and signals
function NetworkMesh() {
  const { mouse } = useThree() as any; // Normalized screen space (-1 to 1)
  const groupRef = useRef<THREE.Group>(null);
  const pulseRef = useRef<THREE.InstancedMesh>(null);

  const NODE_COUNT = 70;
  const CONNECTION_LIMIT = 3;

  // 1. Generate random 3D nodes
  const [nodes, connections] = useMemo(() => {
    const tempNodes: THREE.Vector3[] = [];
    const tempColors: THREE.Color[] = [];
    
    const indigo = new THREE.Color("#5B6CF9");
    const violet = new THREE.Color("#9B59F5");

    for (let i = 0; i < NODE_COUNT; i++) {
      // Random coordinates inside a bounding box
      const x = (Math.random() - 0.5) * 12;
      const y = (Math.random() - 0.5) * 8;
      const z = (Math.random() - 0.5) * 8;
      tempNodes.push(new THREE.Vector3(x, y, z));
      
      // Node color variation
      tempColors.push(Math.random() > 0.4 ? indigo : violet);
    }

    // Connect each node to its closest neighbors
    const tempConnections: Array<{ start: THREE.Vector3; end: THREE.Vector3; startIndex: number; endIndex: number }> = [];
    
    for (let i = 0; i < NODE_COUNT; i++) {
      const distances = tempNodes
        .map((target, idx) => ({ idx, dist: tempNodes[i].distanceTo(target) }))
        .filter((item) => item.idx !== i)
        .sort((a, b) => a.dist - b.dist);

      // Connect to closest N nodes
      for (let c = 0; c < Math.min(CONNECTION_LIMIT, distances.length); c++) {
        const targetIdx = distances[c].idx;
        // Avoid duplicate paths
        if (i < targetIdx) {
          tempConnections.push({
            start: tempNodes[i],
            end: tempNodes[targetIdx],
            startIndex: i,
            endIndex: targetIdx,
          });
        }
      }
    }

    return [tempNodes, tempConnections];
  }, []);

  // 2. Generate line geometry for connections
  const linePoints = useMemo(() => {
    const points: number[] = [];
    connections.forEach((conn) => {
      points.push(conn.start.x, conn.start.y, conn.start.z);
      points.push(conn.end.x, conn.end.y, conn.end.z);
    });
    return new Float32Array(points);
  }, [connections]);

  // 3. Track signals traveling along paths
  const signals = useMemo(() => {
    const tempSignals = Array.from({ length: 25 }, () => {
      const conn = connections[Math.floor(Math.random() * connections.length)];
      return {
        conn,
        progress: Math.random(),
        speed: 0.005 + Math.random() * 0.01,
      };
    });
    return tempSignals;
  }, [connections]);

  // Render loop
  useFrame((state) => {
    if (!groupRef.current) return;

    // Slow rotation
    groupRef.current.rotation.y = state.clock.getElapsedTime() * 0.04;
    groupRef.current.rotation.x = state.clock.getElapsedTime() * 0.02;

    // Mouse parallax
    if (mouse) {
      groupRef.current.position.x += (mouse.x * 2 - groupRef.current.position.x) * 0.05;
      groupRef.current.position.y += (mouse.y * 2 - groupRef.current.position.y) * 0.05;
    }

    // Update signal pulses
    if (pulseRef.current) {
      const dummy = new THREE.Object3D();
      signals.forEach((sig, index) => {
        sig.progress += sig.speed;
        if (sig.progress >= 1) {
          // Select a new random connection
          sig.progress = 0;
          sig.conn = connections[Math.floor(Math.random() * connections.length)];
        }

        // Interpolate position along line
        const pos = new THREE.Vector3().lerpVectors(sig.conn.start, sig.conn.end, sig.progress);
        dummy.position.copy(pos);
        dummy.scale.setScalar(0.7 + Math.sin(state.clock.getElapsedTime() * 5 + index) * 0.3);
        dummy.updateMatrix();
        pulseRef.current!.setMatrixAt(index, dummy.matrix);
      });
      pulseRef.current.instanceMatrix.needsUpdate = true;
    }
  });

  return (
    <group ref={groupRef}>
      {/* Individual Node spheres */}
      {nodes.map((node, i) => (
        <mesh key={i} position={node}>
          <sphereGeometry args={[0.07, 16, 16]} />
          <meshPhongMaterial 
            color={i % 2 === 0 ? "#5B6CF9" : "#9B59F5"} 
            emissive={i % 2 === 0 ? "#5B6CF9" : "#9B59F5"}
            emissiveIntensity={0.6}
            shininess={100}
          />
        </mesh>
      ))}

      {/* Connection lines */}
      <lineSegments>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[linePoints, 3]}
          />
        </bufferGeometry>
        <lineBasicMaterial color="#5B6CF9" opacity={0.2} transparent={true} depthWrite={false} />
      </lineSegments>

      {/* Signal pulses */}
      <instancedMesh ref={pulseRef} args={[null as any, null as any, signals.length]}>
        <sphereGeometry args={[0.08, 8, 8]} />
        <meshBasicMaterial color="#22D3EE" />
      </instancedMesh>
    </group>
  );
}

export default function NeuralNetwork() {
  return (
    <div className="absolute inset-0 w-full h-full pointer-events-none select-none z-0">
      <Canvas
        camera={{ position: [0, 0, 10], fov: 60 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.4} color="#0B0F20" />
        <pointLight position={[10, 10, 10]} intensity={1.5} color="#5B6CF9" />
        <pointLight position={[-10, -10, -10]} intensity={1.5} color="#9B59F5" />
        <NetworkMesh />
      </Canvas>
    </div>
  );
}
