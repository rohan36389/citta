import { motion } from "framer-motion";
import { HOMEPAGE } from "@/data/content";
import SectionHeader from "@/components/SectionHeader";
import StatValue from "@/components/StatValue";

export default function Fueling() {
  const F = HOMEPAGE.fueling;
  const logos = [...F.logos, ...F.logos];
  return (
    <section className="relative section-light py-28 overflow-hidden" data-testid="fueling-section">
      <div className="absolute inset-0 grid-bg-light opacity-40" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <div className="grid lg:grid-cols-12 gap-10 items-end">
          <div className="lg:col-span-7">
            <SectionHeader eyebrow={F.eyebrow} title={F.title} theme="light" />
          </div>
          <div className="lg:col-span-5 grid grid-cols-3 gap-3">
            {F.stats.map((s, i) => (
              <motion.div
                key={s.l}
                initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.1 }}
                className="bg-slate-950 text-white rounded-2xl p-5 relative overflow-hidden"
                data-testid={`fueling-stat-${i}`}
              >
                <div className="absolute -top-4 -right-4 h-16 w-16 rounded-full bg-brand-light/20 blur-2xl" />
                <div className="relative">
                  <div className="font-display text-3xl md:text-4xl font-bold text-gradient-brand"><StatValue value={s.v} /></div>
                  <p className="mt-1 text-white/70 text-xs">{s.l}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="mt-14 relative marquee-mask">
          <div className="flex gap-10 animate-marquee whitespace-nowrap py-6">
            {logos.map((name, i) => (
              <div
                key={i}
                className="shrink-0 min-w-[170px] h-16 rounded-xl border border-slate-200/70 bg-white/70 backdrop-blur grid place-items-center px-6"
                data-testid={`fueling-logo-${i}`}
              >
                <span className="font-display text-slate-800/80 font-semibold text-lg tracking-tight">{name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
