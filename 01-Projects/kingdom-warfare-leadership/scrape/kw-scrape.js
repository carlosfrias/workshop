#!/usr/bin/env node
/**
 * Kingdom Warfare Curriculum Scraper
 * 
 * Scrapes course library from ClientClub platform via Playwright.
 * 
 * Usage:
 *   CLIENTCLUB_EMAIL=... CLIENTCLUB_PASSWORD=... node kw-scrape.js
 * 
 * Output: Prints course structure to stdout. Pipe to data/ for storage.
 */

const { chromium } = require('playwright');

const EMAIL = process.env.CLIENTCLUB_EMAIL;
const PASSWORD = process.env.CLIENTCLUB_PASSWORD;

if (!EMAIL || !PASSWORD) {
  console.error('ERROR: Set CLIENTCLUB_EMAIL and CLIENTCLUB_PASSWORD environment variables');
  process.exit(1);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Login
  await page.goto('https://kingdomwarfare.app.clientclub.net/login', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(4000);
  await page.locator('input[placeholder*="email" i]').first().fill(EMAIL);
  await page.locator('input[type="password"]').first().fill(PASSWORD);
  await page.locator('button:has-text("Login")').first().click();
  await page.waitForTimeout(8000);
  await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {});

  // Go to library
  await page.goto('https://kingdomwarfare.app.clientclub.net/courses/library-v2?courses=my', { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(5000);

  // Get all course cards with progress info
  const courses = await page.evaluate(() => {
    const cards = [];
    document.querySelectorAll('h4').forEach(h => {
      const card = h.closest('[class*="card"], [class*="item"], [class*="row"], a');
      const parent = h.parentElement?.parentElement || h.parentElement;
      let progress = '';
      const progressEl = parent?.querySelector('[class*="progress"], [class*="percent"], [class*="complete"]');
      if (progressEl) progress = progressEl.textContent.trim();
      
      const allText = parent?.textContent || '';
      const pctMatch = allText.match(/(\d+%)/);
      if (pctMatch) progress = pctMatch[1];

      cards.push({
        title: h.textContent.trim(),
        progress,
        fullText: parent?.textContent?.trim()?.substring(0, 300) || ''
      });
    });
    return cards;
  });

  console.log('=== ALL COURSES ===');
  console.log(JSON.stringify(courses, null, 2));

  // Click into each course to see module/lesson structure
  console.log('\n=== DRILLING INTO COURSES ===');
  
  for (let i = 0; i < Math.min(courses.length, 17); i++) {
    const course = courses[i];
    console.log(`\n--- Course ${i+1}: ${course.title} ---`);
    
    try {
      const heading = page.locator('h4').filter({ hasText: course.title.substring(0, 30) }).first();
      if (await heading.count() === 0) {
        console.log('  Could not find heading');
        continue;
      }
      
      const parentAnchor = heading.locator('..');
      await heading.click({ timeout: 5000 }).catch(async () => {
        await parentAnchor.click({ timeout: 5000 }).catch(() => {
          console.log('  Could not click');
        });
      });
      
      await page.waitForTimeout(4000);
      
      const details = await page.evaluate(() => {
        const modules = [];
        const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6, [class*="module"], [class*="lesson"], [class*="section"], [class*="chapter"]'));
        headings.forEach(el => {
          const text = el.textContent.trim();
          if (text.length > 3 && text.length < 200) {
            modules.push(text);
          }
        });
        
        const accordions = Array.from(document.querySelectorAll('[class*="accordion"], [class*="collapse"], [class*="expand"], summary'));
        accordions.forEach(el => {
          const text = el.textContent.trim();
          if (text.length > 3 && text.length < 200) {
            modules.push('[SECTION] ' + text);
          }
        });
        
        return {
          title: document.querySelector('h1')?.textContent?.trim() || '',
          modules: modules.slice(0, 40),
          bodyText: document.body.innerText.substring(0, 2000)
        };
      });
      
      console.log('  Title:', details.title);
      console.log('  Modules:', JSON.stringify(details.modules.slice(0, 20), null, 2));
      console.log('  Body:', details.bodyText.substring(0, 500));
      
      // Go back to library
      await page.goto('https://kingdomwarfare.app.clientclub.net/courses/library-v2?courses=my', { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
      await page.waitForTimeout(4000);
      
    } catch(e) {
      console.log('  Error:', e.message);
      await page.goto('https://kingdomwarfare.app.clientclub.net/courses/library-v2?courses=my', { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
      await page.waitForTimeout(4000);
    }
  }

  await browser.close();
  console.log('\nDONE');
})().catch(e => {
  console.error('ERROR:', e.message);
  process.exit(1);
});
