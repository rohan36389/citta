import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { HOMEPAGE } from "@/data/content";
import { Database, MessageSquare, Video } from "lucide-react";
import StatValue from "@/components/StatValue";

const icons = [Database, MessageSquare, Video];

// Immersive AI Network Background for Stack Section
function StackNetworkBackground() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animationFrameId;

    let width = canvas.width = canvas.offsetWidth;
    let height = canvas.height = canvas.offsetHeight;

    const isMobile = window.innerWidth < 768;
    const particleCount = isMobile ? 18 : 45;
    const connectionDist = 130;

    const particles = [];
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.15, // Extremely slow movement
        vy: (Math.random() - 0.5) * 0.15,
        radius: Math.random() * 2 + 1,
        alpha: Math.random() * 0.3 + 0.1,
        pulseSpeed: 0.005 + Math.random() * 0.005,
        pulseVal: Math.random()
      });
    }

    const resize = () => {
      if (!canvas) return;
      width = canvas.width = canvas.offsetWidth;
      height = canvas.height = canvas.offsetHeight;
    };
    window.addEventListener("resize", resize);

    const draw = () => {
      ctx.clearRect(0, 0, width, height);

      // Draw animated constellation lines
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < connectionDist) {
            const alpha = (1 - dist / connectionDist) * 0.07;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(96, 165, 250, ${alpha})`;
            ctx.lineWidth = 0.6;
            ctx.stroke();
          }
        }
      }

      // Draw particles & breathing glowing neural dots
      particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0 || p.x > width) p.vx *= -1;
        if (p.y < 0 || p.y > height) p.vy *= -1;

        p.pulseVal += p.pulseSpeed;
        const sizeMultiplier = 1 + Math.sin(p.pulseVal) * 0.3;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius * sizeMultiplier, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${p.alpha})`;
        ctx.fill();

        // Volumetric breathing halo for select dots
        if (p.alpha > 0.32) {
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.radius * 3.5 * sizeMultiplier, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(59, 130, 246, ${p.alpha * 0.15})`;
          ctx.fill();
        }
      });

      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return <canvas ref={canvasRef} className="absolute inset-0 w-full h-full pointer-events-none opacity-40 z-0" />;
}

// Pipeline checkpoints configuration (relative coordinates out of 1000 viewBox)
const checkpoints = [
  { label: "RAG", y: 100, side: "left" },
  { label: "Reasoning", y: 220, side: "right" },
  { label: "Memory", y: 340, side: "left" },
  { label: "Planning", y: 460, side: "right" },
  { label: "Agents", y: 580, side: "left" },
  { label: "Voice AI", y: 700, side: "right" },
  { label: "Video AI", y: 820, side: "left" },
  { label: "Execution", y: 940, side: "right" }
];

// Alternating thinking paths to simulate AI reasoning
const thinkingRoutes = [
  // Route A: RAG -> Reasoning -> Step 01 Card -> Agents -> Execution
  "M 500 100 L 500 220 C 450 200, 430 240, 380 220 C 430 240, 450 200, 500 220 L 500 580 L 500 940",
  // Route B: RAG -> Memory -> Core -> Step 02 Card -> Video AI -> Step 03 Card -> Execution
  "M 500 100 L 500 580 C 550 560, 570 600, 620 580 C 570 600, 550 560, 500 580 L 500 820 C 450 800, 430 840, 380 820 C 430 840, 450 800, 500 820 L 500 940",
  // Route C: RAG -> Planning -> Core -> Video AI -> Execution
  "M 500 100 L 500 460 L 500 820 L 500 940"
];

export default function Stack() {
  const S = HOMEPAGE.stack;
  const [isInView, setIsInView] = useState(false);
  const [hoveredStep, setHoveredStep] = useState(null);
  const [activeRoute, setActiveRoute] = useState(null);

  // Cycle thinking routes every 10 seconds
  useEffect(() => {
    if (!isInView) return;
    const interval = setInterval(() => {
      const idx = Math.floor(Math.random() * thinkingRoutes.length);
      setActiveRoute(thinkingRoutes[idx]);
      // Fade out route after 3.2 seconds
      setTimeout(() => setActiveRoute(null), 3200);
    }, 10000);

    return () => clearInterval(interval);
  }, [isInView]);

  return (
    <motion.section 
      onViewportEnter={() => setIsInView(true)}
      className="relative bg-[#050816] text-white py-32 overflow-hidden" 
      data-testid="stack-section"
    >
      {/* Blueprint Grid Overlay */}
      <div className="absolute inset-0 grid-bg-dark opacity-[0.15] z-0" />
      
      {/* Immersive Volumetric Lighting */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full bg-blue-500/[0.03] blur-[150px] pointer-events-none z-0" />
      <div className="absolute -top-32 left-1/4 w-96 h-96 rounded-full bg-indigo-500/[0.04] blur-3xl pointer-events-none z-0" />

      {/* Living AI network canvas */}
      <StackNetworkBackground />

      {/* Embedded CSS for animations */}
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes halo-pulse {
          0%, 100% { opacity: 0.15; transform: scale(1); }
          50% { opacity: 0.35; transform: scale(1.15); }
        }
        @keyframes beam-drift {
          0% { stroke-dashoffset: 0; }
          100% { stroke-dashoffset: -800; }
        }
        @keyframes float-breathing-0 {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-6px) rotate(0.2deg); }
        }
        @keyframes float-breathing-1 {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-7px) rotate(-0.2deg); }
        }
        @keyframes float-breathing-2 {
          0%, 100% { transform: translateY(0px) rotate(0deg); }
          50% { transform: translateY(-5px) rotate(0.1deg); }
        }
        .core-halo {
          animation: halo-pulse 5s ease-in-out infinite;
        }
        .beam-pulse {
          stroke-dasharray: 40 180;
          animation: beam-drift 6s linear infinite;
        }
        .thinking-glow {
          stroke-dasharray: 80 160;
          animation: beam-drift 4s linear infinite;
        }
      `}} />

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 z-10">
        
        {/* Center Title Area */}
        <div className="text-center max-w-3xl mx-auto mb-20">
          <motion.div
            initial={{ opacity: 0, y: 15 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="chip chip-accent uppercase tracking-widest text-[11px] font-mono bg-blue-500/10 border-blue-500/20 text-blue-400 inline-block"
          >
            {S.eyebrow}
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.25 }}
            className="mt-5 font-display text-4xl md:text-5xl font-bold tracking-tight text-white leading-[1.08]"
          >
            {S.title.split("'s ")[0]}'s <span className="text-gradient-brand">{S.title.split("'s ")[1]}</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            transition={{ duration: 0.7, delay: 0.4 }}
            className="mt-4 text-xs font-mono uppercase tracking-widest text-blue-400/80 font-medium"
          >
            {S.outcome}
          </motion.p>
        </div>

        {/* Desktop Pipeline Visualizer */}
        <div className="hidden lg:block relative w-full max-w-[1000px] aspect-square mx-auto">
          
          {/* Main SVG Pipeline Canvas Overlay */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none z-10" viewBox="0 0 1000 1000">
            <defs>
              <linearGradient id="coreBeamGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3B82F6" stopOpacity="0.8" />
                <stop offset="50%" stopColor="#60A5FA" stopOpacity="0.9" />
                <stop offset="100%" stopColor="#10B981" stopOpacity="0.8" />
              </linearGradient>
              <filter id="bloomGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="6" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Glowing vertical energy conduit lines */}
            <motion.line 
              x1="500" y1="0" x2="500" y2="1000" 
              stroke="rgba(59, 130, 246, 0.12)" 
              strokeWidth="4" 
              initial={{ pathLength: 0 }}
              animate={isInView ? { pathLength: 1 } : {}}
              transition={{ duration: 1.4, ease: "easeInOut", delay: 0.3 }}
            />
            
            {/* Core light beam pulse */}
            {isInView && (
              <line 
                x1="500" y1="0" x2="500" y2="1000" 
                stroke="url(#coreBeamGrad)" 
                strokeWidth="2" 
                className="beam-pulse" 
                filter="url(#bloomGlow)"
              />
            )}

            {/* Spline Connections from core to cards */}
            {/* Card 1 Spline (Reasoning y=220) */}
            <motion.path 
              d="M 500 220 C 450 200, 430 240, 380 220" 
              stroke={hoveredStep === 0 ? "rgba(96, 165, 250, 0.65)" : "rgba(255, 255, 255, 0.1)"} 
              strokeWidth={hoveredStep === 0 ? "2.5" : "1.2"} 
              fill="none" 
              initial={{ pathLength: 0 }}
              animate={isInView ? { pathLength: 1 } : {}}
              transition={{ duration: 0.8, delay: 2.1 }}
              className="transition-all duration-300"
            />

            {/* Card 2 Spline (Agents y=580) */}
            <motion.path 
              d="M 500 580 C 550 560, 570 600, 620 580" 
              stroke={hoveredStep === 1 ? "rgba(96, 165, 250, 0.65)" : "rgba(255, 255, 255, 0.1)"} 
              strokeWidth={hoveredStep === 1 ? "2.5" : "1.2"} 
              fill="none" 
              initial={{ pathLength: 0 }}
              animate={isInView ? { pathLength: 1 } : {}}
              transition={{ duration: 0.8, delay: 2.3 }}
              className="transition-all duration-300"
            />

            {/* Card 3 Spline (Video AI y=820) */}
            <motion.path 
              d="M 500 820 C 450 800, 430 840, 380 820" 
              stroke={hoveredStep === 2 ? "rgba(96, 165, 250, 0.65)" : "rgba(255, 255, 255, 0.1)"} 
              strokeWidth={hoveredStep === 2 ? "2.5" : "1.2"} 
              fill="none" 
              initial={{ pathLength: 0 }}
              animate={isInView ? { pathLength: 1 } : {}}
              transition={{ duration: 0.8, delay: 2.5 }}
              className="transition-all duration-300"
            />

            {/* Continuous Spline Data Flow (Core <-> Card) */}
            {isInView && (
              <>
                {/* Spline 1 Data Packets */}
                <circle r="2.8" fill="#60A5FA" filter="url(#bloomGlow)">
                  <animateMotion dur="3.4s" repeatCount="indefinite" path="M 500 220 C 450 200, 430 240, 380 220" />
                </circle>
                <circle r="2.2" fill="#34D399">
                  <animateMotion dur="4.2s" repeatCount="indefinite" path="M 380 220 C 430 240, 450 200, 500 220" />
                </circle>

                {/* Spline 2 Data Packets */}
                <circle r="2.8" fill="#60A5FA" filter="url(#bloomGlow)">
                  <animateMotion dur="4.0s" repeatCount="indefinite" path="M 500 580 C 550 560, 570 600, 620 580" />
                </circle>
                <circle r="2.2" fill="#F472B6">
                  <animateMotion dur="4.8s" repeatCount="indefinite" path="M 620 580 C 570 600, 550 560, 500 580" />
                </circle>

                {/* Spline 3 Data Packets */}
                <circle r="2.8" fill="#60A5FA" filter="url(#bloomGlow)">
                  <animateMotion dur="3.2s" repeatCount="indefinite" path="M 500 820 C 450 800, 430 840, 380 820" />
                </circle>
                <circle r="2.2" fill="#34D399">
                  <animateMotion dur="4.5s" repeatCount="indefinite" path="M 380 820 C 430 840, 450 800, 500 820" />
                </circle>
              </>
            )}

            {/* Launch bright energy pulses on Hover */}
            {hoveredStep === 0 && (
              <circle r="5" fill="#60A5FA" filter="url(#bloomGlow)">
                <animateMotion dur="0.7s" repeatCount="1" path="M 500 220 C 450 200, 430 240, 380 220" />
              </circle>
            )}
            {hoveredStep === 1 && (
              <circle r="5" fill="#60A5FA" filter="url(#bloomGlow)">
                <animateMotion dur="0.7s" repeatCount="1" path="M 500 580 C 550 560, 570 600, 620 580" />
              </circle>
            )}
            {hoveredStep === 2 && (
              <circle r="5" fill="#60A5FA" filter="url(#bloomGlow)">
                <animateMotion dur="0.7s" repeatCount="1" path="M 500 820 C 450 800, 430 840, 380 820" />
              </circle>
            )}

            {/* AI thinking simulation overlay route */}
            <AnimatePresence>
              {activeRoute && (
                <motion.path 
                  d={activeRoute}
                  fill="none"
                  stroke="#38BDF8"
                  strokeWidth="2.5"
                  className="thinking-glow"
                  filter="url(#bloomGlow)"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: [0, 1, 1, 0] }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 3.2, times: [0, 0.1, 0.9, 1] }}
                />
              )}
            </AnimatePresence>
          </svg>

          {/* Core checkpoints and text labels */}
          <div className="absolute top-0 bottom-0 left-1/2 -translate-x-1/2 w-0.5 flex flex-col justify-between pointer-events-none z-20">
            {checkpoints.map((cp, idx) => {
              const isGlowNode = 
                (hoveredStep === 0 && idx === 1) || 
                (hoveredStep === 1 && idx === 4) || 
                (hoveredStep === 2 && idx === 6);

              return (
                <div 
                  key={cp.label}
                  className="absolute left-1/2 -translate-x-1/2 flex items-center justify-center"
                  style={{ top: `${cp.y}px` }}
                >
                  {/* Outer Breathing Halo */}
                  <div className={`core-halo absolute w-8 h-8 rounded-full bg-blue-500/10 border border-blue-500/20 pointer-events-none ${isGlowNode ? "scale-125 border-blue-400 bg-blue-500/20" : ""}`} />
                  
                  {/* Central node dot */}
                  <motion.div 
                    initial={{ scale: 0 }}
                    animate={isInView ? { scale: 1 } : {}}
                    transition={{ type: "spring", damping: 15, delay: 0.4 + (cp.y / 1000) * 1.2 }}
                    className={`relative w-3.5 h-3.5 rounded-full border border-white/40 bg-[#0f172a] shadow-inner transition-all duration-300 ${isGlowNode ? "bg-blue-400 scale-110 shadow-[0_0_12px_#3B82F6]" : ""}`}
                  />

                  {/* Stage Label */}
                  <div 
                    className={`absolute flex flex-col font-mono text-[9px] uppercase tracking-widest text-slate-400 select-none whitespace-nowrap transition-colors duration-300 ${
                      cp.side === "left" ? "right-6 text-right" : "left-6 text-left"
                    } ${isGlowNode ? "text-blue-300 font-bold" : ""}`}
                  >
                    {cp.label}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Step Cards Positioning (desktop relative viewBox container coordinates) */}
          
          {/* Card 1: EAI-Based Intelligence (Reasoning y=220) */}
          <div 
            className={`absolute top-[148px] left-[50px] w-[330px] z-30 transition-all duration-500 ${
              hoveredStep !== null && hoveredStep !== 0 ? "opacity-35 scale-[0.98] blur-[0.5px]" : "opacity-100"
            }`}
            style={{
              animation: `float-breathing-0 7s ease-in-out infinite`
            }}
          >
            <StepCard 
              step={S.steps[0]} 
              idx={0} 
              icon={icons[0]} 
              isInView={isInView}
              slideDirection="left"
              onHoverStart={() => setHoveredStep(0)}
              onHoverEnd={() => setHoveredStep(null)}
            />
          </div>

          {/* Card 2: AI Chat Agents (Agents y=580) */}
          <div 
            className={`absolute top-[508px] right-[50px] w-[330px] z-30 transition-all duration-500 ${
              hoveredStep !== null && hoveredStep !== 1 ? "opacity-35 scale-[0.98] blur-[0.5px]" : "opacity-100"
            }`}
            style={{
              animation: `float-breathing-1 8s ease-in-out infinite`
            }}
          >
            <StepCard 
              step={S.steps[1]} 
              idx={1} 
              icon={icons[1]} 
              isInView={isInView}
              slideDirection="right"
              onHoverStart={() => setHoveredStep(1)}
              onHoverEnd={() => setHoveredStep(null)}
            />
          </div>

          {/* Card 3: Video AI Agents (Video AI y=820) */}
          <div 
            className={`absolute top-[748px] left-[50px] w-[330px] z-30 transition-all duration-500 ${
              hoveredStep !== null && hoveredStep !== 2 ? "opacity-35 scale-[0.98] blur-[0.5px]" : "opacity-100"
            }`}
            style={{
              animation: `float-breathing-2 7.5s ease-in-out infinite`
            }}
          >
            <StepCard 
              step={S.steps[2]} 
              idx={2} 
              icon={icons[2]} 
              isInView={isInView}
              slideDirection="left"
              onHoverStart={() => setHoveredStep(2)}
              onHoverEnd={() => setHoveredStep(null)}
            />
          </div>

        </div>

        {/* Mobile & Tablet Vertical Intelligent Flow */}
        <div className="lg:hidden flex flex-col gap-10 max-w-xl mx-auto relative px-4">
          {/* Vertical mobile conduit overlay */}
          <div className="absolute top-0 bottom-0 left-8 w-px bg-gradient-to-b from-blue-500/20 via-blue-500/40 to-emerald-500/20 pointer-events-none" />
          
          {S.steps.map((s, i) => {
            const Icon = icons[i];
            return (
              <motion.div
                key={s.n}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: "-40px" }}
                transition={{ duration: 0.6, delay: i * 0.12 }}
                className="relative pl-14"
              >
                {/* Mobile Conduit Node */}
                <div className="absolute left-[27px] top-6 w-3 h-3 rounded-full border border-white/50 bg-[#0f172a] flex items-center justify-center">
                  <div className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-ping" />
                </div>

                <div className="group relative rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl p-6 shadow-2xl transition-all duration-300">
                  <div className="absolute inset-0 w-[200%] h-full bg-gradient-to-r from-transparent via-white/5 to-transparent pointer-events-none -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-in-out" />
                  
                  <span className="font-mono text-[10px] uppercase tracking-widest text-blue-400 block mb-3">{s.n}</span>
                  <div className="h-10 w-10 rounded-xl bg-blue-500/10 border border-blue-500/20 grid place-items-center mb-4">
                    <Icon className="h-4.5 w-4.5 text-blue-400" />
                  </div>
                  <h3 className="font-display text-lg font-semibold text-white">{s.title}</h3>
                  <p className="mt-2 text-white/60 text-xs leading-relaxed">{s.desc}</p>
                </div>
              </motion.div>
            );
          })}
        </div>

      </div>

      {/* Continuing glowing energy conduit line downward out of the section */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-0.5 h-16 bg-gradient-to-t from-blue-500/40 to-transparent pointer-events-none hidden lg:block" />
    </motion.section>
  );
}

