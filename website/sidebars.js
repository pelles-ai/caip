// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  docsSidebar: [
    'intro',
    'task-types',
    'agent-card-extensions',
    {
      type: 'category',
      label: 'Data Schemas',
      link: {
        type: 'doc',
        id: 'schemas/index',
      },
      items: [
        'schemas/bom-v1',
        'schemas/rfi-v1',
        'schemas/estimate-v1',
        'schemas/schedule-v1',
        'schemas/quote-v1',
        'schemas/change-order-v1',
      ],
    },
    'sdk',
    'security',
  ],
};

export default sidebars;
