'use client'

import { useEffect, useRef } from 'react'

export default function AetherBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const gl = (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')) as WebGLRenderingContext | null
    if (!gl) {
      console.error('WebGL not supported')
      return
    }

    // Vertex Shader (standard passthrough)
    const vsSource = `
      attribute vec2 position;
      void main() {
        gl_Position = vec4(position, 0.0, 1.0);
      }
    `

    // Fragment Shader (Aether Flow core noise)
    const fsSource = `
      precision highp float;
      uniform float u_time;
      uniform vec2 u_resolution;

      // Smooth noise function
      vec3 mod289(vec3 x) { return x - floor(x*(1./289.))*289.; }
      vec4 mod289(vec4 x) { return x - floor(x*(1./289.))*289.; }
      vec4 permute(vec4 x) { return mod289(((x*34.)+1.)*x); }
      vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159-.85373472095314*r; }
      
      float snoise(vec3 v) {
        const vec2 C = vec2(1.0/6.0, 1.0/3.0);
        const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);

        // First corner
        vec3 i  = floor(v + vec3(dot(v, vec3(C.y))));
        vec3 x0 = v - i + vec3(dot(i, vec3(C.x)));

        // Other corners
        vec3 g = step(x0.yzx, x0.xyz);
        vec3 l = 1.0 - g;
        vec3 i1 = min(g.xyz, l.zxy);
        vec3 i2 = max(g.xyz, l.zxy);

        vec3 x1 = x0 - i1 + vec3(C.x);
        vec3 x2 = x0 - i2 + vec3(C.y);
        vec3 x3 = x0 - D.yyy;

        // Permutations
        i = mod289(i);
        vec4 p = permute(permute(permute(
                   vec4(i.z) + vec4(0.0, i1.z, i2.z, 1.0))
                 + vec4(i.y) + vec4(0.0, i1.y, i2.y, 1.0))
                 + vec4(i.x) + vec4(0.0, i1.x, i2.x, 1.0));

        // Gradients
        float n_ = 0.142857142857; // 1.0/7.0
        vec3 ns = n_ * D.wyz - D.xzx;

        vec4 j = p - 49.0 * floor(p * ns.z * ns.z);

        vec4 x_ = floor(j * ns.z);
        vec4 y_ = floor(j - 7.0 * x_);

        vec4 x = x_ * ns.x + ns.yyyy;
        vec4 y = y_ * ns.x + ns.yyyy;
        vec4 h = vec4(1.0) - abs(x) - abs(y);

        vec4 b0 = vec4(x.xy, y.xy);
        vec4 b1 = vec4(x.zw, y.zw);

        vec4 s0 = floor(b0) * 2.0 + vec4(1.0);
        vec4 s1 = floor(b1) * 2.0 + vec4(1.0);
        vec4 sh = -step(h, vec4(0.0));

        vec4 a0 = b0.xzyw + s0.xzyw * sh.xxyy;
        vec4 a1 = b1.xzyw + s1.xzyw * sh.zzww;

        vec3 p0 = vec3(a0.xy, h.x);
        vec3 p1 = vec3(a0.zw, h.y);
        vec3 p2 = vec3(a1.xy, h.z);
        vec3 p3 = vec3(a1.zw, h.w);

        // Normalise gradients
        vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
        p0 *= norm.x;
        p1 *= norm.y;
        p2 *= norm.z;
        p3 *= norm.w;

        // Mix final noise value
        vec4 m = max(vec4(0.6) - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), vec4(0.0));
        m = m * m;
        return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
      }

      void main() {
        vec2 uv = gl_FragCoord.xy / u_resolution;
        float t  = u_time * 0.12;
        float warp = 0.4;
        float n1 = snoise(vec3(uv * 2.5, t));
        float n2 = snoise(vec3(uv * 3.0 + n1*warp, t*1.3));
        float n3 = snoise(vec3(uv * 1.8 + n2*warp, t*0.8));
        float blend = (n1 + n2 + n3) / 3.0;

        // Aether Flow palette: indigo base, violet mid, teal accent
        vec3 col_a = vec3(0.357, 0.424, 0.976);  // #5B6CF9 indigo
        vec3 col_b = vec3(0.608, 0.349, 0.961);  // #9B59F5 violet
        vec3 col_c = vec3(0.133, 0.827, 0.933);  // #22D3EE teal
        vec3 col_d = vec3(0.663, 0.333, 0.969);  // #A855F7 purple
        vec3 base  = vec3(0.024, 0.031, 0.078);  // #060814 obsidian

        vec3 aurora = mix(col_a, col_b, smoothstep(-.5,.5,blend));
        aurora = mix(aurora, col_c, smoothstep(.2,.8, n2)*0.5);
        aurora = mix(aurora, col_d, smoothstep(.1,.7, n3)*0.35);

        // Fade aurora into the dark base — key for readability
        float intensity = smoothstep(-.3,.8,blend) * 0.18;
        vec3 final = mix(base, aurora, intensity);

        gl_FragColor = vec4(final, 1.0);
      }
    `

    const createShader = (gl: WebGLRenderingContext, type: number, source: string) => {
      const shader = gl.createShader(type)
      if (!shader) return null
      gl.shaderSource(shader, source)
      gl.compileShader(shader)
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.error('Shader compile error:', gl.getShaderInfoLog(shader))
        gl.deleteShader(shader)
        return null
      }
      return shader
    }

    const vs = createShader(gl, gl.VERTEX_SHADER, vsSource)
    const fs = createShader(gl, gl.FRAGMENT_SHADER, fsSource)
    if (!vs || !fs) return

    const program = gl.createProgram()
    if (!program) return
    gl.attachShader(program, vs)
    gl.attachShader(program, fs)
    gl.linkProgram(program)

    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error('Program link error:', gl.getProgramInfoLog(program))
      return
    }

    gl.useProgram(program)

    const positionBuffer = gl.createBuffer()
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer)
    const positions = new Float32Array([
      -1, -1,
       1, -1,
      -1,  1,
      -1,  1,
       1, -1,
       1,  1,
    ])
    gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW)

    const positionLoc = gl.getAttribLocation(program, 'position')
    gl.enableVertexAttribArray(positionLoc)
    gl.vertexAttribPointer(positionLoc, 2, gl.FLOAT, false, 0, 0)

    const timeLoc = gl.getUniformLocation(program, 'u_time')
    const resolutionLoc = gl.getUniformLocation(program, 'u_resolution')

    let animationFrameId: number
    const startTime = performance.now()

    const render = () => {
      const time = (performance.now() - startTime) / 1000.0
      gl.uniform1f(timeLoc, time)
      gl.uniform2f(resolutionLoc, canvas.width, canvas.height)

      gl.viewport(0, 0, canvas.width, canvas.height)
      gl.clearColor(0.024, 0.031, 0.078, 1.0)
      gl.clear(gl.COLOR_BUFFER_BIT)

      gl.drawArrays(gl.TRIANGLES, 0, 6)

      animationFrameId = requestAnimationFrame(render)
    }

    const handleResize = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
      gl.viewport(0, 0, canvas.width, canvas.height)
    }

    window.addEventListener('resize', handleResize)
    handleResize()
    render()

    return () => {
      cancelAnimationFrame(animationFrameId)
      window.removeEventListener('resize', handleResize)
      gl.deleteBuffer(positionBuffer)
      gl.deleteProgram(program)
      gl.deleteShader(vs)
      gl.deleteShader(fs)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 w-full h-full"
      style={{ zIndex: 0, pointerEvents: 'none' }}
    />
  )
}
