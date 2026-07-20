import { useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { HOMEPAGE } from "@/data/content";
import StatValue from "@/components/StatValue";

// Matches client names to local file assets automatically
const LOGO_FILES = [
  "Aurum_street-DCJLaXXK.png",
  "Devarasa-FbIBTtGK.png",
  "Green_Leaves-DGqJH5ZS.png",
  "Nails_by_Mahas_logo-D9n-iPR_.png",
  "Olive_Mithai_Logo_Green_1_Large-B_tXP-Gq.png",
  "SRK_jawa-BwItJrVI.png",
  "SVS_logo-HM8dvI6k.png",
  "Shilpa_botanica_logo-CwuXVVGb.png",
  "Vegasri-D-4mxSCL.png",
  "cropped-Fixity-EDX-Website-Logo-Bs77BqaI.jpeg"
];

const getClientLogoUrl = (clientName) => {
  const normName = clientName.toLowerCase().replace(/[^a-z0-9]/g, "");
  
  const matchedFile = LOGO_FILES.find(file => {
    const normFile = file.toLowerCase().replace(/[^a-z0-9]/g, "");
    
    if (clientName.toLowerCase().includes("aurum") && file.toLowerCase().includes("aurum")) return true;
    if (clientName.toLowerCase().includes("devarasa") && file.toLowerCase().includes("devarasa")) return true;
    if (clientName.toLowerCase().includes("green") && file.toLowerCase().includes("green")) return true;
    if (clientName.toLowerCase().includes("mahas") && file.toLowerCase().includes("mahas")) return true;
    if (clientName.toLowerCase().includes("olive") && file.toLowerCase().includes("olive")) return true;
    if (clientName.toLowerCase().includes("jawa") && file.toLowerCase().includes("jawa")) return true;
    if (clientName.toLowerCase().includes("svs") && file.toLowerCase().includes("svs")) return true;
    if (clientName.toLowerCase().includes("shilpa") && file.toLowerCase().includes("shilpa")) return true;
    if (clientName.toLowerCase().includes("vegasri") && file.toLowerCase().includes("vegasri")) return true;
    if (clientName.toLowerCase().includes("fixity") && file.toLowerCase().includes("fixity")) return true;
    
    return normFile.includes(normName) || normName.includes(normFile);
  });
  
  if (matchedFile) {
    return `/assets/clients/${matchedFile}`;
  }
  
  return null;
};

// Canvas-based subtle AI Network Background with interactive hover pulse
function AINetworkBackground({ triggerPulseRef }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animationFrameId;

    let width = canvas.width = canvas.offsetWidth;
    let height = canvas.height = canvas.offsetHeight;

    const isMobile = window.innerWidth < 768;
    const particleCount = isMobile ? 12 : 32;
    const connectionDist = 120;

    const particles = [];
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.35,
        radius: Math.random() * 1.5 + 1,
        alpha: Math.random() * 0.5 + 0.2
      });
    }

    // Dynamic node coordinates corresponding to areas under columns
    const anchors = [
      { x: width * 0.16, y: height * 0.2 },
      { x: width * 0.16, y: height * 0.5 },
      { x: width * 0.16, y: height * 0.8 },
      { x: width * 0.5,  y: height * 0.15 },
      { x: width * 0.5,  y: height * 0.5 },
      { x: width * 0.5,  y: height * 0.85 },
      { x: width * 0.84, y: height * 0.25 },
      { x: width * 0.84, y: height * 0.55 },
      { x: width * 0.84, y: height * 0.75 }
    ];

    let activeGlows = [];
    const triggerGlow = () => {
      if (activeGlows.length > 3) return;
      const startIdx = Math.floor(Math.random() * anchors.length);
      let endIdx = Math.floor(Math.random() * anchors.length);
      while (endIdx === startIdx) {
        endIdx = Math.floor(Math.random() * anchors.length);
      }
      
      activeGlows.push({
        x1: anchors[startIdx].x,
        y1: anchors[startIdx].y,
        x2: anchors[endIdx].x,
        y2: anchors[endIdx].y,
        progress: 0,
        speed: 0.005 + Math.random() * 0.005
      });
    };

    const interval = setInterval(triggerGlow, 3000);

    // List of active mouse-hover pulses
    let activePulses = [];
    if (triggerPulseRef) {
      triggerPulseRef.current = (x, y) => {
        activePulses.push({
          x,
          y,
          radius: 0,
          maxRadius: 75,
          alpha: 0.7,
          speed: 3
        });
      };
    }

    const resize = () => {
      if (!canvas) return;
      width = canvas.width = canvas.offsetWidth;
      height = canvas.height = canvas.offsetHeight;
      
      anchors[0] = { x: width * 0.16, y: height * 0.2 };
      anchors[1] = { x: width * 0.16, y: height * 0.5 };
      anchors[2] = { x: width * 0.16, y: height * 0.8 };
      anchors[3] = { x: width * 0.5,  y: height * 0.15 };
      anchors[4] = { x: width * 0.5,  y: height * 0.5 };
      anchors[5] = { x: width * 0.5,  y: height * 0.85 };
      anchors[6] = { x: width * 0.84, y: height * 0.25 };
      anchors[7] = { x: width * 0.84, y: height * 0.55 };
      anchors[8] = { x: width * 0.84, y: height * 0.75 };
    };
    window.addEventListener("resize", resize);

    const draw = () => {
      ctx.clearRect(0, 0, width, height);

      // Draw mouse hover pulses
      activePulses = activePulses.filter(p => {
        p.radius += p.speed;
        p.alpha -= 0.02;
        if (p.alpha <= 0) return false;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(59, 130, 246, ${p.alpha})`;
        ctx.lineWidth = 1;
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius + 6, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(96, 165, 250, ${p.alpha * 0.4})`;
        ctx.lineWidth = 0.5;
        ctx.stroke();

        return true;
      });

      // Draw connection lines and moving packets
      activeGlows = activeGlows.filter(glow => {
        glow.progress += glow.speed;
        if (glow.progress >= 1) return false;

        const cx = glow.x1 + (glow.x2 - glow.x1) * glow.progress;
        const cy = glow.y1 + (glow.y2 - glow.y1) * glow.progress;

        ctx.beginPath();
        ctx.moveTo(glow.x1, glow.y1);
        ctx.lineTo(cx, cy);
        ctx.strokeStyle = "rgba(59, 130, 246, 0.12)";
        ctx.lineWidth = 0.8;
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(cx, cy, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(96, 165, 250, 0.6)";
        ctx.fill();

        return true;
      });

      // Draw particle network lines
      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < connectionDist) {
            const alpha = (1 - dist / connectionDist) * 0.12;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(255, 255, 255, ${alpha})`;
            ctx.lineWidth = 0.6;
            ctx.stroke();
          }
        }
      }

      // Draw particles
      particles.forEach(p => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0 || p.x > width) p.vx *= -1;
        if (p.y < 0 || p.y > height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${p.alpha})`;
        ctx.fill();

        if (p.alpha > 0.5) {
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.radius * 2.5, 0, Math.PI * 2);
          ctx.fillStyle = "rgba(96, 165, 250, 0.12)";
          ctx.fill();
        }
      });

      animationFrameId = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animationFrameId);
      clearInterval(interval);
      window.removeEventListener("resize", resize);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return <canvas ref={canvasRef} className="absolute inset-0 w-full h-full pointer-events-none opacity-40" />;
}

