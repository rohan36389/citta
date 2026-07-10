import { Link } from "react-router-dom";
import { Linkedin, Twitter, Youtube, Instagram, Phone, Mail, MapPin } from "lucide-react";
import { BRAND, FOOTER } from "@/data/content";

const socialIcons = { LinkedIn: Linkedin, X: Twitter, YouTube: Youtube, Instagram: Instagram };

export default function Footer() {
  return (
    <footer className="relative section-dark border-t border-white/5 pt-20 pb-8 overflow-hidden" data-testid="site-footer">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-brand-light/30 to-transparent" />
      <div className="aurora opacity-25" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <div className="grid grid-cols-2 lg:grid-cols-12 gap-y-12 gap-x-8">
          {/* Brand column */}
          <div className="col-span-2 lg:col-span-4">
            <Link to="/" className="inline-flex items-center gap-3">
              <img src={BRAND.logoSquare} alt="CittaAI" className="h-11 w-11 rounded-lg" />
              <div className="leading-tight">
                <div className="font-display text-white text-2xl font-semibold tracking-tight">
                  {BRAND.wordmark}<span className="text-brand-light font-bold">{BRAND.wordmarkAccent}</span>
                </div>
                <div className="text-white/50 text-[11px] font-mono uppercase tracking-widest">{BRAND.drivenBy}</div>
              </div>
            </Link>
            <p className="mt-5 text-sm text-white/60 max-w-xs leading-relaxed">
              The intelligence layer for the modern enterprise. Engineering autonomy from the ground up.
            </p>
            <p className="mt-5 font-display italic text-brand-light text-sm">{BRAND.tagline}</p>

            <div className="mt-6 flex items-center gap-3">
              {FOOTER.socials.map(({ l, href }) => {
                const Ico = socialIcons[l] || Linkedin;
                return (
                  <a key={l} href={href} aria-label={l} className="h-9 w-9 rounded-full border border-white/10 grid place-items-center text-white/70 hover:text-white hover:border-brand-light transition-colors">
                    <Ico className="h-4 w-4" />
                  </a>
                );
              })}
            </div>
          </div>

          {FOOTER.columns.map((col) => (
            <div key={col.h} className="lg:col-span-2">
              <h4 className="font-mono text-[11px] uppercase tracking-widest text-brand-light mb-4">{col.h}</h4>
              <ul className="space-y-2.5">
                {col.links.map((l) => (
                  <li key={l.l}>
                    <Link to={l.to} className="text-sm text-white/70 hover:text-white transition-colors">{l.l}</Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          {/* Contact column */}
          <div className="col-span-2 lg:col-span-2">
            <h4 className="font-mono text-[11px] uppercase tracking-widest text-brand-light mb-4">Contact</h4>
            <ul className="space-y-3 text-sm text-white/70">
              <li className="flex items-start gap-2">
                <Phone className="h-4 w-4 mt-0.5 text-white/50" />
                <a href={`tel:${FOOTER.contact.phoneRaw}`} className="hover:text-white">{FOOTER.contact.phone}</a>
              </li>
              <li className="flex items-start gap-2">
                <Mail className="h-4 w-4 mt-0.5 text-white/50" />
                <a href={`mailto:${FOOTER.contact.email}`} className="hover:text-white">{FOOTER.contact.email}</a>
              </li>
              <li className="flex items-start gap-2">
                <MapPin className="h-4 w-4 mt-0.5 text-white/50 shrink-0" />
                <span className="leading-relaxed">{FOOTER.contact.address}</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Certifications */}
        <div className="mt-14 pt-8 border-t border-white/5 flex flex-wrap items-center gap-4">
          <span className="font-mono text-[11px] uppercase tracking-widest text-white/40 mr-2">Certified</span>
          {FOOTER.badges.map((b) => (
            <div key={b.alt} className="h-14 rounded-xl bg-white/95 px-3 py-1.5 grid place-items-center" title={b.alt}>
              <img src={b.src} alt={b.alt} className="h-full w-auto object-contain" />
            </div>
          ))}
        </div>

        <div className="mt-8 pt-6 border-t border-white/5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <p className="text-xs text-white/45 font-mono">{FOOTER.legal.copy}</p>
          <div className="flex flex-wrap gap-5">
            {FOOTER.legal.links.map((l) => (
              <Link key={l.l} to={l.to} className="text-xs text-white/50 hover:text-white/80">{l.l}</Link>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
