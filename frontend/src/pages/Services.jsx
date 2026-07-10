import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowUpRight, Database, Bot, Compass, Megaphone, Wrench } from "lucide-react";
import { NAV } from "@/data/content";
import SectionHeader from "@/components/SectionHeader";

const icons = { "data-engineering": Database, "enterprise-ai": Bot, "ai-strategy": Compass, "martech-360": Megaphone, "consulting": Wrench };

export default function Services() {
  const items = NAV.primary.find((x) => x.label === "Services").children;
  return (
    <div data-testid="services-index-page" className="relative section-dark min-h-screen pt-36 pb-24 overflow-hidden">
      <div className="aurora opacity-40" />
      <div className="absolute inset-0 grid-bg-dark opacity-30" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <div className="chip mb-5">Services</div>
        <h1 className="font-display text-[clamp(2.4rem,5.5vw,4.8rem)] leading-[1.02] font-semibold tracking-tight text-white">
          End-to-end AI <span className="text-gradient-brand">transformation capabilities.</span>
        </h1>
        <p className="mt-6 text-lg text-white/70 max-w-2xl leading-relaxed">
          Strategy, data, engineering, marketing — everything you need to move enterprise AI from proof-of-concept to production.
        </p>

        <div className="mt-14 grid md:grid-cols-2 lg:grid-cols-3 gap-5">
          {items.map((s, i) => {
            const slug = s.to.replace("/services/", "");
            const Icon = icons[slug] || Wrench;
            return (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                transition={{ duration: 0.55, delay: i * 0.06 }}
                className="glass-dark rounded-2xl p-6 tilt"
                data-testid={`service-index-${slug}`}
              >
                <div className="h-11 w-11 rounded-xl bg-brand-blue/15 border border-brand-blue/25 grid place-items-center mb-4">
                  <Icon className="h-4 w-4 text-brand-light" />
                </div>
                <h3 className="font-display text-xl font-semibold text-white">{s.label}</h3>
                <p className="mt-2 text-sm text-white/50">Content coming soon — <code className="font-mono text-brand-light">{"{{PENDING_CONTENT}}"}</code></p>
                <Link to={s.to} className="mt-4 inline-flex items-center gap-1.5 text-brand-light text-sm group/l">
                  Learn more <ArrowUpRight className="h-3.5 w-3.5 group-hover/l:translate-x-0.5 group-hover/l:-translate-y-0.5 transition-transform" />
                </Link>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
