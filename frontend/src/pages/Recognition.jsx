import { motion } from "framer-motion";
import { Trophy, Sparkles, Award as AwardIcon } from "lucide-react";
import { RECOGNITION } from "@/data/content";
import SectionHeader from "@/components/SectionHeader";

// Abstract award SVG "photograph" — used because real ceremony photography is not available
function AwardArt({ variant = "trophy" }) {
  if (variant === "trophy") {
    return (
      <svg viewBox="0 0 400 300" className="w-full h-full">
        <defs>
          <linearGradient id="tGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#F59E0B" stopOpacity="0.9" />
            <stop offset="100%" stopColor="#FBBF24" stopOpacity="0.5" />
          </linearGradient>
          <linearGradient id="tBg" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#1E293B" />
            <stop offset="100%" stopColor="#0F172A" />
          </linearGradient>
        </defs>
        <rect width="400" height="300" fill="url(#tBg)" />
        {/* Confetti */}
        {Array.from({ length: 30 }).map((_, i) => {
          const cx = (i * 37) % 400, cy = (i * 53) % 300;
          return <circle key={`c-${cx}-${cy}`} cx={cx} cy={cy} r={i % 2 ? 2 : 1.5} fill="#60A5FA" opacity="0.4" />;
        })}
        {/* Trophy */}
        <g transform="translate(200,145)">
          {/* Handles */}
          <path d="M -60 -50 Q -80 -30 -60 0" stroke="url(#tGrad)" strokeWidth="4" fill="none" />
          <path d="M  60 -50 Q  80 -30  60 0" stroke="url(#tGrad)" strokeWidth="4" fill="none" />
          {/* Cup */}
          <path d="M -60 -60 L 60 -60 L 55 20 Q 0 40 -55 20 Z" fill="url(#tGrad)" stroke="#F59E0B" strokeWidth="2" />
          <ellipse cx="0" cy="-58" rx="60" ry="8" fill="#FDE68A" opacity="0.5" />
          {/* Stem */}
          <rect x="-8" y="20" width="16" height="30" fill="url(#tGrad)" />
          {/* Base */}
          <rect x="-40" y="50" width="80" height="14" rx="3" fill="#F59E0B" />
          {/* Star on cup */}
          <path d="M 0 -30 l 6 12 l 13 2 l -9.5 9 l 2.5 13 l -12 -6 l -12 6 l 2.5 -13 l -9.5 -9 l 13 -2 z" fill="#0F172A" opacity="0.6" />
        </g>
      </svg>
    );
  }
  // ribbon variant
  return (
    <svg viewBox="0 0 400 300" className="w-full h-full">
      <defs>
        <linearGradient id="rBg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0F172A" />
          <stop offset="100%" stopColor="#0A0F1E" />
        </linearGradient>
      </defs>
      <rect width="400" height="300" fill="url(#rBg)" />
      {/* Stars background */}
      {Array.from({ length: 22 }).map((_, i) => {
        const cx = (i * 71) % 400, cy = (i * 47) % 300;
        return <circle key={`s-${cx}-${cy}`} cx={cx} cy={cy} r={1.5} fill="#60A5FA" opacity="0.35" />;
      })}
      {/* Rosette */}
      <g transform="translate(200,140)">
        <circle r="55" fill="#60A5FA" opacity="0.15" />
        <circle r="42" fill="#2563EB" />
        <circle r="34" fill="#3B82F6" />
        {/* Star */}
        <path d="M 0 -22 l 6 12 l 13 2 l -9.5 9 l 2.5 13 l -12 -6 l -12 6 l 2.5 -13 l -9.5 -9 l 13 -2 z" fill="#FBBF24" />
        {/* Ribbons */}
        <path d="M -20 30 L -35 90 L -20 80 L -10 100 L -5 40 Z" fill="#2563EB" />
        <path d="M  20 30 L  35 90 L  20 80 L  10 100 L  5 40 Z" fill="#3B82F6" />
      </g>
    </svg>
  );
}

export default function Recognition() {
  const R = RECOGNITION;
  return (
    <div data-testid="recognition-page">
      <section className="relative section-dark pt-36 pb-16 overflow-hidden">
        <div className="aurora opacity-40" />
        <div className="absolute inset-0 grid-bg-dark opacity-30" />
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
          <div className="max-w-3xl">
            <div className="chip mb-5"><Sparkles className="h-3.5 w-3.5" /> {R.eyebrow}</div>
            <h1 className="font-display text-[clamp(2.4rem,5.5vw,4.8rem)] leading-[1.02] font-semibold tracking-tight text-white">
              {R.title} <span className="text-gradient-brand">{R.titleAccent}</span>
            </h1>
            <p className="mt-6 text-lg text-white/70 leading-relaxed">
              Recognized by government bodies and industry councils for engineering enterprise-grade AI intelligence.
            </p>
          </div>
        </div>
      </section>

      <section className="relative section-dark2 py-20 overflow-hidden">
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 space-y-6">
          {R.awards.map((a, i) => (
            <motion.article
              key={a.name}
              initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.7, delay: i * 0.1 }}
              className="glass-strong rounded-3xl overflow-hidden grid md:grid-cols-12"
              data-testid={`award-${i}`}
            >
              <div className="md:col-span-5 relative min-h-[280px]">
                <AwardArt variant={i === 0 ? "trophy" : "ribbon"} />
                <div className="absolute inset-0 bg-gradient-to-t md:bg-gradient-to-r from-slate-950/60 to-transparent pointer-events-none" />
              </div>
              <div className="md:col-span-7 p-8 md:p-10 relative">
                <div className="flex items-center gap-2 mb-4">
                  <Trophy className="h-4 w-4 text-brand-light" />
                  <span className="font-mono text-[11px] uppercase tracking-widest text-brand-light">{a.subtitle}</span>
                </div>
                <h2 className="font-display text-2xl md:text-3xl font-semibold text-white">{a.name}</h2>
                <p className="mt-4 text-white/70 leading-relaxed">{a.body}</p>
                <p className="mt-3 text-sm text-white/50 italic">Organized by {a.org}</p>
                {a.wins?.length > 0 && (
                  <ul className="mt-6 grid sm:grid-cols-2 gap-2">
                    {a.wins.map((w) => (
                      <li key={w} className="flex items-start gap-2.5 text-white/80">
                        <AwardIcon className="h-4 w-4 text-brand-light mt-0.5 shrink-0" />
                        <span className="text-sm">{w}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </motion.article>
          ))}
        </div>
      </section>
    </div>
  );
}
