import { defineConfig } from 'vitepress'
import { readdirSync, statSync } from 'fs'
import { join, dirname, basename } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const WIKI_BASE = join(__dirname, '..', '..', 'wiki')

/**
 * Title case conversion
 */
function titleCase(str) {
  return str
    .split(' ')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

/**
 * Recursively generate sidebar items from a directory.
 * Returns items array or null if dir is empty.
 */
function generateDirSidebar(dirPath, urlPrefix) {
  let items = []
  try {
    const entries = readdirSync(dirPath, { withFileTypes: true })

    const files = entries
      .filter(e => e.isFile() && e.name.endsWith('.md') && e.name !== 'index.md')
      .map(e => e.name)
      .sort((a, b) => a.localeCompare(b))

    const dirs = entries
      .filter(e => e.isDirectory())
      .map(e => e.name)
      .sort((a, b) => a.localeCompare(b))

    for (const f of files) {
      const name = f.replace(/\.md$/, '')
      const link = urlPrefix ? `${urlPrefix}/${name}` : `/${name}`
      items.push({
        text: titleCase(name.replace(/-/g, ' ').replace(/_/g, ' ')),
        link
      })
    }

    for (const d of dirs) {
      const subPath = join(dirPath, d)
      const subPrefix = urlPrefix ? `${urlPrefix}/${d}` : `/${d}`
      const subItems = generateDirSidebar(subPath, subPrefix)
      if (subItems && subItems.length > 0) {
        items.push({
          text: titleCase(d.replace(/-/g, ' ').replace(/_/g, ' ')),
          collapsed: true,
          items: subItems
        })
      }
    }
  } catch {
    return null
  }
  return items.length > 0 ? items : null
}

/**
 * Generate top-level sidebar sections from the wiki root.
 */
function generateWikiSidebar() {
  const sections = []
  try {
    const entries = readdirSync(WIKI_BASE, { withFileTypes: true })
    const dirs = entries
      .filter(e => e.isDirectory())
      .map(e => e.name)
      .sort((a, b) => a.localeCompare(b))

    // Explicit section ordering
    const sectionOrder = [
      'guides',
      'reference',
      'products',
      'troubleshooting',
      'operational',
      'tools',
      'templates',
      'decomposition-examples',
      'local-model-pilot'
    ]

    const orderedDirs = []
    for (const d of sectionOrder) {
      if (dirs.includes(d)) orderedDirs.push(d)
    }
    for (const d of dirs) {
      if (!sectionOrder.includes(d)) orderedDirs.push(d)
    }

    for (const d of orderedDirs) {
      const dirPath = join(WIKI_BASE, d)
      const items = generateDirSidebar(dirPath, `/${d}`)
      if (items && items.length > 0) {
        sections.push({
          text: titleCase(d.replace(/-/g, ' ')),
          collapsed: true,
          items
        })
      }
    }
  } catch (e) {
    console.error('Failed to generate sidebar:', e)
  }
  return sections
}

export default defineConfig({
  title: 'Technical Infrastructure Wiki',
  description: 'Extensions, skills, and agents for AI-orchestrated projects',

  srcDir: '../wiki',
  base: '/',
  cleanUrls: true,

  ignoreDeadLinks: true,

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guides', link: '/guides/quick-start' },
      { text: 'Reference', link: '/reference/model-routing-guide' },
      { text: 'Products', link: '/products/' },
      { text: 'Operational', link: '/operational/BACKLOG' },
      { text: 'GitHub', link: 'https://github.com/carlosfrias/trading-workspace' }
    ],

    sidebar: [
      {
        text: 'Home',
        items: [
          { text: 'Overview', link: '/' },
          { text: 'Navigation Hub', link: '/README' }
        ]
      },
      ...generateWikiSidebar()
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/carlosfrias/trading-workspace' }
    ],

    search: {
      provider: 'local'
    }
  },

  markdown: {
    lineNumbers: true
  }
})
