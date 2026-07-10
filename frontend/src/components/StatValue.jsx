import { useEffect, useRef, useState } from "react";

// Count-up animation on scroll into view. Preserves non-numeric parts (e.g., "₹", "+", "%", "→")
export default function StatValue({ value, className = "", duration = 1400 }) {
  const ref = useRef(null);
  const [display, setDisplay] = useState(value);
  const started = useRef(false);

  useEffect(() => {
    // extract first numeric run in value
    const m = String(value).match(/([\d,.]+)/);
    if (!m) { setDisplay(value); return; }
    const target = parseFloat(m[1].replace(/,/g, ""));
    if (isNaN(target)) { setDisplay(value); return; }
    const prefix = String(value).slice(0, m.index);
    const suffix = String(value).slice(m.index + m[1].length);

    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting && !started.current) {
          started.current = true;
          const start = performance.now();
          const step = (now) => {
            const p = Math.min(1, (now - start) / duration);
            const eased = 1 - Math.pow(1 - p, 3);
            const cur = target * eased;
            const decimals = m[1].includes(".") ? 1 : 0;
            const formatted = cur.toLocaleString(undefined, { maximumFractionDigits: decimals, minimumFractionDigits: decimals });
            setDisplay(`${prefix}${formatted}${suffix}`);
            if (p < 1) requestAnimationFrame(step);
          };
          requestAnimationFrame(step);
        }
      });
    }, { threshold: 0.3 });
    if (ref.current) io.observe(ref.current);
    return () => io.disconnect();
  }, [value, duration]);

  return <span ref={ref} className={`tabular-nums ${className}`}>{display}</span>;
}
