import { GITHUB_URL, DISCORD_URL, X_URL, LINKEDIN_URL } from "@/lib/constants";

// Simple inline SVG brand icons. Off-white by default, teal on hover.
// Icon-only links are aria-labeled for accessibility.

const iconClass =
  "h-5 w-5 text-gray-bright transition-colors duration-150 hover:text-teal";

type IconProps = React.SVGProps<SVGSVGElement>;

function GitHubIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" {...props}>
      <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.55 0-.27-.01-1.17-.02-2.13-3.2.7-3.87-1.36-3.87-1.36-.52-1.33-1.28-1.68-1.28-1.68-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.03 1.76 2.69 1.25 3.35.96.1-.75.4-1.25.72-1.54-2.55-.29-5.24-1.28-5.24-5.68 0-1.26.45-2.28 1.18-3.09-.12-.29-.51-1.46.11-3.05 0 0 .96-.31 3.15 1.18a10.9 10.9 0 0 1 5.74 0c2.19-1.49 3.15-1.18 3.15-1.18.62 1.59.23 2.76.11 3.05.74.81 1.18 1.83 1.18 3.09 0 4.41-2.69 5.38-5.25 5.67.41.35.77 1.05.77 2.12 0 1.53-.01 2.76-.01 3.14 0 .3.2.66.8.55A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5Z" />
    </svg>
  );
}

function XIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" {...props}>
      <path d="M18.24 2.25h3.31l-7.23 8.26 8.5 11.24h-6.66l-5.21-6.82L5 21.75H1.68l7.73-8.84L1.25 2.25h6.83l4.71 6.23 5.45-6.23Zm-1.16 17.52h1.83L7.08 4.13H5.12l11.96 15.64Z" />
    </svg>
  );
}

function LinkedInIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" {...props}>
      <path d="M20.45 20.45h-3.55v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.36V9h3.41v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28ZM5.34 7.43a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12Zm1.78 13.02H3.56V9h3.56v11.45Z" />
    </svg>
  );
}

function DiscordIcon(props: IconProps) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" {...props}>
      <path d="M20.32 4.37a19.8 19.8 0 0 0-4.93-1.51 13.76 13.76 0 0 0-.64 1.28 18.27 18.27 0 0 0-5.5 0 13.76 13.76 0 0 0-.64-1.28c-1.72.3-3.37.8-4.93 1.51C.53 9.5-.32 14.5.09 19.44c2.06 1.5 4.05 2.42 6.01 3.02.49-.66.93-1.36 1.03-2.32-.55-.21-1.08-.46-1.58-.77.13-.09.26-.19.38-.29 2.69 1.25 5.62 1.25 8.25 0 .13.11.26.2.38.29-.5.31-1.03.56-1.58.77.1.97.52 1.67 1.03 2.32 1.96-.6 3.96-1.52 6.01-3.02.49-5.66-.84-10.66-3.23-15.07ZM8.02 16.44c-1.2 0-2.19-1.08-2.19-2.42 0-1.34.97-2.43 2.19-2.43s2.21 1.09 2.19 2.43c0 1.34-.98 2.42-2.19 2.42Zm7.96 0c-1.2 0-2.19-1.08-2.19-2.42 0-1.34.97-2.43 2.19-2.43s2.21 1.09 2.19 2.43c0 1.34-.97 2.42-2.19 2.42Z" />
    </svg>
  );
}

const socials = [
  { label: "GitHub", href: GITHUB_URL, Icon: GitHubIcon },
  { label: "X (Twitter)", href: X_URL, Icon: XIcon },
  { label: "LinkedIn", href: LINKEDIN_URL, Icon: LinkedInIcon },
  { label: "Discord", href: DISCORD_URL, Icon: DiscordIcon },
];

export function SocialLinks({ className = "" }: { className?: string }) {
  return (
    <div className={`flex items-center gap-5 ${className}`}>
      {socials.map(({ label, href, Icon }) => (
        <a
          key={label}
          href={href}
          target="_blank"
          rel="noreferrer"
          aria-label={label}
          className="inline-flex"
        >
          <Icon className={iconClass} />
        </a>
      ))}
    </div>
  );
}