import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '{project_name}',
  description: '{project_description}',

  // Source directory: parent directory (where markdown files live)
  srcDir: '.',
  srcExclude: ['**/wiki-build/**', '**/dist/**', '**/node_modules/**'],

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Reference', link: '/_meta/Architecture' },
    ],

    sidebar: [
      // Domains first — they are the wiki's primary content
      {
        text: '{domain1_name}',
        items: [
          { text: 'Activity Log', link: '/{domain1_name}/Activity Log' },
        ],
      },
      {
        text: '{domain2_name}',
        items: [
          { text: 'Activity Log', link: '/{domain2_name}/Activity Log' },
        ],
      },
      // Reference docs — reachable but non-central
      {
        text: 'Reference',
        collapsed: true,
        items: [
          { text: 'Architecture', link: '/_meta/Architecture' },
          { text: 'Agent Definitions', link: '/_meta/Agent Definitions' },
          { text: 'System & Context Files', link: '/_meta/System & Context Files' },
        ],
      },
      {
        text: 'Agents & Workflows',
        collapsed: true,
        items: [
          { text: 'Chain Files', link: '/_meta/Chain Files' },
          { text: 'Model Substitutions', link: '/_meta/Model Substitutions' },
          { text: 'Documentation Standard', link: '/_meta/Documentation Standard' },
        ],
      },
      {
        text: 'Using This Project',
        collapsed: true,
        items: [
          { text: 'Sample Prompts', link: '/_meta/Sample Prompts' },
        ],
      },
    ],

    search: {
      provider: 'local',
    },

    footer: {
      message: 'Built with Project Blueprint',
    },
  },
})