// Sub-component Step Card (VisionOS dark liquid glass styling)
function StepCard({ step, idx, icon: Icon, isInView, slideDirection, onHoverStart, onHoverEnd }) {
  const xOffset = slideDirection === "left" ? -80 : 80;
  
  return (
    <motion.div
      initial={{ opacity: 0, x: xOffset }}
      animate={isInView ? { opacity: 1, x: 0 } : {}}
      transition={{ duration: 0.8, ease: "easeOut", delay: 1.3 + idx * 0.25 }}
      onMouseEnter={onHoverStart}
      onMouseLeave={onHoverEnd}
      className="group relative rounded-3xl border border-white/10 bg-white/[0.02] backdrop-blur-xl p-8 shadow-[0_12px_40px_rgba(0,0,0,0.5)] transition-all duration-500 hover:border-blue-500/30 hover:bg-white/[0.06] hover:scale-[1.03] cursor-pointer hover:shadow-[0_16px_48px_rgba(37,99,235,0.22)]"
      data-testid={`stack-step-${idx}`}
    >
      {/* Reflection Shine overlay */}
      <div 
        className="absolute inset-0 w-[200%] h-full bg-gradient-to-r from-transparent via-white/5 to-transparent pointer-events-none"
        style={{
          transform: "skewX(-20deg) translateX(-100%)",
          animation: "sweep 10s ease-in-out infinite",
          animationDelay: `${idx * 2}s`
        }}
      />

      {/* Border glow highlight */}
      <div className="absolute inset-0 rounded-3xl border border-blue-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

      {/* Step Number Badge */}
      <div className="flex items-center justify-between mb-5">
        <span className="font-mono text-[10px] uppercase tracking-widest text-slate-400 group-hover:text-blue-300 transition-colors duration-300">
          {step.n}
        </span>
        <div className="w-1.5 h-1.5 rounded-full bg-slate-500 group-hover:bg-blue-400 transition-colors duration-300" />
      </div>

      {/* Glass-contained Lucide Icon */}
      <div className="h-12 w-12 rounded-xl bg-blue-500/10 border border-blue-500/20 grid place-items-center mb-5 group-hover:border-blue-400/40 group-hover:bg-blue-500/20 transition-all duration-500">
        <Icon className="h-5 w-5 text-blue-400 group-hover:text-blue-300 transition-colors duration-300" />
      </div>

      {/* Title */}
      <h3 className="font-display text-xl font-semibold text-white tracking-tight group-hover:text-blue-200 transition-colors duration-300">
        {step.title}
      </h3>

      {/* Description */}
      <p className="mt-2.5 text-slate-400 text-sm leading-relaxed transition-colors duration-300 group-hover:text-slate-300">
        {step.desc}
      </p>
    </motion.div>
  );
}
