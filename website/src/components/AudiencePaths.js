import Link from '@docusaurus/Link';

const paths = [
  {
    title: 'Building an Agent',
    desc: 'Create a TACO-compatible agent in 5 minutes. Define your trade, declare schemas, and start serving.',
    link: '/docs/getting-started/build-agent',
    icon: (
      <svg viewBox="0 0 24 24">
        <path d="M12 2L2 7l10 5 10-5-10-5z" />
        <path d="M2 17l10 5 10-5" />
        <path d="M2 12l10 5 10-5" />
      </svg>
    ),
  },
  {
    title: 'Integrating a Platform',
    desc: 'Add an agent sidecar to your existing construction platform. Map your capabilities to TACO task types.',
    link: '/docs/getting-started/integrate-platform',
    icon: (
      <svg viewBox="0 0 24 24">
        <rect x="2" y="3" width="20" height="14" rx="2" />
        <line x1="8" y1="21" x2="16" y2="21" />
        <line x1="12" y1="17" x2="12" y2="21" />
      </svg>
    ),
  },
  {
    title: 'Contributing',
    desc: 'Help define new task types, schemas, and the future of construction agent interoperability.',
    link: 'https://github.com/pelles-ai/taco/blob/main/CONTRIBUTING.md',
    icon: (
      <svg viewBox="0 0 24 24">
        <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 00-3-3.87" />
        <path d="M16 3.13a4 4 0 010 7.75" />
      </svg>
    ),
  },
];

export default function AudiencePaths() {
  return (
    <div className="audience-paths">
      {paths.map((p) => {
        const isExternal = p.link.startsWith('http');
        const Component = isExternal ? 'a' : Link;
        const props = isExternal
          ? {href: p.link, target: '_blank', rel: 'noopener noreferrer'}
          : {to: p.link};
        return (
          <Component className="audience-card" key={p.title} {...props}>
            <div className="audience-card__icon">{p.icon}</div>
            <div className="audience-card__title">{p.title}</div>
            <div className="audience-card__desc">{p.desc}</div>
            <div className="audience-card__link">Learn more &rarr;</div>
          </Component>
        );
      })}
    </div>
  );
}
