#!/usr/bin/env node
/**
 * Kingdom Warfare Full Content Downloader v6 — Final
 * Uses token-id auth + post detail's asset_urls for direct video downloads.
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const https = require('https');

const EMAIL = process.env.CLIENTCLUB_EMAIL;
const PASSWORD = process.env.CLIENTCLUB_PASSWORD;
if (!EMAIL || !PASSWORD) { console.error('ERROR: Set CLIENTCLUB_EMAIL and CLIENTCLUB_PASSWORD'); process.exit(1); }

const API = 'https://services.leadconnectorhq.com';
const LOC = 'hZTOH81bwS7gj6k0ZAMW';
const OUT = path.join(__dirname, '..', 'data', 'courses');

const slug = t => t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').substring(0, 60);
const sf = t => t.replace(/[/\\?%*:|"<>#]/g, '-').replace(/\s+/g, ' ').substring(0, 80);

function dl(url, dest) {
  return new Promise((resolve, reject) => {
    const f = fs.createWriteStream(dest);
    https.get(url, r => {
      if (r.statusCode >= 300 && r.statusCode < 400 && r.headers.location)
        return dl(r.headers.location, dest).then(resolve).catch(reject);
      r.pipe(f); f.on('finish', () => { f.close(); resolve(); });
    }).on('error', reject);
  });
}

(async () => {
  console.log('🚀 Downloader v6 — asset_urls direct\n');

  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  const req = ctx.request;
  let tokenId = null;

  page.on('request', r => {
    if (!tokenId && r.url().includes('leadconnector')) {
      const t = r.headers()['token-id'];
      if (t) tokenId = t;
    }
  });

  // ── Login ──────────────────────────────────────────────────────────
  console.log('📧 Logging in...');
  await page.goto('https://kingdomwarfare.app.clientclub.net/login', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(3000);
  await page.locator('input[placeholder*="email" i]').first().fill(EMAIL);
  await page.locator('input[type="password"]').first().fill(PASSWORD);
  await page.locator('button').filter({ hasText: /login/i }).first().click();
  await page.waitForTimeout(8000);
  await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {});
  await page.goto('https://kingdomwarfare.app.clientclub.net/courses/library-v2?courses=my', { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {});
  await page.waitForTimeout(5000);

  if (!tokenId) { console.log('❌ No token-id'); await browser.close(); return; }
  console.log('✅ Logged in\n');

  const H = { 'Accept': 'application/json', 'Version': '2021-07-28', 'token-id': tokenId, 'source': 'PORTAL_USER', 'channel': 'APP' };

  // ── Get products ───────────────────────────────────────────────────
  const products = await (await req.get(API + '/membership/locations/' + LOC + '/user-purchase/get-all-products?getPostCount=true', { headers: H })).json();
  console.log(`📚 ${products.length} products\n`);

  const kws = ['accelerated', 'governance', 'bloodline', '15 step', 'demonology'];
  const targets = [];
  for (const kw of kws) {
    const p = products.find(x => x.title.toLowerCase().includes(kw));
    if (p) targets.push(p);
  }
  console.log('🎯 Targets:');
  targets.forEach((p, i) => console.log(`  ${i+1}. ${p.title}`));
  console.log('');

  let totalV = 0, totalD = 0;
  const t0 = Date.now();

  // ── Process courses ────────────────────────────────────────────────
  for (let ci = 0; ci < targets.length; ci++) {
    const prod = targets[ci];
    const cs = slug(prod.title);
    console.log(`\n📖 ${ci+1}/${targets.length}: ${prod.title}`);
    console.log('═'.repeat(70));

    const cats = (await (await req.get(API + '/membership/locations/' + LOC + '/user-purchase/categories?product_id=' + prod.id, { headers: H })).json()).categories || [];
    if (!cats.length) { console.log('  ⚠️ No categories'); continue; }

    let cLessons = 0, cDl = 0;

    for (const cat of cats) {
      const ss = slug(cat.title);
      console.log(`\n  📂 ${cat.title}`);

      const postsR = await (await req.get(API + '/membership/locations/' + LOC + '/user-purchase/categories/' + cat.id + '?published_posts=true&product_id=' + prod.id, { headers: H })).json();
      let posts = postsR.category?.posts || [];
      if (!posts.length) { console.log('    (no posts)'); continue; }
      posts.sort((a, b) => (a.sequenceNo || 0) - (b.sequenceNo || 0));

      for (let pi = 0; pi < posts.length; pi++) {
        const post = posts[pi];
        const dir = path.join(OUT, cs, ss);
        fs.mkdirSync(dir, { recursive: true });
        const n = String(pi+1).padStart(2, '0');
        const nm = sf(post.title);
        const titleShort = post.title.substring(0, 65);
        cLessons++; totalV++;

        try {
          // Get full post detail
          const detail = await (await req.get(API + '/membership/locations/' + LOC + '/posts/' + post.id + '?source=communities', { headers: H })).json();
          const au = detail.asset_urls;

          if (!au?.url) {
            fs.writeFileSync(path.join(dir, `${n}-${nm}.md`), `# ${post.title}\n\n**Course:** ${prod.title}\n**Section:** ${cat.title}\n\n*No video asset.*\n`);
            console.log(`    📝 [${pi+1}/${posts.length}] ${titleShort}\n    ⚠️  No video`);
            continue;
          }

          const dur = au.meta?.durationInSeconds || 0;
          const mm = Math.floor(dur / 60);
          const ss2 = Math.floor(dur % 60);

          // Save metadata
          fs.writeFileSync(path.join(dir, `${n}-${nm}.md`),
            `# ${post.title}\n\n**Course:** ${prod.title}\n**Section:** ${cat.title}\n**Lesson ${pi+1}/${posts.length}**\n**Duration:** ${mm}m ${ss2}s\n\n` +
            `## 🎥 Video\n\n[${n}-${nm}.mp4](${n}-${nm}.mp4)\n\n` +
            `---\n*Downloaded: ${new Date().toISOString()}*\n`);

          // Download video
          const vp = path.join(dir, `${n}-${nm}.mp4`);
          if (fs.existsSync(vp)) {
            console.log(`    📝 [${pi+1}/${posts.length}] ${titleShort}\n    ✅ Cached (${mm}m ${ss2}s)`);
          } else {
            process.stdout.write(`    📝 [${pi+1}/${posts.length}] ${titleShort}\n    ⬇️  ${mm}m${ss2}s ...`);
            await dl(au.url, vp);
            console.log(` ✅ ${(fs.statSync(vp).size/1024/1024).toFixed(1)}MB`);
          }
          cDl++; totalD++;
        } catch (e) {
          console.log(`    📝 [${pi+1}/${posts.length}] ${titleShort}\n    ❌ ${e.message.substring(0, 80)}`);
        }
      }
    }
    console.log(`\n  📊 ${cDl}/${cLessons} videos`);
  }

  const mins = ((Date.now() - t0) / 1000 / 60).toFixed(1);
  await browser.close();
  console.log(`\n\n════════════════════════════════`);
  console.log(`  ✅ ${totalD}/${totalV} videos (${mins} min)`);
  console.log(`  📁 ${OUT}`);
  console.log(`════════════════════════════════\n`);
})().catch(e => { console.error('FATAL:', e.message); process.exit(1); });
