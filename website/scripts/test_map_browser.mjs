// Run against an Astro preview or the deployed page:
// MAP_TEST_URL=http://127.0.0.1:4323/map/ PLAYWRIGHT_CHANNEL=chrome npm run test:map:browser
// Otherwise install Playwright's bundled Chromium with `npx playwright install chromium`.
import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const url = process.env.MAP_TEST_URL || 'http://127.0.0.1:4323/map/';
const browser = await chromium.launch({ headless: true, ...(process.env.PLAYWRIGHT_CHANNEL ? { channel: process.env.PLAYWRIGHT_CHANNEL } : {}) });
const errors = [];
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
page.on('pageerror', e => { errors.push(e.message); console.error(e.stack); });
const wait = () => page.waitForTimeout(250);
const camera = () => page.evaluate(() => JSON.parse(JSON.stringify(document.getElementById('plot')._fullLayout.scene.camera)));
const equalCamera = (a, b) => {
  for (const part of ['eye', 'up', 'center']) for (const axis of ['x', 'y', 'z'])
    assert.ok(Math.abs(a[part][axis] - b[part][axis]) < 1e-6, `camera ${part}.${axis} changed`);
  assert.deepEqual(a.projection, b.projection);
};

try {
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.waitForFunction(() => document.getElementById('plot')?._fullLayout);
  assert.match(await page.locator('#keep').innerText(), /average/);
  assert.equal(await page.getByRole('heading', { name: 'Similarity tree', exact: true }).count(), 1);
  console.log('PASS initial render and honest labels');

  // Real pointer rotation includes camera.up; programmatic eye-only tests missed the old bug.
  await page.locator('#plot').scrollIntoViewIfNeeded();
  const bounds = await page.locator('#plot').boundingBox();
  await page.mouse.move(bounds.x + bounds.width * 0.6, bounds.y + bounds.height * 0.45);
  await page.mouse.down();
  await page.mouse.move(bounds.x + bounds.width * 0.72, bounds.y + bounds.height * 0.56, { steps: 20 });
  await page.mouse.up(); await wait();
  const rotated = await camera();
  assert.ok(Math.abs(rotated.up.x) + Math.abs(rotated.up.y) > 0.01, 'test must actually rotate camera.up');
  await page.locator('#traj').check(); await wait(); equalCamera(rotated, await camera());
  await page.locator('#pathgroup').selectOption('family'); await wait(); equalCamera(rotated, await camera());
  await page.locator('#labs input[data-lab="OpenAI"]').uncheck(); await wait(); equalCamera(rotated, await camera());
  await page.locator('#labs input[data-lab="OpenAI"]').check(); await wait();
  console.log('PASS complete camera retained across overlays, grouping and lab filters');

  for (const method of ['Umap', 'Mds', 'Pca']) {
    await page.locator(`#m${method}`).click();
    for (const dimensions of [3, 2]) {
      await page.locator(`#dim${dimensions}`).click(); await wait();
      const scales = await page.evaluate(dimensions => {
        const l = document.getElementById('plot')._fullLayout;
        if (dimensions === 2) return [Math.abs(l.xaxis._m), Math.abs(l.yaxis._m)];
        return ['x', 'y', 'z'].map(axis => l.scene.aspectratio[axis] / (l.scene[`${axis}axis`].range[1] - l.scene[`${axis}axis`].range[0]));
      }, dimensions);
      assert.ok(Math.max(...scales) / Math.min(...scales) < 1 + 1e-7, `${method}${dimensions}: unequal units ${scales}`);
    }
  }
  await page.locator('#mUmap').click(); await page.locator('#dim3').click(); await wait();
  equalCamera(rotated, await camera());
  console.log('PASS six projection modes preserve axis units; returning restores camera');

  await page.locator('#q').fill('union'); await wait();
  let card = await page.locator('#card').innerText();
  assert.match(card, /Union Alpha/); assert.match(card, /125 responses/); assert.match(card, /1 collection cell/);
  assert.match(card, /[0-3]\/3 original top-three/); assert.match(card, /gpt-6-astra/);
  await page.locator('#labs input[data-lab="Unknown"]').uncheck(); await wait();
  assert.match(await page.locator('#card').innerText(), /Hidden by current filters/);
  await page.locator('#card [data-reveal]').click(); await wait();
  assert.ok(await page.locator('#labs input[data-lab="Unknown"]').isChecked());
  assert.doesNotMatch(await page.locator('#card').innerText(), /Hidden by current filters/);
  await page.evaluate(() => { const d = document.getElementById('date'); d.value = 0; d.dispatchEvent(new Event('input', { bubbles: true })); }); await wait();
  assert.match(await page.locator('#card').innerText(), /Hidden by current filters/);
  await page.locator('#card [data-reveal]').click(); await wait();
  assert.doesNotMatch(await page.locator('#card').innerText(), /Hidden by current filters/);
  await page.locator('#card .sample-scope summary').click();
  assert.match(await page.locator('#card .sample-scope').innerText(), /Capture dates unavailable/);
  assert.match(await page.locator('#card .sample-scope').innerText(), /SHORT: 25/);
  await page.locator('#card [data-model="gpt-6-astra"]').click(); await wait();
  assert.match(await page.locator('#card h2').innerText(), /gpt-6-astra/);
  await page.locator('#q').fill('no-such-model-zzzz'); await wait();
  assert.match(await page.locator('#card').innerText(), /No matching models/);
  console.log('PASS per-model fidelity, sample provenance, hidden selections and reveal');

  const leaf = page.locator('#dendro .leaf[aria-label="Show Union Alpha on the map"]');
  await leaf.focus(); await leaf.press('Enter'); await wait();
  assert.match(await page.locator('#card h2').innerText(), /Union Alpha/);
  console.log('PASS keyboard activation of similarity-tree leaves');

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 } });
  mobile.on('pageerror', e => { errors.push(e.message); console.error(e.stack); });
  await mobile.goto(url, { waitUntil: 'networkidle' });
  await mobile.waitForFunction(() => document.getElementById('plot')?._fullLayout);
  const geometry = await mobile.evaluate(() => ({
    advancedOpen: document.getElementById('advanced').open,
    top: document.getElementById('plot').getBoundingClientRect().top,
    overflow: document.documentElement.scrollWidth > innerWidth,
  }));
  assert.equal(geometry.advancedOpen, false);
  assert.equal(geometry.overflow, false);
  assert.ok(geometry.top < 844, `mobile map starts below first viewport: ${geometry.top}`);
  await mobile.locator('#advanced summary').first().click();
  assert.equal(await mobile.locator('#advanced').evaluate(el => el.open), true);
  console.log('PASS mobile controls collapse and map starts in first viewport', geometry);
  assert.deepEqual(errors, []);
  console.log(`PASS map browser regression suite: ${url}`);
} finally {
  await browser.close();
}
