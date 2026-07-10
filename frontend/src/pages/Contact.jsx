import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowUpRight, Phone, Mail, MapPin, ShieldCheck } from "lucide-react";
import { CONTACT_PAGE, CONTACT } from "@/data/content";
import SectionHeader from "@/components/SectionHeader";

export default function Contact() {
  const C = CONTACT_PAGE;
  const [inquiry, setInquiry] = useState(C.inquiryTypes[0]);
  const [status, setStatus] = useState(null);

  const submit = (e) => {
    e.preventDefault();
    setStatus("sent");
    setTimeout(() => setStatus(null), 3500);
  };

  const cardIcons = [Phone, Mail, MapPin];

  return (
    <div data-testid="contact-page" className="relative section-dark min-h-screen pt-36 pb-24 overflow-hidden">
      <div className="aurora opacity-40" />
      <div className="absolute inset-0 grid-bg-dark opacity-30" />
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6">
        <div className="max-w-3xl">
          <div className="chip mb-5">{C.eyebrow}</div>
          <h1 className="font-display text-[clamp(2.2rem,5vw,4.4rem)] font-semibold tracking-tight text-white leading-[1.02]">
            {C.title} <span className="text-gradient-brand">{C.titleAccent}</span>
          </h1>
          <p className="mt-6 text-lg text-white/70 leading-relaxed max-w-2xl">{C.lead}</p>
        </div>

        {/* Contact cards */}
        <div className="mt-14 grid md:grid-cols-3 gap-5">
          {C.cards.map((c, i) => {
            const Ico = cardIcons[i];
            const Wrap = ({ children }) => c.href ? <a href={c.href} className="block">{children}</a> : <div>{children}</div>;
            return (
              <motion.div
                key={c.t}
                initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.08 }}
                className="glass-dark rounded-3xl p-6 tilt"
                data-testid={`contact-card-${i}`}
              >
                <Wrap>
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-xl bg-white/5 border border-white/10 grid place-items-center">
                      <Ico className="h-4 w-4 text-brand-light" />
                    </div>
                    <span className="font-mono text-xs uppercase tracking-widest text-white/50">{c.t}</span>
                  </div>
                  <div className="mt-4 font-display text-white text-lg font-medium leading-snug">{c.v}</div>
                  <p className="mt-2 text-sm text-white/60 leading-relaxed">{c.sub}</p>
                </Wrap>
              </motion.div>
            );
          })}
        </div>

        {/* Form */}
        <div className="mt-14 grid lg:grid-cols-12 gap-8">
          <motion.form
            initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            onSubmit={submit}
            className="lg:col-span-8 glass-strong rounded-3xl p-8"
            data-testid="contact-form"
          >
            <div className="grid md:grid-cols-2 gap-4">
              <div className="md:col-span-2">
                <label className="font-mono text-[10px] uppercase tracking-widest text-white/50">Inquiry Type</label>
                <select
                  value={inquiry} onChange={(e) => setInquiry(e.target.value)}
                  data-testid="contact-inquiry"
                  className="mt-1 w-full bg-white/5 border border-white/10 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-brand-light"
                >
                  {C.inquiryTypes.map((i) => <option key={i} className="bg-slate-950">{i}</option>)}
                </select>
              </div>
              <div>
                <label className="font-mono text-[10px] uppercase tracking-widest text-white/50">Name</label>
                <input required data-testid="contact-name" className="mt-1 w-full bg-white/5 border border-white/10 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-brand-light" />
              </div>
              <div>
                <label className="font-mono text-[10px] uppercase tracking-widest text-white/50">Phone</label>
                <input data-testid="contact-phone" className="mt-1 w-full bg-white/5 border border-white/10 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-brand-light" />
              </div>
              <div>
                <label className="font-mono text-[10px] uppercase tracking-widest text-white/50">Business Email</label>
                <input required type="email" data-testid="contact-email" className="mt-1 w-full bg-white/5 border border-white/10 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-brand-light" />
              </div>
              <div>
                <label className="font-mono text-[10px] uppercase tracking-widest text-white/50">Company</label>
                <input data-testid="contact-company" className="mt-1 w-full bg-white/5 border border-white/10 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-brand-light" />
              </div>
              <div className="md:col-span-2">
                <label className="font-mono text-[10px] uppercase tracking-widest text-white/50">Message</label>
                <textarea rows={5} data-testid="contact-message" className="mt-1 w-full bg-white/5 border border-white/10 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-brand-light resize-none" />
              </div>
            </div>
            {/* reCAPTCHA placeholder */}
            <div className="mt-5 flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 px-4 py-3" data-testid="contact-recaptcha">
              <div className="h-6 w-6 rounded-md border border-white/20 grid place-items-center">
                <ShieldCheck className="h-3.5 w-3.5 text-brand-light" />
              </div>
              <span className="text-sm text-white/70">I'm not a robot</span>
              <span className="ml-auto text-[10px] font-mono text-white/40">reCAPTCHA</span>
            </div>
            <button type="submit" data-testid="contact-submit" className="btn-primary mt-6 w-full justify-center">
              Send Message <ArrowUpRight className="h-4 w-4" />
            </button>
            {status === "sent" && (
              <p className="mt-4 text-sm text-emerald-400 font-mono text-center">Message sent — we'll respond within 24 hours.</p>
            )}
            <p className="text-[11px] text-white/40 text-center mt-4 font-mono">{CONTACT.response}</p>
          </motion.form>

          {/* Side info */}
          <div className="lg:col-span-4 space-y-4">
            <div className="glass-dark rounded-3xl p-6">
              <h4 className="font-display text-lg text-white font-semibold">Speak to sales</h4>
              <p className="mt-2 text-sm text-white/60">Enterprise-grade deployments. Named engineers. Measurable outcomes.</p>
              <a href={`tel:${CONTACT.phoneRaw}`} className="mt-4 block text-brand-light hover:underline font-mono">{CONTACT.phone}</a>
            </div>
            <div className="glass-dark rounded-3xl p-6">
              <h4 className="font-display text-lg text-white font-semibold">Careers & press</h4>
              <p className="mt-2 text-sm text-white/60">For careers, partnerships, and press — use the form with the appropriate inquiry type.</p>
              <a href={`mailto:${CONTACT.email}`} className="mt-4 block text-brand-light hover:underline font-mono">{CONTACT.email}</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
