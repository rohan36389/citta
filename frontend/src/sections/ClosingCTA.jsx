import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { HOMEPAGE } from "@/data/content";
import { ArrowUpRight } from "lucide-react";

export default function ClosingCTA() {
  const C = HOMEPAGE.closing;
  return (
    <section className="relative section-dark2 py-28 overflow-hidden" data-testid="closing-cta">
      <div className="aurora opacity-40" />
      <div className="relative mx-auto max-w-5xl px-4 sm:px-6 text-center">
        <motion.h2
          initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          transition={{ duration: 0.7 }}
          className="font-display text-4xl md:text-6xl font-semibold tracking-tight text-white leading-[1.02]"
        >
          {C.title}
        </motion.h2>
        <motion.p
          initial={{ opacity: 0, y: 12 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.15 }}
          className="mt-6 text-lg text-white/70 max-w-2xl mx-auto leading-relaxed"
        >
          {C.desc}
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-10 flex flex-wrap gap-3 justify-center"
        >
          {C.ctas.map((c) => (
            <Link key={c.label} to={c.to} className={c.primary ? "btn-primary" : "btn-ghost"}>
              {c.label} <ArrowUpRight className="h-4 w-4" />
            </Link>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
