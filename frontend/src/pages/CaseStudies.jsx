import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowUpRight, TrendingUp, Users2, Ship } from "lucide-react";
import { CASESTUDIES } from "@/data/content";
import SectionHeader from "@/components/SectionHeader";
import StatValue from "@/components/StatValue";

const icons = [TrendingUp, Users2, Ship];

// Chart mocks
function Bars() {
  const bars = [22, 40, 65, 82, 100];
  return (
    <svg viewBox="0 0 200 90" className="w-full h-24">
      {bars.map((h, i) => (
        <rect key={`bar-${h}-${i}`} x={i * 40 + 4} y={90 - (h * 0.9)} width={28} height={h * 0.9} fill="#60A5FA" opacity={0.35 + i * 0.15} rx="3" />
      ))}
    </svg>
  );
}
function Spark() {
  const pts = [8, 12, 10, 18, 26, 40, 55, 68, 74, 82, 88, 96];
  const path = pts.map((y, i) => `${i === 0 ? "M" : "L"} ${(i / (pts.length - 1)) * 200} ${100 - y}`).join(" ");
  return (
    <svg viewBox="0 0 200 100" className="w-full h-24">
      <defs>
        <linearGradient id="csSpark" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#2563EB" />
          <stop offset="100%" stopColor="#60A5FA" />
        </linearGradient>
      </defs>
      <path d={path} stroke="url(#csSpark)" strokeWidth="2.5" fill="none" />
      <path d={`${path} L 200 100 L 0 100 Z`} fill="url(#csSpark)" opacity="0.18" />
    </svg>
  );
}
function Route() {
  return (
    <svg viewBox="0 0 200 100" className="w-full h-24">
      <path d="M 10 80 Q 60 20 100 55 T 190 30" stroke="#60A5FA" strokeWidth="2.5" fill="none" strokeDasharray="4 3" />
      <circle cx="10" cy="80" r="5" fill="#2563EB" />
      <circle cx="190" cy="30" r="5" fill="#60A5FA" />
      <text x="12" y="72" fontSize="8" fill="#94A3B8" fontFamily="JetBrains Mono">India</text>
      <text x="150" y="24" fontSize="8" fill="#94A3B8" fontFamily="JetBrains Mono">Export</text>
    </svg>
  );
}
const charts = [Bars, Spark, Route];

export default function CaseStudies() {
  const C = CASESTUDIES;
  return (
    <div data-testid="case-studies-page">
      <section className="relative section-dark pt-36 pb-16 overflow-hidden">
        <div className="aurora opacity-40" />
        <div className="absolute inset-0 grid-bg-dark opacity-30" />
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
          <div className="chip mb-5">{C.eyebrow}</div>
          <h1 className="font-display text-[clamp(2.4rem,5.5vw,4.8rem)] leading-[1.02] font-semibold tracking-tight text-white">
            <span className="text-gradient-brand">{C.title}</span>
          </h1>
          <p className="mt-6 text-lg text-white/70 max-w-2xl leading-relaxed">
            We engineer measurable outcomes. Here is the impact of deploying autonomous cognitive architectures in the real world.
          </p>
        </div>
      </section>

      <section className="relative section-dark2 py-20 overflow-hidden">
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
          <div className="grid lg:grid-cols-3 gap-5">
            {C.cases.map((c, i) => {
              const Ico = icons[i];
              const Chart = charts[i];
              return (
                <motion.article
                  key={c.brand}
                  initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: i * 0.1 }}
                  className="glass-strong rounded-3xl p-8 tilt overflow-hidden relative"
                  data-testid={`case-study-${i}`}
                >
                  <div className="absolute -top-16 -right-16 h-40 w-40 rounded-full bg-brand-blue/25 blur-3xl" />
                  <div className="relative">
                    <div className="flex items-center justify-between mb-6">
                      <span className="font-mono text-[11px] uppercase tracking-widest text-white/50">{c.brand}</span>
                      <Ico className="h-4 w-4 text-brand-light" />
                    </div>
                    <div className="font-display text-6xl font-semibold text-gradient-brand leading-none">
                      <StatValue value={c.metric} />
                    </div>
                    <h4 className="mt-4 font-display text-xl text-white font-medium">{c.label}</h4>
                    <p className="mt-3 text-white/60 leading-relaxed">{c.desc}</p>
                    <div className="mt-6"><Chart /></div>
                  </div>
                </motion.article>
              );
            })}
          </div>

          <div className="mt-16 rounded-3xl glass-dark p-8 md:p-10 text-center">
            <h3 className="font-display text-2xl md:text-3xl text-white font-semibold">Your outcome is next.</h3>
            <p className="mt-3 text-white/60 max-w-2xl mx-auto">Book a call — we walk you through the ROI blueprint for your industry.</p>
            <div className="mt-6"><Link to="/contact" className="btn-primary inline-flex">Say Hello! <ArrowUpRight className="h-4 w-4" /></Link></div>
          </div>
        </div>
      </section>
    </div>
  );
}
