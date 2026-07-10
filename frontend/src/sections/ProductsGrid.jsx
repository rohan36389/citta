import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { HOMEPAGE } from "@/data/content";
import { ArrowUpRight, Rocket, Bot, GraduationCap, FlaskConical, Building2 } from "lucide-react";
import SectionHeader from "@/components/SectionHeader";

const icons = [Rocket, Bot, GraduationCap, FlaskConical, Building2];

export default function ProductsGrid() {
  const P = HOMEPAGE.products;
  return (
    <section id="products" className="relative section-light py-28 overflow-hidden" data-testid="products-section">
      <div className="absolute inset-0 grid-bg-light opacity-60" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8">
          <SectionHeader eyebrow={P.eyebrow} title={P.title} theme="light" />
          <p className="text-slate-600 max-w-md">{P.lead}</p>
        </div>

        <div className="mt-14 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {P.items.map((p, i) => {
            const Ico = icons[i];
            const isFeature = i === 0;
            return (
              <motion.div
                key={p.title}
                initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.08 }}
                className={`relative rounded-3xl overflow-hidden border tilt ${
                  isFeature
                    ? "lg:col-span-2 lg:row-span-2 bg-gradient-to-br from-[#0A0F1E] to-[#0F172A] text-white border-white/10 p-10 min-h-[420px]"
                    : "bg-white border-slate-200/70 p-8"
                }`}
                data-testid={`product-card-${i}`}
              >
                {isFeature && (
                  <>
                    <div className="absolute inset-0 grid-bg-dark opacity-30" />
                    <div className="absolute -top-24 -right-24 h-80 w-80 rounded-full bg-brand-blue/25 blur-3xl" />
                    <div className="absolute bottom-0 left-0 h-40 w-40 rounded-full bg-brand-light/20 blur-3xl" />
                  </>
                )}
                <div className="relative flex flex-col h-full">
                  <div className="flex items-center justify-between mb-6">
                    <span className={`font-mono text-xs uppercase tracking-widest ${isFeature ? "text-brand-light" : "text-brand-blue"}`}>{p.n}</span>
                    <div className={`h-11 w-11 rounded-xl grid place-items-center border ${
                      isFeature ? "bg-white/5 border-white/10" : "bg-brand-blue/5 border-brand-blue/20"
                    }`}>
                      <Ico className={`h-5 w-5 ${isFeature ? "text-brand-light" : "text-brand-blue"}`} />
                    </div>
                  </div>
                  <h3 className={`font-display font-semibold leading-tight ${isFeature ? "text-4xl md:text-5xl" : "text-2xl"}`}>{p.title}</h3>
                  <p className={`mt-4 leading-relaxed ${isFeature ? "text-white/70 text-lg max-w-lg" : "text-slate-600"}`}>{p.desc}</p>
                  <Link
                    to={p.to}
                    className={`mt-auto pt-6 inline-flex items-center gap-1.5 group font-medium ${
                      isFeature ? "text-brand-light" : "text-brand-blue"
                    }`}
                    data-testid={`product-link-${i}`}
                  >
                    Learn more <ArrowUpRight className="h-4 w-4 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
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
