import { motion } from "framer-motion";
import { HOMEPAGE } from "@/data/content";
import { Database, MessageSquare, Video, ArrowRight } from "lucide-react";
import SectionHeader from "@/components/SectionHeader";

const icons = [Database, MessageSquare, Video];

export default function Stack() {
  const S = HOMEPAGE.stack;
  return (
    <section className="relative section-dark py-28 overflow-hidden" data-testid="stack-section">
      <div className="aurora opacity-40" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <div className="max-w-3xl">
          <SectionHeader eyebrow={S.eyebrow} title={S.title} />
          <p className="mt-5 text-brand-light font-mono text-sm uppercase tracking-widest">{S.outcome}</p>
        </div>
        <div className="mt-14 relative">
          <div className="hidden md:block absolute top-1/2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-brand-blue/40 to-transparent" />
          <div className="grid md:grid-cols-3 gap-5 relative">
            {S.steps.map((s, i) => {
              const Icon = icons[i];
              return (
                <motion.div
                  key={s.n}
                  initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: i * 0.12 }}
                  className="glass-strong rounded-3xl p-7 relative tilt"
                  data-testid={`stack-step-${i}`}
                >
                  <div className="flex items-center justify-between mb-6">
                    <span className="font-mono text-[11px] uppercase tracking-widest text-brand-light">{s.n}</span>
                    {i < S.steps.length - 1 && (
                      <ArrowRight className="h-4 w-4 text-white/30 hidden md:block" />
                    )}
                  </div>
                  <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-brand-blue/20 to-brand-light/10 border border-brand-blue/30 grid place-items-center mb-5">
                    <Icon className="h-5 w-5 text-brand-light" />
                  </div>
                  <h3 className="font-display text-xl font-semibold text-white">{s.title}</h3>
                  <p className="mt-2 text-white/60 text-sm leading-relaxed">{s.desc}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
