import { StatusBar } from "@/components/StatusBar";
import { Header } from "@/components/Header";
import { Hero } from "@/components/Hero";
import { Ticker } from "@/components/Ticker";
import { Metrics } from "@/components/Metrics";
import { HowItWorks } from "@/components/HowItWorks";
import { Features } from "@/components/Features";
import { CodeTabs } from "@/components/CodeTabs";
import { DocsPreview } from "@/components/DocsPreview";
import { Footer } from "@/components/Footer";

export default function Home() {
  return (
    <>
      <StatusBar />
      <Header />
      <main id="main-content">
        <Hero />
        <Ticker />
        <Metrics />
        <HowItWorks />
        <Features />
        <CodeTabs />
        <DocsPreview />
      </main>
      <Footer />
    </>
  );
}
