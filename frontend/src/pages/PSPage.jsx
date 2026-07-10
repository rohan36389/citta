import { useEffect } from "react";
import { useParams, Navigate } from "react-router-dom";
import { PAGE_CONFIGS, ACCENT } from "@/data/content";
import {
  PSHero, PSStakeholders, PSCapabilities, PSBestOutcomes, PSWhyGrid, PSClosing,
} from "@/components/PSSections";

function useAccentTheme(cfg) {
  useEffect(() => {
    if (!cfg) return undefined;
    const a = ACCENT[cfg.accent] || ACCENT.blue;
    const root = document.documentElement;
    root.setAttribute("data-accent", cfg.accent);
    root.style.setProperty("--accent", a.hex);
    root.style.setProperty("--accent-light", a.light);
    root.style.setProperty("--accent-grad", a.grad);
    return () => {
      root.removeAttribute("data-accent");
      root.style.removeProperty("--accent");
      root.style.removeProperty("--accent-light");
      root.style.removeProperty("--accent-grad");
    };
  }, [cfg]);
}

export default function PSPage({ kind }) {
  const { slug } = useParams();
  const cfg = PAGE_CONFIGS[slug];
  useAccentTheme(cfg);

  if (!cfg) return <Navigate to="/" replace />;
  if (kind && cfg.kind !== kind) return <Navigate to={`/${cfg.kind}s/${cfg.slug}`} replace />;

  const backTo = cfg.kind === "product" ? "/#products" : "/#solutions";
  const backLabel = cfg.kind === "product" ? "Back to products" : "Back to solutions";

  return (
    <div data-testid={`${cfg.kind}-page`} data-slug={cfg.slug}>
      <PSHero cfg={cfg} backTo={backTo} backLabel={backLabel} />
      {cfg.stakeholders && <PSStakeholders stakeholders={cfg.stakeholders} />}
      <PSCapabilities cfg={cfg} />
      {cfg.bestFor && <PSBestOutcomes bestFor={cfg.bestFor} outcomes={cfg.outcomes} />}
      {cfg.whyGrid && <PSWhyGrid cfg={cfg} />}
      <PSClosing cfg={cfg} />
    </div>
  );
}
