import Hero from "@/sections/Hero";
import Challenges from "@/sections/Challenges";
import Positioning from "@/sections/Positioning";
import Stack from "@/sections/Stack";
import ProductsGrid from "@/sections/ProductsGrid";
import ServicesRow from "@/sections/ServicesRow";
import IndustryOS from "@/sections/IndustryOS";
import Results from "@/sections/Results";
import Fueling from "@/sections/Fueling";
import Why from "@/sections/Why";
import ClosingCTA from "@/sections/ClosingCTA";

export default function Home() {
  return (
    <div data-testid="home-page">
      <Hero />
      <Challenges />
      <Positioning />
      <Stack />
      <ProductsGrid />
      <ServicesRow />
      <IndustryOS />
      <Results />
      <Fueling />
      <Why />
      <ClosingCTA />
    </div>
  );
}
