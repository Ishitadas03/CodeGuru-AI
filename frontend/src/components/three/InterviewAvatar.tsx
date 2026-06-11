"use client";

import React, { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

interface InterviewAvatarProps {
  state?: "idle" | "speaking" | "thinking" | "feedback";
  className?: string;
}

function AvatarMesh({ state = "idle" }: { state: "idle" | "speaking" | "thinking" | "feedback" }) {
  const coreRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  // Map state name to float value for WebGL shader
  const stateVal = useMemo(() => {
    if (state === "speaking") return 1.0;
    if (state === "thinking") return 2.0;
    if (state === "feedback") return 3.0;
    return 0.0; // idle
  }, [state]);

  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uState: { value: stateVal },
  }), []);

  const vertexShader = `
    varying vec3 vPosition;
    varying vec3 vNormal;
    void main() {
      vNormal = normalize(normalMatrix * normal);
      vPosition = position;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `;

  const fragmentShader = `
    uniform float uTime;
    uniform float uState;
    varying vec3 vPosition;
    varying vec3 vNormal;
    
    void main() {
      vec3 color = vec3(0.357, 0.424, 0.976); // #5B6CF9 indigo base
      
      if (uState == 1.0) { // speaking
        float angle = atan(vPosition.x, vPosition.z);
        float blend = sin(angle * 2.0 + uTime * 4.0) * 0.5 + 0.5;
        vec3 col_violet = vec3(0.608, 0.349, 0.961); // #9B59F5 violet
        vec3 col_teal   = vec3(0.133, 0.827, 0.933); // #22D3EE teal
        color = mix(col_violet, col_teal, blend);
      } else if (uState == 2.0) { // thinking
        color = vec3(0.658, 0.333, 0.969); // #A855F7 purple
      } else if (uState == 3.0) { // feedback
        color = vec3(0.204, 0.827, 0.600); // #34D399 emerald
      } else { // idle
        float pulse = 0.85 + 0.15 * sin(uTime * 2.5);
        color = vec3(0.357, 0.424, 0.976) * pulse; // #5B6CF9 indigo
      }
      
      gl_FragColor = vec4(color, 0.8);
    }
  `;

  useFrame((tState) => {
    const elapsed = tState.clock.getElapsedTime();

    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = elapsed;
      materialRef.current.uniforms.uState.value = stateVal;
    }

    if (coreRef.current) {
      if (state === "speaking") {
        coreRef.current.rotation.y = elapsed * 1.2;
        coreRef.current.rotation.x = elapsed * 0.6;
        const scale = 1.35 + Math.sin(elapsed * 8) * 0.08;
        coreRef.current.scale.setScalar(scale);
      } else if (state === "thinking") {
        coreRef.current.rotation.y = elapsed * 0.3;
        coreRef.current.rotation.x = elapsed * 0.15;
        const scale = 1.3 + Math.sin(elapsed * 4) * 0.03;
        coreRef.current.scale.setScalar(scale);
      } else {
        coreRef.current.rotation.y = elapsed * 0.25;
        coreRef.current.rotation.x = elapsed * 0.1;
        const scale = 1.3 + Math.sin(elapsed * 1.8) * 0.04;
        coreRef.current.scale.setScalar(scale);
      }
    }

    if (ringRef.current) {
      ringRef.current.rotation.x = elapsed * 0.8;
      ringRef.current.rotation.y = elapsed * 0.5;
    }
  });

  return (
    <group>
      {/* 3D Wireframe Core Avatar */}
      <mesh ref={coreRef}>
        <icosahedronGeometry args={[1, 2]} />
        <shaderMaterial
          ref={materialRef}
          vertexShader={vertexShader}
          fragmentShader={fragmentShader}
          uniforms={uniforms}
          wireframe={true}
          transparent={true}
          depthWrite={false}
        />
      </mesh>

      {/* Orbiting ring for "thinking" or "speaking" */}
      {state === "thinking" && (
        <mesh ref={ringRef}>
          <torusGeometry args={[1.5, 0.04, 8, 48]} />
          <meshBasicMaterial color="#A855F7" transparent={true} opacity={0.6} />
        </mesh>
      )}
      {state === "speaking" && (
        <mesh ref={ringRef}>
          <torusGeometry args={[1.4, 0.03, 8, 48]} />
          <meshBasicMaterial color="#22D3EE" transparent={true} opacity={0.4} />
        </mesh>
      )}
    </group>
  );
}

export default function InterviewAvatar({ state = "idle", className }: InterviewAvatarProps) {
  return (
    <div className={`w-full h-full flex items-center justify-center relative select-none ${className || "min-h-[300px]"}`}>
      <Canvas
        camera={{ position: [0, 0, 4], fov: 50 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.25} />
        <pointLight position={[5, 5, 5]} intensity={1.5} color="#F0F4FF" />
        <AvatarMesh state={state} />
      </Canvas>
    </div>
  );
}
