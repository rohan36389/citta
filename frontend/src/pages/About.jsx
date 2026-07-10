import { motion } from "framer-motion";
import { Linkedin, ShieldCheck, Timer, LifeBuoy, Cpu, Sparkles } from "lucide-react";
import { ABOUT } from "@/data/content";
import SectionHeader from "@/components/SectionHeader";
import StatValue from "@/components/StatValue";

const whyIcons = [ShieldCheck, Timer, LifeBuoy, Cpu];

function TeamCard({ person, size = "lg", i = 0 }) {
  const isLarge = size === "lg";
  return (
    <motion.figure
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      transition={{ duration: 0.65, delay: i * 0.08, ease: [0.2, 0.7, 0.2, 1] }}
      className={`group relative rounded-3xl overflow-hidden bg-slate-950 border border-white/8 ${isLarge ? "" : ""}`}
      data-testid={`team-card-${person.name.toLowerCase().replace(/\s+/g, "-")}`}
    >
      {/* Photo */}
      <div className={`relative overflow-hidden ${isLarge ? "aspect-[4/5]" : "aspect-[3/4]"}`}>
        <div className="absolute inset-0 bg-gradient-to-br from-brand-blue/25 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        <img
          src={person.photo}
          alt={person.name}
          loading="lazy"
          className="w-full h-full object-cover object-top transition-transform duration-[900ms] ease-[cubic-bezier(0.2,0.7,0.2,1)] group-hover:scale-[1.04]"
        />
        {/* Bottom gradient overlay on hover */}
        <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-slate-950/90 via-slate-950/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        {/* LinkedIn on hover */}
        {person.linkedin && (
          <a
            href={person.linkedin}
            target="_blank" rel="noreferrer"
            aria-label={`${person.name} on LinkedIn`}
            className="absolute bottom-4 right-4 h-9 w-9 rounded-full bg-brand-blue text-white grid place-items-center opacity-0 translate-y-2 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-500 shadow-lg shadow-brand-blue/40"
            data-testid={`team-linkedin-${person.name.toLowerCase().replace(/\s+/g, "-")}`}
          >
            <Linkedin className="h-4 w-4" />
          </a>
        )}
      </div>

      {/* Caption */}
      <figcaption className="p-5 relative">
        <h4 className={`font-display font-semibold text-white ${isLarge ? "text-xl" : "text-base"}`}>
          {person.name}
          <span className="block h-[2px] w-0 mt-1.5 rounded-full bg-gradient-to-r from-brand-blue to-brand-light group-hover:w-16 transition-[width] duration-500" />
        </h4>
        <p className={`mt-1.5 text-white/60 ${isLarge ? "text-sm" : "text-xs"}`}>{person.title}</p>
      </figcaption>
    </motion.figure>
  );
}

// Abstract skyscraper SVG illustration used as About hero visual (in-lieu of stock photograph)
function SkyscraperArt() {
  return (
    <svg viewBox="0 0 400 500" className="w-full h-full">
      <defs>
        <linearGradient id="bldg" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#60A5FA" stopOpacity="0.4" />
          <stop offset="100%" stopColor="#2563EB" stopOpacity="0.05" />
        </linearGradient>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0F172A" />
          <stop offset="100%" stopColor="#0A0F1E" />
        </linearGradient>
      </defs>
      <rect width="400" height="500" fill="url(#sky)" />
      {/* Buildings */}
      {[[60, 200, 60, 300], [140, 120, 80, 380], [240, 60, 90, 440], [345, 180, 40, 320]].map(([x, y, w, h], i) => (
        <g key={i}>
          <rect x={x} y={y} width={w} height={h} fill="url(#bldg)" stroke="#334155" strokeWidth="1" />
          {/* Windows grid */}
          {Array.from({ length: Math.floor(h / 20) }).map((_, r) => (
            Array.from({ length: Math.floor(w / 15) }).map((__, c) => {
              const lit = Math.random() > 0.6;
              return (
                <rect key={`${r}-${c}`}
                  x={x + 4 + c * 15} y={y + 6 + r * 20} width="8" height="10"
                  fill={lit ? "#60A5FA" : "#1E293B"} opacity={lit ? 0.85 : 0.4}
                />
              );
            })
          ))}
        </g>
      ))}
    </svg>
  );
}

