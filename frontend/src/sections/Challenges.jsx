import { motion } from "framer-motion";
import { Settings, GitBranch, Cpu, Boxes, Repeat } from "lucide-react";
import { HOMEPAGE } from "@/data/content";
import SectionHeader from "@/components/SectionHeader";

const icons = [GitBranch, Cpu, Boxes, Repeat];

// Simple SVG "gears" illustration used at right-side of section (matches brief 3.4)
function GearsIllustration() {
  return (
    <svg viewBox="0 0 400 400" className="w-full h-full" role="img" aria-label="Industrial gears representing manual, mechanical, outdated processes">
      <defs>
        <linearGradient id="gearGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#1E293B" />
          <stop offset="100%" stopColor="#0F172A" />
        </linearGradient>
        <linearGradient id="gearRim" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#334155" />
          <stop offset="100%" stopColor="#1E293B" />
        </linearGradient>
      </defs>
      {/* Large gear */}
      <g transform="translate(160,180)">
        <g className="animate-[spin_28s_linear_infinite]" style={{ transformOrigin: "center" }}>
          {Array.from({ length: 12 }).map((_, i) => (
            <rect key={i} x="-8" y="-115" width="16" height="30" fill="url(#gearRim)"
                  transform={`rotate(${(i / 12) * 360})`} />
          ))}
          <circle r="95" fill="url(#gearGrad)" stroke="#334155" strokeWidth="2" />
          <circle r="55" fill="none" stroke="#475569" strokeWidth="1" />
          <circle r="20" fill="#0A0F1E" stroke="#60A5FA" strokeWidth="1.5" />
        </g>
      </g>
      {/* Small gear */}
      <g transform="translate(300,110)">
        <g className="animate-[spin_18s_linear_reverse_infinite]" style={{ transformOrigin: "center" }}>
          {Array.from({ length: 8 }).map((_, i) => (
            <rect key={i} x="-5" y="-58" width="10" height="18" fill="url(#gearRim)"
                  transform={`rotate(${(i / 8) * 360})`} />
          ))}
          <circle r="48" fill="url(#gearGrad)" stroke="#334155" strokeWidth="1.5" />
          <circle r="12" fill="#0A0F1E" stroke="#60A5FA" strokeWidth="1" />
        </g>
      </g>
      {/* Tiny gear */}
      <g transform="translate(80,300)">
        <g className="animate-[spin_22s_linear_infinite]" style={{ transformOrigin: "center" }}>
          {Array.from({ length: 6 }).map((_, i) => (
            <rect key={i} x="-4" y="-40" width="8" height="14" fill="url(#gearRim)"
                  transform={`rotate(${(i / 6) * 360})`} />
          ))}
          <circle r="32" fill="url(#gearGrad)" stroke="#334155" strokeWidth="1" />
          <circle r="8" fill="#0A0F1E" stroke="#60A5FA" strokeWidth="1" />
        </g>
      </g>
    </svg>
  );
}

export default function Challenges() {
  const C = HOMEPAGE.challenges;
  return (
    <section className="relative section-dark2 py-28 overflow-hidden" data-testid="challenges-section">
      <div className="absolute inset-0 grid-bg-dark opacity-30" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <SectionHeader eyebrow={C.eyebrow} title={C.title} />

        <div className="mt-14 grid lg:grid-cols-12 gap-10 items-start">
          <div className="lg:col-span-7 grid sm:grid-cols-2 gap-4">
            {C.items.map((it, i) => {
              const Ico = icons[i % icons.length];
              return (
                <motion.div
                  key={it.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-60px" }}
                  transition={{ duration: 0.55, delay: i * 0.08 }}
                  className="glass-dark rounded-2xl p-6 tilt"
                  data-testid={`challenge-card-${i}`}
                >
                  <div className="h-10 w-10 rounded-xl bg-white/5 border border-white/10 grid place-items-center mb-4">
                    <Ico className="h-4 w-4 text-brand-light" />
                  </div>
                  <h3 className="font-display text-xl font-semibold text-white leading-tight">{it.title}</h3>
                  <p className="mt-2 text-sm text-white/60 leading-relaxed">{it.desc}</p>
                </motion.div>
              );
            })}
          </div>

          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8 }}
            className="lg:col-span-5 relative aspect-square rounded-3xl overflow-hidden glass-dark p-6"
          >
            <div className="absolute inset-0 grid-bg-dark opacity-40" />
            <div className="relative h-full flex flex-col justify-between">
              <div className="flex items-center justify-between">
                <span className="chip !text-white/70 !border-white/20 !bg-white/5">{C.contrast.left}</span>
                <Settings className="h-5 w-5 text-white/40 animate-spin" style={{ animationDuration: "8s" }} />
              </div>
              <div className="h-64">
                <GearsIllustration />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono uppercase tracking-widest text-white/40">vs.</span>
                <span className="chip">{C.contrast.right}</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
