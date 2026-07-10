import { motion } from "framer-motion";
import { HOMEPAGE } from "@/data/content";
import { TrendingUp, Users2, Ship } from "lucide-react";
import SectionHeader from "@/components/SectionHeader";
import StatValue from "@/components/StatValue";

const icons = [TrendingUp, Users2, Ship];

// Small chart mocks
function Sparkline() {
  const pts = [10, 14, 12, 22, 30, 44, 60, 72, 78, 88, 92, 98];
  const path = pts.map((y, i) => `${i === 0 ? "M" : "L"} ${(i / (pts.length - 1)) * 200} ${100 - y}`).join(" ");
  return (
    <svg viewBox="0 0 200 100" className="w-full h-16">
      <defs>
        <linearGradient id="spark" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#2563EB" />
          <stop offset="100%" stopColor="#60A5FA" />
        </linearGradient>
      </defs>
      <path d={path} stroke="url(#spark)" strokeWidth="2" fill="none" />
      <path d={`${path} L 200 100 L 0 100 Z`} fill="url(#spark)" opacity="0.15" />
    </svg>
  );
}
function Bars() {
  const bars = [22, 40, 65, 82, 100];
  return (
    <svg viewBox="0 0 200 100" className="w-full h-16">
      {bars.map((h, i) => (
        <rect key={`bar-${h}-${i}`} x={i * 40 + 4} y={100 - h} width={28} height={h} fill="#60A5FA" opacity={0.35 + i * 0.15} rx="3" />
      ))}
    </svg>
  );
}
function RoutePath() {
  return (
    <svg viewBox="0 0 200 100" className="w-full h-16">
      <path d="M 10 80 Q 60 20 100 55 T 190 30" stroke="#60A5FA" strokeWidth="2" fill="none" strokeDasharray="4 3" />
      <circle cx="10" cy="80" r="4" fill="#2563EB" />
      <circle cx="190" cy="30" r="4" fill="#60A5FA" />
    </svg>
  );
}
const charts = [Bars, Sparkline, RoutePath];

export default function Results() {
  const R = HOMEPAGE.results;
  return (
    <section className="relative section-dark py-28 overflow-hidden" data-testid="results-section">
      <div className="absolute inset-0 grid-bg-dark opacity-25" />
      <div className="absolute -top-20 right-1/4 w-96 h-96 rounded-full bg-brand-blue/15 blur-3xl" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <SectionHeader eyebrow={R.eyebrow} title={R.title} lead={R.lead} />

        <div className="mt-14 grid lg:grid-cols-3 gap-5">
          {R.cases.map((c, i) => {
            const Icon = icons[i];
            const Chart = charts[i];
            return (
              <motion.div
                key={c.brand}
                initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.1 }}
                className="glass-strong rounded-3xl p-8 tilt relative overflow-hidden"
                data-testid={`result-case-${i}`}
              >
                <div className="absolute top-0 right-0 h-32 w-32 bg-gradient-to-br from-brand-light/20 to-transparent blur-2xl" />
                <div className="relative">
                  <div className="flex items-center justify-between mb-6">
                    <span className="font-mono text-[11px] uppercase tracking-widest text-white/40">{c.brand}</span>
                    <Icon className="h-4 w-4 text-brand-light" />
                  </div>
                  <div className="font-display text-5xl md:text-6xl font-semibold text-gradient-brand leading-none">
                    <StatValue value={c.metric} />
                  </div>
                  <h4 className="mt-4 font-display text-lg text-white font-medium">{c.label}</h4>
                  <p className="mt-3 text-sm text-white/60 leading-relaxed">{c.desc}</p>
                  <div className="mt-6"><Chart /></div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