export default function About() {
  const A = ABOUT;
  return (
    <div data-testid="about-page">
      {/* HERO */}
      <section className="relative section-dark pt-36 pb-24 overflow-hidden">
        <div className="aurora opacity-45" />
        <div className="absolute inset-0 grid-bg-dark opacity-30" />
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
          <div className="grid lg:grid-cols-12 gap-10 items-center">
            <div className="lg:col-span-7">
              <div className="chip mb-5"><Sparkles className="h-3.5 w-3.5" /> {A.eyebrow}</div>
              <h1 className="font-display text-[clamp(2.4rem,5.5vw,4.8rem)] leading-[1.02] font-semibold tracking-tight text-white">
                {A.title} <span className="text-gradient-brand">{A.titleAccent}</span>
              </h1>
              <p className="mt-6 text-lg md:text-xl text-white/70 leading-relaxed max-w-2xl">{A.lead}</p>
            </div>
            <div className="lg:col-span-5">
              <div className="relative rounded-3xl overflow-hidden aspect-[4/5] glass-strong">
                <SkyscraperArt />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/40 to-transparent" />
                <div className="absolute bottom-6 left-6 right-6">
                  <span className="chip">Enterprise Scale</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-3">
            {A.stats.map((s, i) => (
              <motion.div
                key={s.l}
                initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.08 }}
                className="glass-dark rounded-2xl p-5"
                data-testid={`about-stat-${i}`}
              >
                <div className="font-display text-4xl font-bold text-gradient-brand"><StatValue value={s.v} /></div>
                <p className="mt-1 text-white/60 text-sm">{s.l}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Story */}
      <section className="relative section-light py-24 overflow-hidden">
        <div className="absolute inset-0 grid-bg-light opacity-50" />
        <div className="relative mx-auto max-w-4xl px-4 sm:px-6 text-center">
          <SectionHeader eyebrow="Our Story" title={A.storyTitle} theme="light" align="center" />
          <p className="mt-6 text-lg text-slate-600 leading-relaxed max-w-3xl mx-auto">{A.story}</p>
        </div>
      </section>

      {/* Why enterprises choose us */}
      <section className="relative section-dark2 py-24 overflow-hidden">
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
          <SectionHeader eyebrow="Trust" title="Why Enterprises Choose Us" />
          <div className="mt-12 grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {A.why.map((w, i) => {
              const Ico = whyIcons[i];
              return (
                <motion.div
                  key={w.t}
                  initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                  transition={{ duration: 0.55, delay: i * 0.08 }}
                  className="glass-dark rounded-2xl p-6 tilt"
                  data-testid={`about-why-${i}`}
                >
                  <div className="h-10 w-10 rounded-xl bg-brand-blue/15 border border-brand-blue/25 grid place-items-center mb-4">
                    <Ico className="h-4 w-4 text-brand-light" />
                  </div>
                  <h3 className="font-display text-lg font-semibold text-white">{w.t}</h3>
                  <p className="mt-2 text-sm text-white/60 leading-relaxed">{w.d}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Principles */}
      <section className="relative section-light py-24 overflow-hidden">
        <div className="absolute inset-0 grid-bg-light opacity-50" />
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
          <SectionHeader eyebrow="Principles" title="What we stand for" theme="light" />
          <div className="mt-12 grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {A.principles.map((p, i) => (
              <motion.div
                key={p.t}
                initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                transition={{ duration: 0.55, delay: i * 0.08 }}
                className="bg-white rounded-2xl p-6 border border-slate-200/70 card-lift"
                data-testid={`about-principle-${i}`}
              >
                <div className="font-mono text-[11px] text-brand-blue uppercase tracking-widest">P/0{i + 1}</div>
                <h3 className="mt-2 font-display text-lg font-semibold text-slate-950">{p.t}</h3>
                <p className="mt-2 text-sm text-slate-600 leading-relaxed">{p.d}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* TEAM — Signature wow moment (Section 3.6) */}
      <section id="team" className="relative section-dark2 py-28 overflow-hidden" data-testid="about-team-section">
        <div className="aurora opacity-30" />
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
          <SectionHeader eyebrow="The People" title={A.team.title} lead={A.team.subtitle} />

          {/* Leaders row (3 large) */}
          <div className="mt-14 grid grid-cols-1 md:grid-cols-3 gap-6">
            {A.team.leaders.map((p, i) => (
              <TeamCard key={p.name} person={p} size="lg" i={i} />
            ))}
          </div>

          {/* Second row (4 smaller) */}
          <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-5">
            {A.team.others.map((p, i) => (
              <TeamCard key={p.name} person={p} size="sm" i={i} />
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

