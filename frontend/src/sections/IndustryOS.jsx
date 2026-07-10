import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { HOMEPAGE } from "@/data/content";
import { ShoppingBag, HeartPulse, Building, ArrowUpRight } from "lucide-react";
import SectionHeader from "@/components/SectionHeader";

const icons = [ShoppingBag, HeartPulse, Building];

export default function IndustryOS() {
  const S = HOMEPAGE.solutions;
  return (
    <section id="solutions" className="relative section-light py-28 overflow-hidden" data-testid="industryos-section">
      <div className="absolute inset-0 grid-bg-light opacity-50" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <SectionHeader eyebrow={S.eyebrow} title={S.title} lead={S.lead} theme="light" />

        <div className="mt-14 grid md:grid-cols-3 gap-5">
          {S.items.map((it, i) => {
            const Icon = icons[i];
            return (
              <motion.div
                key={it.name}
                initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.1 }}
                className="group relative rounded-3xl border border-slate-200/70 bg-white p-8 tilt overflow-hidden"
                data-testid={`industryos-card-${i}`}
              >
                <div className="absolute -top-16 -right-16 h-40 w-40 rounded-full bg-brand-blue/10 blur-3xl group-hover:bg-brand-blue/20 transition-colors" />
                <div className="relative">
                  <div className="h-12 w-12 rounded-2xl bg-brand-blue/8 border border-brand-blue/20 grid place-items-center">
                    <Icon className="h-5 w-5 text-brand-blue" />
                  </div>
                  <h3 className="mt-6 font-display text-2xl font-semibold text-slate-950">{it.name}</h3>
                  <p className="mt-3 text-slate-600 leading-relaxed">{it.tag}</p>
                  <Link to={it.to} className="mt-6 inline-flex items-center gap-1.5 text-brand-blue font-medium group/l">
                    Explore OS <ArrowUpRight className="h-4 w-4 group-hover/l:translate-x-0.5 group-hover/l:-translate-y-0.5 transition-transform" />
                  </Link>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
