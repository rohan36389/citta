import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { lazy, Suspense, useEffect, useState } from "react";
import { ArrowRight, ArrowUpRight, Sparkles } from "lucide-react";
import { HOMEPAGE } from "@/data/content";
import ErrorBoundary from "@/components/ErrorBoundary";

const HeroCanvas = lazy(() => import("@/components/HeroCanvas"));

export default function Hero() {
  const H = HOMEPAGE.hero;
  const [ready, setReady] = useState(false);
  useEffect(() => {
    const t = setTimeout(() => setReady(true), 120);
    return () => clearTimeout(t);
  }, []);
  return (
    <section
      id="hero"
      data-testid="hero-section"
      className="relative min-h-[100svh] w-full overflow-hidden section-dark pt-32 pb-16"
    >
      <div className="absolute inset-0">
        {ready && (
          <ErrorBoundary fallback={<div className="absolute inset-0 grid-bg-dark" />}>
            <Suspense fallback={<div className="absolute inset-0 grid-bg-dark" />}> 
              <HeroCanvas />
            </Suspense>
          </ErrorBoundary>
        )}
      </div>
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute inset-0 grid-bg-dark opacity-40" />
        <div className="absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-[#0A0F1E] to-transparent" />
        <div className="absolute inset-x-0 bottom-0 h-64 bg-gradient-to-t from-[#0A0F1E] via-[#0A0F1E]/85 to-transparent" />
      </div>

      <a href="#main-content" className="sr-only focus:not-sr-only">Skip to main content</a>

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <div className="max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="chip mb-6 animate-pulse-ring"
            data-testid="hero-eyebrow"
          >
            <Sparkles className="h-3.5 w-3.5" /> {H.eyebrow}
          </motion.div>

          <h1
            className="font-display text-[clamp(2.4rem,6vw,5.6rem)] leading-[0.98] font-semibold tracking-tight text-white"
            data-testid="hero-title"
          >
            <motion.span
              initial={{ opacity: 0, y: 22 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.15, ease: [0.2, 0.7, 0.2, 1] }}
              className="block"
            >
              {H.titleLead}
            </motion.span>
            <motion.span
              initial={{ opacity: 0, y: 22 }} animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.75, delay: 0.28, ease: [0.2, 0.7, 0.2, 1] }}
              className="block text-gradient-brand"
            >
              {H.titleAccent}
            </motion.span>
          </h1>

          <motion.p
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.55, duration: 0.6 }}
            className="mt-7 max-w-2xl text-lg text-white/70 leading-relaxed"
            data-testid="hero-subtitle"
          >
            {H.subtitle}
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7, duration: 0.6 }}
            className="mt-9 flex flex-wrap gap-3"
          >
            <Link to={H.ctas[0].to} data-testid="hero-cta-primary" className="btn-primary">
              {H.ctas[0].label} <ArrowRight className="h-4 w-4" />
            </Link>
            <a href="#products" data-testid="hero-cta-secondary" className="btn-ghost">
              {H.ctas[1].label} <ArrowUpRight className="h-4 w-4" />
            </a>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            transition={{ delay: 0.95, duration: 0.7 }}
            className="mt-12 flex flex-wrap items-center gap-x-6 gap-y-3"
            data-testid="hero-tags"
          >
            {H.tags.map((t) => (
              <div key={t} className="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-white/50">
                <span className="h-1.5 w-1.5 rounded-full bg-brand-light animate-pulse" /> {t}
              </div>
            ))}
          </motion.div>
        </div>
      </div>


      {/* Bottom-right subtle scroll cue */}
      <div className="absolute bottom-8 right-8 hidden md:flex flex-col items-end gap-2 text-white/40 text-[10px] font-mono uppercase tracking-widest">
        <span>Scroll</span>
        <span className="h-10 w-px bg-gradient-to-b from-white/40 to-transparent" />
      </div>
    </section>
  );
}
