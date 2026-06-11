"use client";

import React, { useRef, useMemo } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { GLSL_NOISE_3D } from "@/lib/three-helpers";

interface SkillOrbMeshProps {
  mastery: number; // 0 to 100
}

function OrbMesh({ mastery }: SkillOrbMeshProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);
  const { pointer } = useThree(); // Normalized screen space (-1 to 1)

  // Normalize mastery level to 0-1 range
  const masteryNormalized = useMemo(() => {
    return Math.max(0, Math.min(100, mastery)) / 100;
  }, [mastery]);

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uMastery: { value: masteryNormalized },
      uPointer: { value: new THREE.Vector2(0, 0) },
    }),
    [masteryNormalized]
  );

  // Custom vertex and fragment GLSL shaders
  const vertexShader = `
    uniform float uTime;
    uniform float uMastery;
    varying vec3 vNormal;
    varying vec3 vPosition;
    varying float vDisplacement;

    ${GLSL_NOISE_3D}

    void main() {
      vNormal = normalize(normalMatrix * normal);
      vPosition = position;
      
      // Calculate vertex displacement using simplex noise and mastery level
      float noiseFreq = 2.0;
      float noiseSpeed = 0.8;
      float noiseValue = snoise(position * noiseFreq + vec3(0.0, 0.0, uTime * noiseSpeed));
      
      // Higher mastery = smoother, faster wave ripple. Lower mastery = turbulent spike
      float amp = 0.12 + (1.0 - uMastery) * 0.15;
      float displacement = noiseValue * amp * uMastery;
      vDisplacement = displacement;

      vec3 newPosition = position + normal * displacement;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
    }
  `;

  const fragmentShader = `
    uniform float uMastery;
    varying vec3 vNormal;
    varying vec3 vPosition;
    varying float vDisplacement;

    void main() {
      // Base colors
      vec3 col_indigo = vec3(0.357, 0.424, 0.976);  // #5B6CF9 indigo
      vec3 col_violet = vec3(0.608, 0.349, 0.961);  // #9B59F5 violet
      vec3 col_teal   = vec3(0.133, 0.827, 0.933);  // #22D3EE teal

      // Interpolate base color by displacement height and mastery level
      float blend = clamp(uMastery + vDisplacement, 0.0, 1.0);
      vec3 color = mix(col_indigo, col_violet, blend);
      
      // Add teal highlights for spike features
      if (vDisplacement > 0.05) {
        color = mix(color, col_teal, clamp(vDisplacement * 2.0, 0.0, 1.0));
      }

      // Add simple glass rim lighting (fresnel glow)
      float rim = 1.0 - max(dot(vNormal, vec3(0.0, 0.0, 1.0)), 0.0);
      rim = pow(rim, 3.0);
      
      color += col_teal * rim * 0.8; // Teal aura edge

      gl_FragColor = vec4(color, 0.9);
    }
  `;

  useFrame((state) => {
    if (meshRef.current && materialRef.current) {
      const elapsed = state.clock.getElapsedTime();
      
      // Update shader uniforms
      materialRef.current.uniforms.uTime.value = elapsed;
      materialRef.current.uniforms.uPointer.value.lerp(pointer, 0.1);

      // Sphere rotation tracking the pointer
      meshRef.current.rotation.y = elapsed * 0.1 + pointer.x * 0.4;
      meshRef.current.rotation.x = elapsed * 0.05 - pointer.y * 0.4;
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[2, 64, 64]} />
      <shaderMaterial
        ref={materialRef}
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        transparent={true}
        depthWrite={true}
      />
    </mesh>
  );
}

function OrbitRings() {
  const ringsRef = useRef<THREE.Group>(null);
  
  useFrame((state) => {
    if (ringsRef.current) {
      ringsRef.current.rotation.y = state.clock.getElapsedTime() * 0.15;
      ringsRef.current.rotation.x = state.clock.getElapsedTime() * 0.08;
    }
  });

  return (
    <group ref={ringsRef}>
      {/* Horizontal orbit ring */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[2.6, 0.02, 8, 64]} />
        <meshBasicMaterial color="#5B6CF9" transparent={true} opacity={0.3} />
      </mesh>
      {/* Tilted orbit ring */}
      <mesh rotation={[Math.PI / 4, Math.PI / 4, 0]}>
        <torusGeometry args={[2.8, 0.015, 8, 64]} />
        <meshBasicMaterial color="#9B59F5" transparent={true} opacity={0.2} />
      </mesh>
    </group>
  );
}

export default function SkillOrb({ mastery = 75 }: { mastery?: number }) {
  return (
    <div className="w-full h-full min-h-[300px] flex items-center justify-center relative">
      <Canvas
        camera={{ position: [0, 0, 4.5], fov: 50 }}
        gl={{ antialias: true, alpha: true }}
      >
        <ambientLight intensity={0.2} />
        <pointLight position={[5, 5, 5]} intensity={1.5} color="#5B6CF9" />
        <OrbMesh mastery={mastery} />
        <OrbitRings />
      </Canvas>
    </div>
  );
}
