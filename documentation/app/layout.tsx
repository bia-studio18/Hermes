import type { Metadata } from "next";
import { Footer, Layout, Navbar } from "nextra-theme-docs";
import { GitHubIcon } from "nextra/icons";
import { Head } from "nextra/components";
import { getPageMap } from "nextra/page-map";
import "nextra-theme-docs/style.css";
import "./style.css";

export const metadata: Metadata = {
  title: {
    default: "Hermes Documentation",
    template: "%s – Hermes",
  },
  description:
    "Hermes: Data infrastructure for acquiring, processing, and serving structured data at scale.",
  metadataBase: new URL("https://docs.hermes-plt.xyz"), // TODO: replace with actual site URL
};

// TODO: replace with the actual landing-page URL
const SITE_URL = "https://hermes-plt.xyz";
const GITHUB_URL = "https://github.com/ryomenhaider/Hermes";

function HermesLogo() {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path d="M4 4L12 20L20 4" stroke="#F5F5F2" strokeWidth="3" strokeLinecap="square" />
        <path d="M8 12H16" stroke="#2F6F68" strokeWidth="3" strokeLinecap="square" />
      </svg>
      <span
        style={{
          fontWeight: 700,
          fontSize: "1rem",
          letterSpacing: "0.08em",
          color: "#F5F5F2",
        }}
      >
        HERMES
      </span>
    </div>
  );
}

const navbar = (
  <Navbar
    logo={<HermesLogo />}
    logoLink={SITE_URL}
    projectLink={GITHUB_URL}
    projectIcon={<GitHubIcon height="20" />}
  >
    <span
      style={{
        fontSize: "0.875rem",
        fontWeight: 500,
        color: "#8B9198",
        textDecoration: "none",
        marginRight: "0.5rem",
      }}
    >
      Docs
    </span>
  </Navbar>
);

const footer = (
  <Footer>
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        width: "100%",
        borderTop: "1px solid #1C262B",
        paddingTop: "1.5rem",
        fontSize: "0.75rem",
        color: "#8B9198",
      }}
    >
      <span>Elastic License 2.0</span>
      <span>
        <a
          href={GITHUB_URL}
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: "#8B9198", textDecoration: "none" }}
        >
          GitHub
        </a>
      </span>
    </div>
  </Footer>
);

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" dir="ltr" suppressHydrationWarning>
      <Head
        color={{ hue: 168, saturation: 40, lightness: { dark: 55, light: 45 } }}
        backgroundColor={{ dark: "#0B0D0F", light: "#F5F5F2" }}
      >
        <meta httpEquiv="Content-Language" content="en" />
        <meta name="og:description" content="Hermes: Data infrastructure for the modern world." />
        <meta name="og:title" content="Hermes Documentation" />
        <meta name="apple-mobile-web-app-title" content="Hermes" />
      </Head>
      <body>
        <Layout
          pageMap={await getPageMap()}
          navbar={navbar}
          footer={footer}
          docsRepositoryBase={`${GITHUB_URL}/edit/main/documentation/content`}
          sidebar={{
            defaultMenuCollapseLevel: 1,
            toggleButton: true,
            autoCollapse: true,
          }}
          navigation={{ prev: true, next: true }}
          toc={{ backToTop: "Scroll to top", title: "On This Page", float: true }}
          themeSwitch={{ dark: "Dark", light: "Light", system: "System" }}
          nextThemes={{
            attribute: "class",
            defaultTheme: "dark",
            disableTransitionOnChange: true,
            storageKey: "hermes-theme",
          }}
          editLink="Edit this page"
        >
          {children}
        </Layout>
      </body>
    </html>
  );
}