import React from "react";
import { DocsThemeConfig } from "nextra-theme-docs";

const SITE_URL = "https://hermes.dev"; // TODO: replace with actual URL
const GITHUB_URL = "https://github.com/ryomenhaider/Hermes";

const config: DocsThemeConfig = {
  logo: (
    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
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
  ),
  project: {
    link: GITHUB_URL,
  },
  docsRepository: `${GITHUB_URL}/edit/main/nextra-docs`,
  head: (
    <>
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <meta httpEquiv="Content-Language" content="en" />
      <meta name="description" content="Hermes: Data infrastructure for acquiring, processing, and serving structured data at scale." />
      <meta name="og:description" content="Hermes: Data infrastructure for acquiring, processing, and serving structured data at scale." />
      <meta name="og:title" content="Hermes Documentation" />
      <meta name="apple-mobile-web-app-title" content="Hermes" />
      <link rel="icon" href="/favicon.ico" />
    </>
  ),
  useNextSeoProps() {
    return {
      titleTemplate: "%s – Hermes",
    };
  },
  sidebar: {
    defaultMenuCollapseLevel: 1,
    toggleButton: true,
  },
  footer: {
    content: (
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
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
    ),
  },
  primaryHue: 168,
  primarySaturation: 40,
  color: {
    hue: { dark: 168, light: 168 },
    saturation: { dark: 40, light: 40 },
  },
  themeSwitch: {
    disabled: false,
    storageKey: "hermes-theme",
  },
  toc: {
    backToTop: true,
    title: "On This Page",
  },
  navigation: {
    prev: true,
    next: true,
  },
};

export default config;
