// @ts-check

import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'TACO',
  tagline: 'The A2A Construction Open-standard',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://taco-protocol.com',
  baseUrl: '/',

  organizationName: 'pelles-ai',
  projectName: 'taco',

  onBrokenLinks: 'throw',

  headTags: [
    {
      tagName: 'link',
      attributes: {
        rel: 'preconnect',
        href: 'https://fonts.googleapis.com',
      },
    },
    {
      tagName: 'link',
      attributes: {
        rel: 'preconnect',
        href: 'https://fonts.gstatic.com',
        crossorigin: 'anonymous',
      },
    },
    {
      tagName: 'link',
      attributes: {
        rel: 'stylesheet',
        href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap',
      },
    },
  ],

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl: 'https://github.com/pelles-ai/taco/tree/main/website/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/taco-social-card.png',
      colorMode: {
        respectPrefersColorScheme: true,
      },
      navbar: {
        title: 'TACO',
        logo: {
          alt: 'TACO Logo',
          src: 'img/taco_logo.png',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'docsSidebar',
            position: 'left',
            label: 'Docs',
          },
          {
            href: 'https://github.com/pelles-ai/taco/tree/main/spec',
            label: 'Spec',
            position: 'left',
          },
          {
            href: 'https://github.com/pelles-ai/taco',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Documentation',
            items: [
              {
                label: 'Introduction',
                to: '/docs/intro',
              },
              {
                label: 'Task Types',
                to: '/docs/task-types',
              },
              {
                label: 'Data Schemas',
                to: '/docs/schemas/',
              },
            ],
          },
          {
            title: 'Community',
            items: [
              {
                label: 'GitHub Discussions',
                href: 'https://github.com/pelles-ai/taco/discussions',
              },
              {
                label: 'Issues',
                href: 'https://github.com/pelles-ai/taco/issues',
              },
              {
                label: 'Contributing',
                href: 'https://github.com/pelles-ai/taco/blob/main/CONTRIBUTING.md',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/pelles-ai/taco',
              },
              {
                label: 'A2A Protocol',
                href: 'https://a2a-protocol.org',
              },
              {
                label: 'Pelles',
                href: 'https://pelles.ai',
              },
            ],
          },
        ],
        copyright: `Initiated by Pelles. Built on the A2A protocol (Linux Foundation). Apache 2.0.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['bash', 'json'],
      },
    }),
};

export default config;
