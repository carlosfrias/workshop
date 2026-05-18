const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const https = require('https');
const API = 'https://services.leadconnectorhq.com';
const LOC = 'hZTOH81bwS7gj6k0ZAMW';
const OUT = path.join(__dirname, '..', 'data', 'courses');
const slug = t => t.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').substring(0, 60);
const sf = t => t.replace(/[/\\?%*:|"<>#]/g, '-').replace(/\s+/g, ' ').substring(0, 80);
function dl(url, dest) {
  return new Promise((resolve, reject) => {
    const f = fs.createWriteStream(dest);
    https.get(url, r => { if(r.statusCode>=300&&r.statusCode<400&&r.headers.location) return dl(r.headers.location,dest).then(resolve).catch(reject); r.pipe(f); f.on('finish',()=>{f.close();resolve();}); }).on('error', reject);
  });
}
(async () => {
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  const req = ctx.request;
  let tokenId = null;
  page.on('request', r => { if (!tokenId && r.url().includes('leadconnector')) { const t = r.headers()['token-id']; if (t) tokenId = t; } });
  await page.goto('https://kingdomwarfare.app.clientclub.net/login', { waitUntil: 'networkidle', timeout: 30000 }); await page.waitForTimeout(3000);
  await page.locator('input[placeholder*="email" i]').first().fill(process.env.CLIENTCLUB_EMAIL);
  await page.locator('input[type="password"]').first().fill(process.env.CLIENTCLUB_PASSWORD);
  await page.locator('button').filter({ hasText: /login/i }).first().click(); await page.waitForTimeout(8000);
  await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {});
  await page.goto('https://kingdomwarfare.app.clientclub.net/courses/library-v2?courses=my', { waitUntil: 'networkidle', timeout: 30000 }).catch(() => {}); await page.waitForTimeout(5000);
  if (!tokenId) { console.log('No token'); await browser.close(); return; }
  const H = { 'Accept': 'application/json', 'Version': '2021-07-28', 'token-id': tokenId, 'source': 'PORTAL_USER', 'channel': 'APP' };
  const products = await (await req.get(API+'/membership/locations/'+LOC+'/user-purchase/get-all-products?getPostCount=true',{headers:H})).json();
  
  const targets = [
    products.find(p => p.title.toLowerCase().includes('acceller')) || products.find(p => p.title.toLowerCase().includes('start here')),
    products.find(p => p.title.toLowerCase().includes('advanced demonology'))
  ].filter(Boolean);

  let totalDl = 0;
  for (const prod of targets) {
    const cs = slug(prod.title);
    console.log('\n'+prod.title);
    const cats = (await (await req.get(API+'/membership/locations/'+LOC+'/user-purchase/categories?product_id='+prod.id,{headers:H})).json()).categories || [];
    for (const cat of cats) {
      const ss = slug(cat.title);
      const postsR = await (await req.get(API+'/membership/locations/'+LOC+'/user-purchase/categories/'+cat.id+'?published_posts=true&product_id='+prod.id,{headers:H})).json();
      let posts = postsR.category?.posts || [];
      if (!posts.length) continue;
      posts.sort((a,b)=>(a.sequenceNo||0)-(b.sequenceNo||0));
      for (let pi=0; pi<posts.length; pi++) {
        const post = posts[pi]; const dir = path.join(OUT,cs,ss); fs.mkdirSync(dir,{recursive:true});
        const n = String(pi+1).padStart(2,'0'); const nm = sf(post.title); const vp = path.join(dir,n+'-'+nm+'.mp4');
        if (fs.existsSync(vp)) { console.log('  ✅ '+post.title.substring(0,60)); continue; }
        try {
          const detail = await (await req.get(API+'/membership/locations/'+LOC+'/posts/'+post.id+'?source=communities',{headers:H})).json();
          const au = detail.asset_urls;
          if (!au?.url) { fs.writeFileSync(path.join(dir,n+'-'+nm+'.md'),'# '+post.title+'\n\n*No video.*\n'); console.log('  ⚠️ No video: '+post.title.substring(0,50)); continue; }
          const dur = au.meta?.durationInSeconds||0, mm = Math.floor(dur/60), ss2 = Math.floor(dur%60);
          fs.writeFileSync(path.join(dir,n+'-'+nm+'.md'),'# '+post.title+'\n\n**Course:** '+prod.title+'\n**Section:** '+cat.title+'\n**Duration:** '+mm+'m '+ss2+'s\n\n## 🎥 Video\n\n['+n+'-'+nm+'.mp4]('+n+'-'+nm+'.mp4)\n');
          process.stdout.write('  ⬇️ '+mm+'m'+ss2+'s ...'); await dl(au.url, vp);
          console.log(' ✅ '+(fs.statSync(vp).size/1024/1024).toFixed(1)+'MB: '+post.title.substring(0,50));
          totalDl++;
        } catch(e) { console.log('  ❌ '+e.message.substring(0,60)); }
      }
    }
  }
  console.log('\n✅ '+totalDl+' videos downloaded');
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
