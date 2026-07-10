import { motion } from "framer-motion";
import { HOMEPAGE } from "@/data/content";
import SectionHeader from "@/components/SectionHeader";

export default function Positioning() {
  const P = HOMEPAGE.positioning;
  return (
    <section className="relative section-light py-28 overflow-hidden" data-testid="positioning-section">
      <div className="absolute inset-0 grid-bg-light opacity-60" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <div className="grid lg:grid-cols-12 gap-14 items-start">
          <div className="lg:col-span-5">
            <SectionHeader eyebrow={P.eyebrow} title={P.title} theme="light" />
            <p className="mt-6 text-lg text-slate-600 leading-relaxed max-w-lg">{P.lead}</p>
          </div>
          <div className="lg:col-span-7 grid gap-4">
            {P.pillars.map((p, i) => (
              <motion.div
                key={p.n}
                initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.6, delay: i * 0.1 }}
                className="group relative bg-white border border-slate-200/70 rounded-3xl p-8 tilt"
                data-testid={`pillar-${i}`}
              >
                <div className="absolute top-6 right-8 font-display text-7xl font-bold text-slate-100 group-hover:text-brand-blue/15 transition-colors">{p.n}</div>
                <div className="relative">
                  <h3 className="font-display text-2xl font-semibold text-slate-950 leading-tight">{p.title}</h3>
                  <p className="mt-3 text-slate-600 leading-relaxed max-w-2xl">{p.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
