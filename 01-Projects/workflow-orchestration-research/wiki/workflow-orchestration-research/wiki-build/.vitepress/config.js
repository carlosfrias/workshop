import { defineConfig } from 'vitepress';

export default defineConfig({
  title: 'Workflow Orchestration Research',
  description: 'Research project evaluating workflow orchestration platforms for managing personal workload as projects',
  // Read markdown from the vault (documentation lives there)
  srcDir: '../../../../../personal-vault/01-Projects/workflow-orchestration-research/wiki/workflow-orchestration-research',
  outDir: './dist',
  cleanUrls: true,
  themeConfig: {
    nav: [
      { text: 'Home', link: '/Home' },
      { text: 'Research', link: '/research/Activity Log' },
      { text: 'Evaluation', link: '/evaluation/Activity Log' },
    ],
    sidebar: [
      {
        text: 'Domains',
        items: [
          { text: 'Research', link: '/research/Activity Log' },
          { text: 'Evaluation', link: '/evaluation/Activity Log' },
        ],
      },
      {
        text: 'Reference',
        items: [
          { text: 'Architecture', link: '/_meta/Architecture' },
          { text: 'Agent Definitions', link: '/_meta/Agent Definitions' },
          { text: 'Evaluation Dimensions', link: '/_meta/Evaluation Dimensions' },
          { text: 'Sample Prompts', link: '/_meta/Sample Prompts' },
          { text: 'Documentation Standard', link: '/_meta/Documentation Standard' },
        ],
      },
    ],
  },
});