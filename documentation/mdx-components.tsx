import { useMDXComponents as getThemeComponents } from "nextra-theme-docs";
import { Banner, Callout, Cards, FileTree, Steps, Tabs } from "nextra/components";

const themeComponents = getThemeComponents();
const builtIns = { Banner, Callout, Cards, FileTree, Steps, Tabs };

// Merge the theme's defaults, Nextra's built-in components, and any overrides.
export function useMDXComponents(components?: Record<string, React.ComponentType<any>>) {
  return { ...themeComponents, ...builtIns, ...(components ?? {}) };
}