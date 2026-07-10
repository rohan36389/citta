// Sub-components used by PSPage.jsx — extracted to keep the page under
// ~50 lines and cyclomatic complexity low.

import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowLeft, ArrowUpRight, Check, Sparkles, Layers } from "lucide-react";
import SectionHeader from "@/components/SectionHeader";
import StatValue from "@/components/StatValue";
import CapabilityIcon from "@/components/CapabilityIcon";

export function PSBack({ to, label }) {
  return (
    <Link to={to} className="inline-flex items-center gap-2 text-sm text-white/60 hover:text-white mb-8 group" data-testid="ps-back">
      <ArrowLeft className="h-4 w-4 group-hover:-translate-x-0.5 transition-transform" /> {label}
    </Link>
  );
}

export function PSHero({ cfg, backTo, backLabel }) {
  return (
    <section className="relative section-dark pt-36 pb-24 overflow-hidden" data-testid={`ps-hero-${cfg.slug}`}>
      <div className="aurora-accent opacity-70" />
      <div className="absolute inset-0 grid-bg-dark opacity-30" />
      <div
        className="absolute top-1/2 right-[-10%] -translate-y-1/2 h-[600px] w-[600px] rounded-full opacity-40 blur-3xl animate-gradient-drift"
        style={{ background: "var(--accent-grad)", backgroundSize: "200% 200%" }}
      />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <PSBack to={backTo} label={backLabel} />

        <div className="grid lg:grid-cols-12 gap-10 items-start">
          <div className="lg:col-span-8">
            <motion.div
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.05 }}
              className="chip chip-accent"
            >
              <Sparkles className="h-3.5 w-3.5" /> {cfg.eyebrow}
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.12 }}
              className="mt-5 font-display text-[clamp(2.2rem,5vw,4.4rem)] font-semibold tracking-tight text-white leading-[1.02]"
            >
              {cfg.name}
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.25 }}
              className="mt-5 text-xl md:text-2xl font-display text-gradient-accent"
            >
              {cfg.hero}
            </motion.p>
            <motion.p
              initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="mt-6 text-lg text-white/70 leading-relaxed max-w-2xl"
            >
              {cfg.subtitle}
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.55 }}
              className="mt-9 flex flex-wrap gap-3"
            >
              <Link to="/contact" className="btn-accent">Say Hello! <ArrowUpRight className="h-4 w-4" /></Link>
              <a href="#capabilities" className="btn-ghost">Explore Capabilities</a>
            </motion.div>
          </div>

          <div className="lg:col-span-4 grid grid-cols-2 gap-3">
            {cfg.stats.map((s, i) => (
              <motion.div
                key={s.l}
                initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 + i * 0.08 }}
                className="glass-strong rounded-2xl p-5 relative overflow-hidden"
                data-testid={`ps-stat-${s.l}`}
              >
                <div className="absolute -top-6 -right-6 h-20 w-20 rounded-full opacity-25 blur-2xl" style={{ background: "var(--accent-grad)" }} />
                <div className="relative">
                  <div className="font-display text-3xl font-bold text-gradient-accent"><StatValue value={s.v} /></div>
                  <p className="mt-1 text-white/60 text-xs">{s.l}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

export function PSStakeholders({ stakeholders }) {
  return (
    <section className="relative section-dark2 py-14 overflow-hidden">
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <div className="flex flex-wrap items-center gap-3 justify-center">
          <span className="font-mono text-[11px] uppercase tracking-widest text-white/50 mr-2">Built for</span>
          {stakeholders.map((s) => <span key={s} className="chip chip-accent">{s}</span>)}
        </div>
      </div>
    </section>
  );
}

export function PSCapabilities({ cfg }) {
  const heading = cfg.kind === "product" ? "What it does." : "How it works.";
  return (
    <section id="capabilities" className="relative section-light py-28 overflow-hidden" data-testid="ps-capabilities">
      <div className="absolute inset-0 grid-bg-light opacity-60" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <SectionHeader eyebrow="Capabilities" title={heading} theme="light" />
        <div className="mt-12 grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {cfg.capabilities.map((c, i) => (
            <motion.div
              key={c.t}
              initial={{ opacity: 0, y: 22 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, margin: "-40px" }}
              transition={{ duration: 0.55, delay: (i % 6) * 0.05 }}
              className="group bg-white rounded-2xl p-6 border border-slate-200/70 card-lift"
              data-testid={`ps-capability-${c.t}`}
            >
              <div className="mb-4"><CapabilityIcon label={c.t} className="h-10 w-10" /></div>
              <h3 className="font-display text-lg font-semibold text-slate-950 leading-tight">{c.t}</h3>
              <p className="mt-2 text-sm text-slate-600 leading-relaxed">{c.d}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function PSBestOutcomes({ bestFor, outcomes }) {
  return (
    <section className="relative section-dark2 py-24 overflow-hidden">
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 grid md:grid-cols-2 gap-10">
        <div className="glass-dark rounded-3xl p-8">
          <div className="chip chip-accent mb-4"><Layers className="h-3.5 w-3.5" /> Best For</div>
          <ul className="mt-4 flex flex-wrap gap-2">
            {bestFor.map((b) => (
              <li key={b} className="rounded-full border border-white/10 bg-white/5 px-3.5 py-1.5 text-sm text-white/80">{b}</li>
            ))}
          </ul>
        </div>
        <div className="glass-dark rounded-3xl p-8">
          <div className="chip chip-accent mb-4"><Sparkles className="h-3.5 w-3.5" /> Outcomes</div>
          <ul className="mt-4 space-y-2.5">
            {outcomes.map((o) => (
              <li key={o} className="flex items-start gap-2.5 text-white/85">
                <Check className="h-5 w-5 mt-0.5 shrink-0" style={{ color: "var(--accent-light)" }} />
                <span>{o}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

export function PSWhyGrid({ cfg }) {
  return (
    <section className="relative section-dark py-24 overflow-hidden" data-testid="ps-why-grid">
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <SectionHeader eyebrow="Why choose this OS" title={`Why ${cfg.name}`} />
        <div className="mt-12 grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {cfg.whyGrid.map((w, i) => (
            <motion.div
              key={w}
              initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.05 }}
              className="glass-dark rounded-2xl px-5 py-6 flex items-center gap-3"
            >
              <div className="h-9 w-9 rounded-lg grid place-items-center" style={{ background: "color-mix(in oklab, var(--accent) 15%, transparent)" }}>
                <Check className="h-4 w-4" style={{ color: "var(--accent-light)" }} />
              </div>
              <span className="text-white font-medium">{w}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

export function PSClosing({ cfg }) {
  return (
    <section className="relative section-dark2 py-28 overflow-hidden">
      <div className="aurora-accent opacity-40" />
      <div className="relative mx-auto max-w-4xl px-4 sm:px-6 text-center">
        <h2 className="font-display text-4xl md:text-5xl font-semibold text-white">Ready to deploy?</h2>
        <p className="mt-4 text-white/70 max-w-2xl mx-auto">
          Talk to our engineers about {cfg.name} — we walk you through the architecture, integrations and deployment blueprint.
        </p>
        <div className="mt-8 flex flex-wrap gap-3 justify-center">
          <Link to="/contact" className="btn-accent">Say Hello! <ArrowUpRight className="h-4 w-4" /></Link>
          <Link to="/case-studies" className="btn-ghost">See Case Studies</Link>
        </div>
      </div>
    </section>
  );
}
