import { motion } from "framer-motion";
import { HOMEPAGE } from "@/data/content";
import SectionHeader from "@/components/SectionHeader";

export default function Why() {
  const W = HOMEPAGE.why;
  return (
    <section id="why" className="relative section-dark py-28 overflow-hidden" data-testid="why-section">
      <div className="aurora opacity-45" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <SectionHeader eyebrow={W.eyebrow} title={W.title} sub={W.sub} />
        <div className="mt-14 grid md:grid-cols-3 gap-5">
          {W.items.map((it, i) => (
            <motion.div
              key={it.n}
              initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
              transition={{ duration: 0.6, delay: i * 0.1 }}
              className="glass-dark rounded-3xl p-7 tilt relative overflow-hidden"
              data-testid={`why-item-${i}`}
            >
              <div className="absolute top-0 right-0 h-32 w-32 bg-gradient-to-br from-brand-blue/20 to-transparent blur-2xl" />
              <div className="relative">
                <div className="mb-5 h-12 w-12 rounded-2xl bg-gradient-to-br from-brand-blue to-brand-light text-white grid place-items-center font-display font-bold text-lg">
                  {it.n}
                </div>
                <h3 className="font-display text-2xl font-semibold text-white leading-tight">{it.title}</h3>
                <p className="mt-3 text-white/60 leading-relaxed">{it.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
