import { useParams, Link } from "react-router-dom";
import { ArrowLeft, ArrowUpRight, Info } from "lucide-react";
import { NAV } from "@/data/content";

export default function ServiceSubPage() {
  const { slug } = useParams();
  const item = NAV.primary.find((x) => x.label === "Services").children.find((c) => c.to.endsWith(slug));
  const label = item?.label || slug;
  return (
    <div data-testid="service-sub-page" className="relative section-dark min-h-screen pt-36 pb-24 overflow-hidden">
      <div className="aurora opacity-30" />
      <div className="absolute inset-0 grid-bg-dark opacity-30" />
      <div className="relative mx-auto max-w-4xl px-4 sm:px-6">
        <Link to="/services" className="inline-flex items-center gap-2 text-sm text-white/60 hover:text-white mb-8 group">
          <ArrowLeft className="h-4 w-4 group-hover:-translate-x-0.5 transition-transform" /> Back to services
        </Link>
        <div className="chip mb-5">Service</div>
        <h1 className="font-display text-[clamp(2.4rem,5.5vw,4.4rem)] font-semibold tracking-tight text-white leading-[1.02]">
          {label}
        </h1>
        <div className="mt-10 rounded-3xl glass-dark p-8">
          <div className="flex items-start gap-3">
            <div className="h-9 w-9 rounded-xl bg-brand-blue/15 border border-brand-blue/25 grid place-items-center shrink-0">
              <Info className="h-4 w-4 text-brand-light" />
            </div>
            <div>
              <h2 className="font-display text-xl text-white font-semibold">Content coming soon</h2>
              <p className="mt-2 text-white/60 leading-relaxed">
                This service page is being finalised. In the meantime, book a strategy call and our engineers will walk you through the {label} playbook, references, and pricing.
              </p>
              <div className="mt-6">
                <Link to="/contact" className="btn-primary">Say Hello! <ArrowUpRight className="h-4 w-4" /></Link>
              </div>
              <p className="mt-4 text-[11px] font-mono text-white/40">{`{{PENDING_CONTENT}}`}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