// Client Logo Card with VisionOS styles
function ClientLogoCard({ name, index, onMouseEnter }) {
  const logoUrl = getClientLogoUrl(name);
  
  const floatDelay = `${(index * 0.5).toFixed(2)}s`;
  const sweepDelay = `${(index * 1.8).toFixed(2)}s`;

  return (
    <div 
      onMouseEnter={onMouseEnter}
      className="group relative w-full h-[98px] flex items-center justify-center rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-xl px-6 py-4 shadow-[0_8px_32px_0_rgba(0,0,0,0.5)] transition-all duration-500 overflow-hidden cursor-pointer hover:border-blue-500/30 hover:bg-white/[0.08] hover:scale-[1.04] hover:-translate-y-1.5 hover:shadow-[0_16px_40px_rgba(37,99,235,0.25)]"
      style={{
        animation: `float-breathe 8s ease-in-out infinite`,
        animationDelay: floatDelay
      }}
    >
      {/* Reflection shine sweep effect */}
      <div 
        className="absolute inset-0 w-[200%] h-full bg-gradient-to-r from-transparent via-white/10 to-transparent pointer-events-none"
        style={{
          transform: "skewX(-20deg) translateX(-100%)",
          animation: "sweep 10s ease-in-out infinite",
          animationDelay: sweepDelay
        }}
      />
      
      {/* Soft blue glow border highlight on hover */}
      <div className="absolute inset-0 rounded-2xl border border-blue-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

      {/* Blue ambient glow inside the card on hover */}
      <div className="absolute inset-0 bg-blue-500/[0.02] opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />

      <div className="relative w-full h-full flex items-center justify-center">
        {logoUrl ? (
          <img 
            src={logoUrl} 
            alt={name} 
            className="max-w-[75%] max-h-[58%] object-contain transition-all duration-500 group-hover:scale-[1.04] filter brightness-95 contrast-105 group-hover:brightness-100" 
            loading="lazy"
          />
        ) : (
          <span className="font-display font-medium tracking-[0.25em] text-white/50 uppercase text-[10px] text-center select-none transition-colors duration-500 group-hover:text-white/80">
            {name}
          </span>
        )}
      </div>
    </div>
  );
}

