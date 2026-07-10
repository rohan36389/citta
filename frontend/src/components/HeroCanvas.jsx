import { Canvas, useFrame } from "@react-three/fiber";
import { useMemo, useRef, Suspense } from "react";
import * as THREE from "three";

// Fibonacci sphere for well-distributed nodes
function makeNodes(count, radius) {
  const pts = [];
  const phi = Math.PI * (Math.sqrt(5) - 1);
  for (let i = 0; i < count; i++) {
    const y = 1 - (i / (count - 1)) * 2;
    const r = Math.sqrt(1 - y * y);
    const theta = phi * i;
    pts.push([Math.cos(theta) * r * radius, y * radius, Math.sin(theta) * r * radius]);
  }
  return pts;
}

function NodeSphere({ nodes, group }) {
  return (
    <group ref={group}>
      {nodes.map((p, i) => (
        <mesh key={i} position={p}>
          <sphereGeometry args={[0.035, 12, 12]} />
          <meshBasicMaterial color={i % 3 === 0 ? "#60A5FA" : "#93C5FD"} />
        </mesh>
      ))}
    </group>
  );
}

function ConnectionLines({ nodes, groupRef, maxDist = 1.35 }) {
  // Precompute static connections (indices) for efficiency
  const { positions, colors } = useMemo(() => {
    const pos = [];
    const col = [];
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        const a = nodes[i], b = nodes[j];
        const d = Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
        if (d < maxDist) {
          pos.push(...a, ...b);
          const intensity = 1 - d / maxDist;
          col.push(0.4 * intensity, 0.65 * intensity, 1.0 * intensity);
          col.push(0.4 * intensity, 0.65 * intensity, 1.0 * intensity);
        }
      }
    }
    return { positions: new Float32Array(pos), colors: new Float32Array(col) };
  }, [nodes, maxDist]);

  return (
    <lineSegments ref={groupRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={positions.length / 3} array={positions} itemSize={3} />
        <bufferAttribute attach="attributes-color"    count={colors.length / 3}    array={colors}    itemSize={3} />
      </bufferGeometry>
      <lineBasicMaterial vertexColors transparent opacity={0.55} />
    </lineSegments>
  );
}

function DataPackets({ nodes, count = 24 }) {
  const meshRef = useRef();
  const dummy = useMemo(() => new THREE.Object3D(), []);

  // Assign each packet a random source, destination, and speed
  const packets = useMemo(() => {
    return Array.from({ length: count }, () => {
      const from = Math.floor(Math.random() * nodes.length);
      let to = Math.floor(Math.random() * nodes.length);
      while (to === from) to = Math.floor(Math.random() * nodes.length);
      return { from, to, t: Math.random(), speed: 0.15 + Math.random() * 0.25 };
    });
  }, [nodes, count]);

  useFrame((_, delta) => {
    if (!meshRef.current) return;
    packets.forEach((p, i) => {
      p.t += delta * p.speed;
      if (p.t >= 1) {
        p.t = 0;
        p.from = p.to;
        let nxt = Math.floor(Math.random() * nodes.length);
        while (nxt === p.from) nxt = Math.floor(Math.random() * nodes.length);
        p.to = nxt;
      }
      const a = nodes[p.from], b = nodes[p.to];
      dummy.position.set(
        a[0] + (b[0] - a[0]) * p.t,
        a[1] + (b[1] - a[1]) * p.t,
        a[2] + (b[2] - a[2]) * p.t
      );
      const s = 0.7 + Math.sin(p.t * Math.PI) * 0.6;
      dummy.scale.setScalar(s);
      dummy.updateMatrix();
      meshRef.current.setMatrixAt(i, dummy.matrix);
    });
    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={meshRef} args={[null, null, count]}>
      <sphereGeometry args={[0.055, 12, 12]} />
      <meshBasicMaterial color="#93E4FF" />
    </instancedMesh>
  );
}

function Scene() {
  const groupRef = useRef();
  const linesRef = useRef();
  const nodes = useMemo(() => makeNodes(46, 2.4), []);

  useFrame(({ clock, mouse }) => {
    const t = clock.getElapsedTime();
    if (groupRef.current) {
      groupRef.current.rotation.y = t * 0.08 + mouse.x * 0.35;
      groupRef.current.rotation.x = mouse.y * 0.2;
    }
    if (linesRef.current) {
      linesRef.current.material.opacity = 0.4 + Math.sin(t * 1.2) * 0.15;
    }
  });

  return (
    <group ref={groupRef}>
      <NodeSphere nodes={nodes} />
      <ConnectionLines nodes={nodes} groupRef={linesRef} />
      <DataPackets nodes={nodes} count={28} />
      {/* Ambient soft glow inside */}
      <mesh>
        <sphereGeometry args={[0.9, 32, 32]} />
        <meshBasicMaterial color="#2563EB" transparent opacity={0.06} />
      </mesh>
    </group>
  );
}

export default function HeroCanvas() {
  return (
    <div className="absolute inset-0" data-testid="hero-3d-canvas">
      <Canvas
        camera={{ position: [0, 0, 6], fov: 45 }}
        dpr={[1, 2]}
        gl={{ antialias: true, alpha: true }}
      >
        <color attach="background" args={["#0A0F1E"]} />
        <fog attach="fog" args={["#0A0F1E", 6, 14]} />
        <Suspense fallback={null}>
          <Scene />
        </Suspense>
      </Canvas>
    </div>
  );
}
