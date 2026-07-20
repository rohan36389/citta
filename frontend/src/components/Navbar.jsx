import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Globe, ChevronDown, ArrowUpRight } from "lucide-react";
import { NAV, BRAND } from "@/data/content";

function NavLink({ item }) {
  const [open, setOpen] = useState(false);
  const hasChildren = !!item.children?.length;

  if (!hasChildren) {
    return (
      <Link
        to={item.to}
        data-testid={`nav-link-${item.label.toLowerCase().replace(/\s+/g, "-")}`}
        className="text-sm text-white/85 hover:text-white transition-colors relative group py-2"
      >
        {item.label}
        <span className="absolute -bottom-0.5 left-0 h-px w-0 bg-brand-light group-hover:w-full transition-all duration-300" />
      </Link>
    );
  }

  return (
    <div className="relative" onMouseEnter={() => setOpen(true)} onMouseLeave={() => setOpen(false)}>
      <button
        onClick={() => setOpen((v) => !v)}
        data-testid={`nav-menu-${item.label.toLowerCase()}`}
        className="text-sm text-white/85 hover:text-white transition-colors relative group inline-flex items-center gap-1 py-2"
      >
        {item.label}
        <ChevronDown className={`h-3.5 w-3.5 transition-transform ${open ? "rotate-180" : ""}`} />
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 6, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 4, scale: 0.98 }}
            transition={{ duration: 0.18, ease: [0.2, 0.7, 0.2, 1] }}
            className="absolute left-1/2 -translate-x-1/2 top-full pt-3 z-50"
          >
            <div className="glass-strong rounded-2xl p-3 min-w-[280px] shadow-2xl">
              {item.children.map((c) => (
                <Link
                  key={c.label}
                  to={c.to}
                  className="group flex items-start gap-3 rounded-xl px-3 py-2.5 hover:bg-white/6 transition-colors"
                >
                  <div className="mt-1 h-1.5 w-1.5 rounded-full bg-brand-light shrink-0 group-hover:scale-125 transition-transform" />
                  <div>
                    <div className="text-white text-sm font-medium">{c.label}</div>
                    {c.note && <div className="text-white/50 text-[11px] font-mono uppercase tracking-wider mt-0.5">{c.note}</div>}
                  </div>
                </Link>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const { pathname } = useLocation();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  useEffect(() => { setOpen(false); }, [pathname]);

  return (
    <header className="fixed top-0 inset-x-0 z-50" data-testid="site-navbar">
      <motion.div
        initial={{ y: -24, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.55, ease: [0.2, 0.7, 0.2, 1] }}
        className="mx-auto mt-4 max-w-7xl px-4 sm:px-6"
      >
        {/* Outer row: logo left + pill right */}
        <div className="flex items-center gap-4">

          {/* ── Full logo — outside the pill ── */}
          <Link to="/" data-testid="nav-brand" className="shrink-0 group">
            <img
              src="/assets/brand/logo-wide.png"
              alt="CittaAI — Driven by Fixity"
              className="h-16 w-auto object-contain transition-transform duration-300 group-hover:scale-[1.03]"
              style={{ maxWidth: "240px", mixBlendMode: "screen" }}
            />
          </Link>

          {/* ── Nav pill ── */}
          <div className={`flex flex-1 items-center justify-between rounded-full pl-5 pr-2 py-2 transition-all duration-300 ${
            scrolled ? "glass-strong shadow-2xl" : "glass-dark"
          }`}>
            <nav className="hidden lg:flex items-center gap-7">
              {NAV.primary.map((item) => <NavLink key={item.label} item={item} />)}
            </nav>

            <div className="hidden lg:flex items-center gap-2">
              <button className="inline-flex items-center gap-1.5 text-sm text-white/70 hover:text-white px-3 py-2 rounded-full transition-colors" data-testid="nav-lang">
                <Globe className="h-4 w-4" /> {NAV.language}
              </button>
              <Link to={NAV.cta.to} data-testid="nav-cta" className="btn-primary !py-2 !px-4 !text-[13px]">
                {NAV.cta.label} <ArrowUpRight className="h-3.5 w-3.5" />
              </Link>
            </div>

            <button
              onClick={() => setOpen((v) => !v)}
              data-testid="nav-mobile-toggle"
              className="lg:hidden h-10 w-10 rounded-full grid place-items-center border border-white/10 text-white"
              aria-label="Menu"
            >
              {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>{/* end pill */}
        </div>{/* end outer row */}

        <AnimatePresence>
          {open && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="lg:hidden mt-2 rounded-2xl glass-strong p-4"
              data-testid="mobile-menu"
            >
              <div className="flex flex-col divide-y divide-white/5">
                {NAV.primary.map((item) => (
                  <div key={item.label} className="py-2">
                    {item.children?.length ? (
                      <details className="group">
                        <summary className="flex items-center justify-between cursor-pointer text-white/90 py-2 list-none">
                          <span className="font-medium">{item.label}</span>
                          <ChevronDown className="h-4 w-4 transition-transform group-open:rotate-180" />
                        </summary>
                        <div className="pl-3 py-1 space-y-1">
                          {item.children.map((c) => (
                            <Link key={c.label} to={c.to} className="block text-sm text-white/70 hover:text-white py-1.5">
                              {c.label}
                            </Link>
                          ))}
                        </div>
                      </details>
                    ) : (
                      <Link to={item.to} className="block text-white/90 py-2 font-medium">{item.label}</Link>
                    )}
                  </div>
                ))}
                <Link to={NAV.cta.to} className="btn-primary justify-center mt-4">
                  {NAV.cta.label}
                </Link>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </header>
  );
}