export default function Fueling() {
  const F = HOMEPAGE.fueling;
  const [isInView, setIsInView] = useState(false);
  const triggerPulseRef = useRef(null);

  // Staged client lists for columns
  const col1 = ["Aurum Street", "Devarasa", "Green Leaves", "Nails by Mahas"];
  const col2 = ["Olive Mithai", "Premedis", "SRK Jawa", "SVS"];
  const col3 = ["Shaaranga", "Shilpa Botanica", "Vegasri", "Axygen", "Fixity"];

  const handleCardMouseEnter = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const parent = e.currentTarget.closest(".showcase-container");
    if (!parent) return;
    const parentRect = parent.getBoundingClientRect();
    const x = rect.left - parentRect.left + rect.width / 2;
    const y = rect.top - parentRect.top + rect.height / 2;
    if (triggerPulseRef.current) {
      triggerPulseRef.current(x, y);
    }
  };

  return (
    <motion.section 
      onViewportEnter={() => setIsInView(true)}
      className="relative bg-gradient-to-b from-[#0A0F1E] to-[#050816] text-white py-28 overflow-hidden" 
      data-testid="fueling-section"
    >
      {/* Subtle grid mesh overlay */}
      <div className="absolute inset-0 grid-bg-dark opacity-20" />
      
      {/* Ambient blue radial lights in background */}
      <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-blue-500/10 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none" />

      {/* CSS Keyframes and styling embedded locally */}
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes scroll-up {
          0% { transform: translateY(0); }
          100% { transform: translateY(-50%); }
        }
        @keyframes scroll-down {
          0% { transform: translateY(-50%); }
          100% { transform: translateY(0); }
        }
        @keyframes float-breathe {
          0%, 100% { transform: translateY(0) scale(1); }
          50% { transform: translateY(-3px) scale(1.008); }
        }
        @keyframes sweep {
          0% { transform: skewX(-20deg) translateX(-100%); }
          25% { transform: skewX(-20deg) translateX(120%); }
          100% { transform: skewX(-20deg) translateX(120%); }
        }
        .animate-scroll-up-1 {
          animation: scroll-up 24s linear infinite;
        }
        .animate-scroll-down-2 {
          animation: scroll-down 28s linear infinite;
        }
        .animate-scroll-up-3 {
          animation: scroll-up 38s linear infinite;
        }
        .animate-scroll-up-1:hover,
        .animate-scroll-down-2:hover,
        .animate-scroll-up-3:hover {
          animation-play-state: paused;
        }
      `}} />

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <div className="grid lg:grid-cols-12 gap-16 items-center">
          
          {/* LEFT Column: Copy & Statistics */}
          <div className="lg:col-span-5 flex flex-col justify-center">
            
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, y: 15 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.6 }}
              className="chip chip-accent uppercase tracking-widest text-[11px] font-mono inline-block w-fit bg-blue-500/10 border-blue-500/20 text-blue-400"
            >
              {F.eyebrow}
            </motion.div>

            {/* Headline */}
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.6, delay: 0.15 }}
              className="mt-5 font-display text-4xl md:text-5xl font-bold tracking-tight text-white leading-tight whitespace-pre-line"
            >
              {F.title}
            </motion.h2>

            {/* Description */}
            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="mt-6 text-base md:text-lg text-slate-400 leading-relaxed max-w-md"
            >
              {F.desc}
            </motion.p>

            {/* Statistics */}
            <div className="mt-10 grid grid-cols-2 gap-6 border-t border-white/5 pt-8">
              {F.stats.map((s, i) => (
                <motion.div
                  key={s.l}
                  initial={{ opacity: 0, y: 15 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-80px" }}
                  transition={{ duration: 0.6, delay: 0.4 + i * 0.1 }}
                  className="relative"
                >
                  <div className="font-display text-4xl font-bold text-gradient-brand">
                    <StatValue value={s.v} />
                  </div>
                  <p className="mt-1.5 text-slate-400 text-sm font-medium">{s.l}</p>
                </motion.div>
              ))}
            </div>
          </div>

          {/* RIGHT Column: Infinite vertical scrolling showcase (VisionOS Dark glass container) */}
          <motion.div 
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.8, delay: 0.5 }}
            className="lg:col-span-7 relative h-[560px] w-full overflow-hidden rounded-3xl border border-white/10 bg-slate-950/40 p-6 flex gap-4 shadow-[inset_0_2px_12px_rgba(255,255,255,0.02)] showcase-container"
          >
            {/* AI Network canvas background */}
            <AINetworkBackground triggerPulseRef={triggerPulseRef} />

            {/* Column 1 (Moves upward) */}
            <div className="flex-1 h-full overflow-hidden relative">
              <div className={`flex flex-col gap-4 w-full ${isInView ? "animate-scroll-up-1" : ""}`}>
                {[...col1, ...col1].map((name, idx) => (
                  <ClientLogoCard 
                    key={`col1-${idx}-${name}`} 
                    name={name} 
                    index={idx} 
                    onMouseEnter={handleCardMouseEnter} 
                  />
                ))}
              </div>
            </div>

            {/* Column 2 (Moves downward) */}
            <div className="hidden md:flex flex-1 h-full overflow-hidden relative">
              <div className={`flex flex-col gap-4 w-full ${isInView ? "animate-scroll-down-2" : ""}`}>
                {[...col2, ...col2].map((name, idx) => (
                  <ClientLogoCard 
                    key={`col2-${idx}-${name}`} 
                    name={name} 
                    index={idx} 
                    onMouseEnter={handleCardMouseEnter} 
                  />
                ))}
              </div>
            </div>

            {/* Column 3 (Moves upward slower) */}
            <div className="hidden lg:flex flex-1 h-full overflow-hidden relative">
              <div className={`flex flex-col gap-4 w-full ${isInView ? "animate-scroll-up-3" : ""}`}>
                {[...col3, ...col3].map((name, idx) => (
                  <ClientLogoCard 
                    key={`col3-${idx}-${name}`} 
                    name={name} 
                    index={idx} 
                    onMouseEnter={handleCardMouseEnter} 
                  />
                ))}
              </div>
            </div>
            
            {/* Soft gradient masks at top and bottom for smooth layout clipping fade */}
            <div className="absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-[#060917] to-transparent pointer-events-none z-10" />
            <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-[#060917] to-transparent pointer-events-none z-10" />
          </motion.div>

        </div>
      </div>
    </motion.section>
  );
}
