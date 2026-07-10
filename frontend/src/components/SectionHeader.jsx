import { motion } from "framer-motion";

export default function SectionHeader({ eyebrow, title, titleAccent, sub, lead, align = "left", theme = "dark" }) {
  const textColor = theme === "light" ? "text-[color:var(--text-primary-dark)]" : "text-white";
  const leadColor = theme === "light" ? "text-slate-600" : "text-white/65";
  const chip = theme === "light" ? "chip chip-light" : "chip";
  const alignCls = align === "center" ? "text-center mx-auto" : "";
  return (
    <div className={`max-w-3xl ${alignCls}`}>
      {eyebrow && (
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-60px" }}
          transition={{ duration: 0.5 }}
          className={`${chip} mb-5 ${align === "center" ? "mx-auto" : ""}`}
        >
          {eyebrow}
        </motion.div>
      )}
      <motion.h2
        initial={{ opacity: 0, y: 12 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-60px" }}
        transition={{ duration: 0.65 }}
        className={`font-display text-4xl md:text-5xl lg:text-[3.4rem] font-semibold tracking-tight leading-[1.02] ${textColor}`}
      >
        {title}{titleAccent && <> <span className="text-gradient-accent">{titleAccent}</span></>}
      </motion.h2>
      {sub && <p className={`mt-4 font-display text-xl ${textColor} opacity-80`}>{sub}</p>}
      {lead && <p className={`mt-5 text-lg leading-relaxed ${leadColor}`}>{lead}</p>}
    </div>
  );
}
