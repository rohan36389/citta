import { useRef, useEffect, useState, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

// ─── Materials ────────────────────────────────────────────────────────────────
const DARK_METAL = {
  color: "#0d1424",
  roughness: 0.18,
  metalness: 0.94,
  clearcoat: 1.0,
  clearcoatRoughness: 0.08,
};
const MID_METAL = {
  color: "#1a2540",
  roughness: 0.28,
  metalness: 0.88,
};
const ACCENT_METAL = {
  color: "#0f1e36",
  roughness: 0.12,
  metalness: 0.96,
};
const CITTA_BLUE = "#2D7FF9";
const CITTA_BLUE_LIGHT = "#60A5FA";

// ─── RobotHead — the only moving part ────────────────────────────────────────
function RobotHead({ rotX, rotY, blinkScale }) {
  const headGroup = useRef();
  const leftEyeRef = useRef();
  const rightEyeRef = useRef();

  useFrame(() => {
    if (!headGroup.current) return;
    // Smooth rotation via lerp applied by parent
    headGroup.current.rotation.x = rotX.current;
    headGroup.current.rotation.y = rotY.current;

    // Eye blink scale
    if (leftEyeRef.current) leftEyeRef.current.scale.y = blinkScale.current;
    if (rightEyeRef.current) rightEyeRef.current.scale.y = blinkScale.current;
  });

  return (
    <group ref={headGroup} position={[0, 0.52, 0]}>
      {/* Helmet — main head shape */}
      <mesh castShadow>
        <sphereGeometry args={[0.34, 40, 40]} />
        <meshPhysicalMaterial {...DARK_METAL} />
      </mesh>

      {/* Brow ridge */}
      <mesh position={[0, 0.14, 0.28]} rotation={[0.25, 0, 0]}>
        <boxGeometry args={[0.50, 0.06, 0.10]} />
        <meshPhysicalMaterial {...ACCENT_METAL} />
      </mesh>

      {/* Visor dark panel */}
      <mesh position={[0, 0.05, 0.29]} rotation={[0.05, 0, 0]}>
        <boxGeometry args={[0.44, 0.13, 0.08]} />
        <meshPhysicalMaterial color="#02060f" roughness={0.04} metalness={0.98} clearcoat={1} />
      </mesh>

      {/* LEFT eye glow */}
      <group ref={leftEyeRef} position={[-0.13, 0.06, 0.32]}>
        <mesh>
          <sphereGeometry args={[0.028, 24, 24]} />
          <meshBasicMaterial color={CITTA_BLUE} />
        </mesh>
        {/* Soft eye halo */}
        <mesh>
          <sphereGeometry args={[0.044, 16, 16]} />
          <meshBasicMaterial color={CITTA_BLUE} transparent opacity={0.18} />
        </mesh>
      </group>

      {/* RIGHT eye glow */}
      <group ref={rightEyeRef} position={[0.13, 0.06, 0.32]}>
        <mesh>
          <sphereGeometry args={[0.028, 24, 24]} />
          <meshBasicMaterial color={CITTA_BLUE} />
        </mesh>
        <mesh>
          <sphereGeometry args={[0.044, 16, 16]} />
          <meshBasicMaterial color={CITTA_BLUE} transparent opacity={0.18} />
        </mesh>
      </group>

      {/* Nose bridge line detail */}
      <mesh position={[0, -0.04, 0.31]}>
        <boxGeometry args={[0.06, 0.04, 0.04]} />
        <meshStandardMaterial color="#0f1a2e" metalness={0.8} roughness={0.2} />
      </mesh>

      {/* Chin speaker grille */}
      <mesh position={[0, -0.14, 0.28]}>
        <boxGeometry args={[0.22, 0.04, 0.06]} />
        <meshStandardMaterial color="#0a1020" metalness={0.85} roughness={0.3} />
      </mesh>

      {/* Ear stubs */}
      {[-1, 1].map((side) => (
        <group key={side} position={[side * 0.35, 0.05, 0]}>
          <mesh>
            <cylinderGeometry args={[0.035, 0.04, 0.06, 16]} />
            <meshStandardMaterial color="#1a2c48" metalness={0.85} roughness={0.2} />
          </mesh>
          {/* Ear blue accent ring */}
          <mesh position={[0, 0, 0]}>
            <torusGeometry args={[0.035, 0.008, 8, 24]} />
            <meshBasicMaterial color={CITTA_BLUE_LIGHT} transparent opacity={0.5} />
          </mesh>
        </group>
      ))}

      {/* Top antenna */}
      <mesh position={[0, 0.38, 0]}>
        <cylinderGeometry args={[0.008, 0.012, 0.12, 12]} />
        <meshStandardMaterial color="#1a2c48" metalness={0.9} roughness={0.1} />
      </mesh>
      <mesh position={[0, 0.45, 0]}>
        <sphereGeometry args={[0.016, 12, 12]} />
        <meshBasicMaterial color={CITTA_BLUE} />
      </mesh>
    </group>
  );
}

// ─── RobotBody — fully static, only subtle breathing ─────────────────────────
function RobotBody({ breathe }) {
  const bodyRef = useRef();
  const shouldersRef = useRef();

  useFrame(() => {
    if (bodyRef.current) bodyRef.current.position.y = -0.55 + breathe.current * 0.012;
    if (shouldersRef.current) {
      shouldersRef.current.position.y = -0.36 + breathe.current * 0.009;
      shouldersRef.current.rotation.z = breathe.current * 0.004;
    }
  });

  return (
    <group>
      {/* Neck joint */}
      <mesh position={[0, 0.15, 0]}>
        <cylinderGeometry args={[0.08, 0.1, 0.18, 24]} />
        <meshPhysicalMaterial {...MID_METAL} />
      </mesh>

      {/* Chest torso */}
      <group ref={bodyRef} position={[0, -0.55, 0]}>
        {/* Core torso */}
        <mesh castShadow>
          <cylinderGeometry args={[0.3, 0.26, 0.62, 36]} />
          <meshPhysicalMaterial {...DARK_METAL} />
        </mesh>

        {/* Chest plate panel */}
        <mesh position={[0, 0.08, 0.24]}>
          <boxGeometry args={[0.34, 0.24, 0.04]} />
          <meshPhysicalMaterial {...ACCENT_METAL} clearcoat={1} clearcoatRoughness={0.05} />
        </mesh>

        {/* Chest blue accent strip */}
        <mesh position={[0, 0.09, 0.27]}>
          <boxGeometry args={[0.22, 0.028, 0.02]} />
          <meshBasicMaterial color={CITTA_BLUE} transparent opacity={0.85} />
        </mesh>

        {/* Core reactor circle */}
        <mesh position={[0, -0.04, 0.27]}>
          <circleGeometry args={[0.052, 32]} />
          <meshBasicMaterial color={CITTA_BLUE_LIGHT} transparent opacity={0.6} />
        </mesh>
        <mesh position={[0, -0.04, 0.268]}>
          <torusGeometry args={[0.062, 0.008, 8, 32]} />
          <meshBasicMaterial color={CITTA_BLUE} transparent opacity={0.55} />
        </mesh>

        {/* Abdominal segment lines */}
        {[-0.12, -0.20].map((y, i) => (
          <mesh key={i} position={[0, y, 0.25]}>
            <boxGeometry args={[0.28, 0.012, 0.032]} />
            <meshStandardMaterial color="#0a1a32" metalness={0.9} roughness={0.2} />
          </mesh>
        ))}

        {/* Lower torso ring */}
        <mesh position={[0, -0.28, 0]}>
          <torusGeometry args={[0.27, 0.022, 12, 36]} />
          <meshStandardMaterial color="#162038" metalness={0.85} roughness={0.25} />
        </mesh>
      </group>

      {/* Shoulder pauldrons */}
      <group ref={shouldersRef} position={[0, -0.36, 0]}>
        {[-1, 1].map((side) => (
          <group key={side} position={[side * 0.42, 0, 0]}>
            <mesh castShadow>
              <sphereGeometry args={[0.16, 24, 24]} />
              <meshPhysicalMaterial {...DARK_METAL} />
            </mesh>
            {/* Shoulder blue accent */}
            <mesh position={[0, -0.01, 0.13]}>
              <boxGeometry args={[0.1, 0.028, 0.02]} />
              <meshBasicMaterial color={CITTA_BLUE_LIGHT} transparent opacity={0.5} />
            </mesh>
            {/* Upper arm stub */}
            <mesh position={[0, -0.2, 0]}>
              <cylinderGeometry args={[0.085, 0.075, 0.22, 20]} />
              <meshPhysicalMaterial {...MID_METAL} />
            </mesh>
          </group>
        ))}
      </group>
    </group>
  );
}

// ─── Blue floor glow ──────────────────────────────────────────────────────────
function FloorGlow({ breathe }) {
  const glowRef = useRef();

  // Build an ellipse shape using THREE.EllipseCurve → ShapeGeometry
  const ellipseGeo = useMemo(() => {
    const curve = new THREE.EllipseCurve(0, 0, 0.48, 0.18, 0, Math.PI * 2, false, 0);
    const points = curve.getPoints(48);
    const shape = new THREE.Shape(points);
    return new THREE.ShapeGeometry(shape);
  }, []);

  useFrame(() => {
    if (glowRef.current) {
      glowRef.current.material.opacity = 0.22 + breathe.current * 0.06;
    }
  });

  return (
    <mesh ref={glowRef} rotation={[-Math.PI / 2, 0, 0]} position={[0, -1.1, 0]}>
      <primitive object={ellipseGeo} attach="geometry" />
      <meshBasicMaterial color={CITTA_BLUE} transparent opacity={0.22} />
    </mesh>
  );
}

// ─── Full Scene ───────────────────────────────────────────────────────────────
function RobotScene({ heroInView, isChatOpen }) {
  const rotX = useRef(0);
  const rotY = useRef(0);
  const targetX = useRef(0);
  const targetY = useRef(0);
  const breatheVal = useRef(0);
  const blinkScale = useRef(1);
  const clock = useRef(0);

  // --- Cursor tracking via Hero element ---
  useEffect(() => {
    const hero = document.getElementById("hero");
    if (!hero) return;

    const MAX_H = 20 * (Math.PI / 180);
    const MAX_V = 10 * (Math.PI / 180);

    const onMove = (e) => {
      const rect = hero.getBoundingClientRect();
      const nx = (e.clientX - rect.left) / rect.width - 0.5;   // -0.5 to 0.5
      const ny = (e.clientY - rect.top) / rect.height - 0.5;
      targetX.current = ny * 2 * MAX_V;
      targetY.current = nx * 2 * MAX_H;
    };

    const onLeave = () => {
      targetX.current = 0;
      targetY.current = 0;
    };

    hero.addEventListener("mousemove", onMove);
    hero.addEventListener("mouseleave", onLeave);
    return () => {
      hero.removeEventListener("mousemove", onMove);
      hero.removeEventListener("mouseleave", onLeave);
    };
  }, []);

  // --- Random blink every ~4s ---
  useEffect(() => {
    const blink = () => {
      blinkScale.current = 0.05;
      setTimeout(() => { blinkScale.current = 1; }, 100);
    };
    const sched = () => {
      blink();
      setTimeout(sched, 3800 + Math.random() * 2400);
    };
    const t = setTimeout(sched, 2000);
    return () => clearTimeout(t);
  }, []);

  // --- Frame loop ---
  useFrame((_, delta) => {
    clock.current += delta;

    // Breathing sine
    breatheVal.current = Math.sin(clock.current * 1.45);

    // Chat open → look toward bottom-right chat panel
    if (isChatOpen) {
      targetY.current = 18 * (Math.PI / 180);
      targetX.current = 8 * (Math.PI / 180);
    }

    // Lerp head rotation
    rotX.current += (targetX.current - rotX.current) * 0.065;
    rotY.current += (targetY.current - rotY.current) * 0.065;
  });

  return (
    <group>
      <RobotBody breathe={breatheVal} />
      <RobotHead rotX={rotX} rotY={rotY} blinkScale={blinkScale} />
      <FloorGlow breathe={breatheVal} />
    </group>
  );
}

// ─── Exported Component ───────────────────────────────────────────────────────
export default function RobotConcierge() {
  const [mounted, setMounted] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const heroRef = useRef(null);
  const [heroInView, setHeroInView] = useState(true);

  // Fade in after mount
  useEffect(() => {
    const t = setTimeout(() => setMounted(true), 400);
    return () => clearTimeout(t);
  }, []);

  // Listen to chat toggle events from AIConsultant
  useEffect(() => {
    const handler = (e) => setIsChatOpen(e.detail?.isOpen ?? false);
    window.addEventListener("cittaai_chat_toggle", handler);
    return () => window.removeEventListener("cittaai_chat_toggle", handler);
  }, []);

  // Pause rendering when hero scrolls out of view
  useEffect(() => {
    const hero = document.getElementById("hero");
    if (!hero) return;
    const obs = new IntersectionObserver(
      ([entry]) => setHeroInView(entry.isIntersecting),
      { threshold: 0.05 }
    );
    obs.observe(hero);
    return () => obs.disconnect();
  }, []);

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        opacity: mounted ? 1 : 0,
        transform: mounted ? "translateY(0)" : "translateY(20px)",
        transition: "opacity 1.1s ease-out, transform 1.0s ease-out",
      }}
    >
      <Canvas
        frameloop={heroInView ? "always" : "never"}
        camera={{ position: [0, 0.08, 2.1], fov: 40 }}
        dpr={[1, 1.5]}
        gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      >
        {/* Lighting — CittaAI blue theme */}
        <ambientLight intensity={0.55} />
        {/* Key light — warm front */}
        <directionalLight position={[1.5, 2.5, 2.5]} intensity={2.2} color="#e8f0ff" castShadow />
        {/* Rim light — CittaAI blue */}
        <pointLight position={[-2, 1, -1.5]} intensity={3.5} color={CITTA_BLUE} />
        {/* Fill light — soft blue top */}
        <directionalLight position={[0, 3, -2]} intensity={1.2} color={CITTA_BLUE_LIGHT} />
        {/* Ground bounce — very faint blue */}
        <pointLight position={[0, -2, 1]} intensity={0.6} color={CITTA_BLUE} />

        <RobotScene heroInView={heroInView} isChatOpen={isChatOpen} />
      </Canvas>
    </div>
  );
}
