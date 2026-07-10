import { useEffect } from "react";
import { useLocation } from "react-router-dom";

export default function ScrollToTop() {
  const { pathname, hash } = useLocation();
  useEffect(() => {
    if (hash) {
      requestAnimationFrame(() => {
        const el = document.querySelector(hash);
        if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
      });
      return;
    }
    window.scrollTo({ top: 0, behavior: "instant" });
  }, [pathname, hash]);

  // reset per-page accent when leaving product/solution page
  useEffect(() => {
    if (!/^\/(products|solutions)\//.test(pathname)) {
      document.documentElement.removeAttribute("data-accent");
      document.documentElement.style.removeProperty("--accent");
      document.documentElement.style.removeProperty("--accent-light");
      document.documentElement.style.removeProperty("--accent-grad");
    }
  }, [pathname]);
  return null;
}
