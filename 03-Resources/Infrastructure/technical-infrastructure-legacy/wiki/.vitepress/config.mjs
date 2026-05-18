import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(
  defineConfig({
    title: 'AI Trading Infrastructure Wiki',
    lang: 'en',
    themeConfig: {
      nav: [
        { text: 'Home', link: '/' },
        { text: 'Guides', link: '/guides/' },
        { text: 'Reference', link: '/reference/' },
        { text: 'Operational', link: '/operational/' },
        { text: 'Products', link: '/products/' },
        { text: 'Troubleshooting', link: '/troubleshooting/' },
        { text: 'Templates', link: '/templates/' }
      ],
      sidebar: {
        '/': [
          { text: 'Getting Started', link: '/getting-started/' },
          { text: 'Operational Docs', link: '/operational/operational-docs/' },
          { text: 'Guides', link: '/guides/' },
          { text: 'Reference', link: '/reference/' },
          { text: 'Products', link: '/products/' },
          { text: 'Troubleshooting', link: '/troubleshooting/' },
          { text: 'Templates', link: '/templates/' }
        ],
        '/guides/': [
          { text: 'Getting Started', link: '/guides/getting-started/' },
          { text: 'Ollama Setup', link: '/guides/ollama-setup/' },
          { text: 'GIST Message Protocol', link: '/guides/gist-message-protocol/' },
          { text: 'Tools', link: '/tools/' }
        ],
        '/reference/': [
          { text: 'Model Routing Guide', link: '/reference/model-routing-guide/' },
          { text: 'Decompose-Execute-Verify Pattern', link: '/reference/decompose-execute-verify-pattern/' },
          { text: 'Project Blueprint', link: '/products/project-blueprint/' }
        ],
        '/operational/': [
          { text: 'Status', link: '/operational/status/' },
          { text: 'Planning', link: '/operational/planning/' },
          { text: 'Sessions', link: '/operational/sessions/' },
          { text: 'Recommendations', link: '/operational/recommendations/' }
        ],
        '/products/': [
          { text: 'AgenticOS', link: '/products/agentic-os/' },
          { text: 'Transcript', link: '/products/agentic-os-transcript/' },
          { text: 'Project Blueprint', link: '/products/project-blueprint/' },
          { text: 'GIST Message Queue', link: '/products/gist-message-queue/' },
          { text: 'PI Keyword Router', link: '/products/pi-keyword-router/' }
        ],
        '/troubleshooting/': [
          { text: 'Network Troubleshooting', link: '/troubleshooting/network-troubleshooting-guide/' },
          { text: 'Offline Node Troubleshooting', link: '/troubleshooting/offline-node-troubleshooting/' }
        ],
        '/templates/': [
          { text: 'PLAN Template', link: '/templates/plan-template/' },
          { text: 'SESSION-NOTES Template', link: '/templates/session-notes-template/' }
        ]
      },
      search: {
        provider: 'local',
        options: {
          translations: {
            placeholder: 'Search docs...',
            noResults: 'No results found',
            searching: 'Searching...',
            results: '{total} results found',
            tags: 'Tags'
          }
        }
      }
    },
    mermaid: {
      // Mermaid configuration
      theme: 'default',
      securityLevel: 'loose',
      startOnLoad: true,
    }
  })
)
