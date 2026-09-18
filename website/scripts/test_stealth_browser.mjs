// BROWSER_TEST_URL=http://127.0.0.1:4324/ PLAYWRIGHT_CHANNEL=chrome node scripts/test_stealth_browser.mjs
import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { isEphemeralProbe } from '../src/lib/modelMetadata.js';
for (const slug of ['union-alpha', 'ox-alpha-260821', 'ox-alpha-260825']) assert.equal(isEphemeralProbe(slug), true);
for (const slug of ['gpt-6-astra', 'glm-5-3-flash']) assert.equal(isEphemeralProbe(slug), false);
const browser = await chromium.launch({ headless: true, ...(process.env.PLAYWRIGHT_CHANNEL ? { channel: process.env.PLAYWRIGHT_CHANNEL } : {}) });
const url = process.env.BROWSER_TEST_URL || 'http://127.0.0.1:4324/';
try {
  for (const javaScriptEnabled of [false, true]) {
    const context = await browser.newContext({ javaScriptEnabled });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(url, { waitUntil: 'networkidle' });
    const union = page.locator('[data-model="union-alpha"]');
    assert.equal(await union.getAttribute('data-ephemeral'), 'true');
    assert.equal(await union.isVisible(), false);
    assert.equal(await page.locator('#includeEphemeral').isChecked(), false);
    assert.equal(await page.locator('[data-model="gpt-6-astra"]').isVisible(), true);
    const count = () => page.locator('.model-card:not(.hidden)').count();
    const initialCount = await count();
    assert.equal(await page.locator('#resultCount').innerText(), `${initialCount} shown`);
    if (javaScriptEnabled) {
      await page.locator('#includeEphemeral').check();
      assert.equal(await union.isVisible(), true);
      assert.equal(await count(), initialCount + 3);
      assert.equal(await page.locator('#resultCount').innerText(), `${initialCount + 3} shown`);
      await page.locator('#search').fill('union alpha');
      assert.equal(await count(), 1);
      await page.locator('#includeEphemeral').uncheck();
      assert.equal(await count(), 0);
      assert.equal(await page.locator('#emptyState').isVisible(), true);
      await page.locator('#includeEphemeral').check();
      await union.locator('a.card-link').click();
      await page.waitForLoadState('networkidle');
      assert.match(page.url(), /\/models\/union-alpha\//);
      assert.equal(await page.locator('h1').count(), 1);
    }
    assert.deepEqual(errors, []);
    await context.close();
  }
  console.log('PASS stealth defaults (with/without JS), opt-in, counts, search and retained detail page');
} finally { await browser.close(); }
