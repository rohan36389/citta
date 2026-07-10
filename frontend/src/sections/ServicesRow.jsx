import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { HOMEPAGE } from "@/data/content";
import { Database, Bot, Compass, Megaphone, ArrowRight } from "lucide-react";
import SectionHeader from "@/components/SectionHeader";

const icons = [Database, Bot, Compass, Megaphone];

export default function ServicesRow() {
  const S = HOMEPAGE.services;
  return (
    <section id="services" className="relative section-dark py-28 overflow-hidden" data-testid="services-section">
      <div className="absolute inset-0 grid-bg-dark opacity-30" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <SectionHeader eyebrow={S.eyebrow} title={S.title} lead={S.lead} />
        <div className="mt-14 grid md:grid-cols-2 gap-5">
          {S.items.map((s, i) => {
            const Icon = icons[i];
            return (
              <motion.article
                key={s.title}
                initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.08 }}
                className="group glass-dark rounded-3xl p-8 md:p-10 tilt relative overflow-hidden"
                data-testid={`service-card-${i}`}
              >
                <div className="absolute top-0 right-0 h-40 w-40 bg-gradient-to-br from-brand-light/15 to-transparent blur-3xl opacity-70" />
                <div className="relative">
                  <div className="flex items-start justify-between mb-6">
                    <div className="h-12 w-12 rounded-2xl bg-white/5 border border-white/10 grid place-items-center">
                      <Icon className="h-5 w-5 text-brand-light" />
                    </div>
                    <span className="font-mono text-[11px] uppercase tracking-widest text-white/40">S/0{i + 1}</span>
                  </div>
                  <h3 className="font-display text-2xl md:text-3xl font-semibold text-white">{s.title}</h3>
                  <p className="mt-2 text-brand-light/90 text-sm">{s.sub}</p>
                  <p className="mt-4 text-white/60 leading-relaxed">{s.desc}</p>
                  <Link to={s.to} className="mt-6 inline-flex items-center gap-1.5 text-brand-light text-sm group/l">
                    Learn more <ArrowRight className="h-3.5 w-3.5 group-hover/l:translate-x-1 transition-transform" />
                  </Link>
                </div>
              </motion.article>
            );
          })}
        </div>
        <div className="mt-12 flex justify-start">
          <Link to={S.cta.to} className="btn-ghost group" data-testid="services-view-all">
            {S.cta.label} <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
      </div>
    </section>
  );
}
