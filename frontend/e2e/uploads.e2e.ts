// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// Upload limits, in a browser.
//
// `src/lib/editor/upload_limits.test.ts` reads the source and checks the browser's
// fallbacks are no looser than config.py's. That cannot see whether Uppy is actually
// applying them, which is the thing that was broken: `restrictions` is an Uppy Core
// option and was being passed to the Dashboard plugin, where it does nothing, so the
// picker had no size cap and no type filter at all. Only a real file in a real picker
// shows that.
//
// The server side is covered by TestStorage in frogquiz/tests/test_server.py.

import { expect, test } from '@playwright/test';
import { mc, saveQuiz, rememberAnonQuiz } from './helpers';

/** The ceiling the server publishes, so this spec does not hardcode a second copy. */
async function serverLimit(request): Promise<number> {
	const res = await request.get('/api/v1/storage/limits');
	expect(res.status()).toBe(200);
	return (await res.json()).max_file_size as number;
}

/** Opens a saved quiz's editor with its first question's media picker showing. */
async function openPicker(page, request) {
	const saved = await saveQuiz(request, {
		title: 'Uploads',
		description: 'one question',
		questions: [
			mc('Pick one?', [
				['A', true],
				['B', false]
			])
		]
	});
	await rememberAnonQuiz(page, saved.body.id, saved.secret!);
	await page.goto(`/edit?quiz_id=${saved.body.id}`);
	await expect(page.locator('[data-question-card]')).toHaveCount(1);
	// The one card opens focused, with the uploader's trigger inside it.
	const addMedia = page.getByRole('button', { name: /Add Media/ }).first();
	await expect(addMedia).toBeVisible();
	await addMedia.click();
	// Only Image is enabled, so the type picker is skipped and the Dashboard mounts.
	await expect(page.locator('.uppy-Dashboard-inner, .uppy-Root').first()).toBeVisible();
}

test('the picker states the size rule before a file is chosen', async ({ page, request }) => {
	const limit = await serverLimit(request);
	await openPicker(page, request);
	// Not just "some text": the number has to be the server's, since the whole point of
	// GET /limits is that config.py is the only place it is written.
	const mb = Math.round(limit / 1_000_000);
	await expect(page.getByText(new RegExp(`up to ${mb} MB`, 'i'))).toBeVisible();
});

test('an oversized file is refused in the browser, before it uploads', async ({
	page,
	request
}) => {
	const limit = await serverLimit(request);
	await openPicker(page, request);

	let posted = false;
	page.on('request', (r) => {
		if (r.method() === 'POST' && r.url().includes('/api/v1/storage/')) posted = true;
	});

	await page.locator('.uppy-Dashboard-input').first().setInputFiles({
		name: 'huge.png',
		mimeType: 'image/png',
		buffer: Buffer.alloc(limit + 1024)
	});

	// Uppy's own restriction error. Its wording is Uppy's, so match loosely on the part
	// that is stable across versions.
	await expect(page.getByText(/exceeds maximum allowed size/i)).toBeVisible({ timeout: 10_000 });
	// And it never left the browser: the server would answer 413, but only after the
	// person had waited for the whole transfer.
	expect(posted, 'the oversized file was sent anyway').toBe(false);
});

test('a type the server will not take is refused in the browser too', async ({ page, request }) => {
	await openPicker(page, request);
	await page.locator('.uppy-Dashboard-input').first().setInputFiles({
		name: 'x.svg',
		mimeType: 'image/svg+xml',
		buffer: Buffer.from('<svg onload=alert(1)/>')
	});
	// SVG is a script-injection vector and is absent from upload_limits() on purpose.
	await expect(page.getByText(/you can only upload|not an allowed file type/i)).toBeVisible({
		timeout: 10_000
	});
});

test('a file within the limit is accepted and attached', async ({ page, request }) => {
	await openPicker(page, request);
	// A real 1x1 PNG: Uppy's Compressor and ImageEditor run on the bytes, so a buffer of
	// zeros with a .png name is not enough to get through to the upload.
	const png = Buffer.from(
		'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFAAH/q842iQAAAABJRU5ErkJggg==',
		'base64'
	);
	await page
		.locator('.uppy-Dashboard-input')
		.first()
		.setInputFiles({ name: 'tiny.png', mimeType: 'image/png', buffer: png });
	const upload = page.getByRole('button', { name: /Upload 1 file/i });
	await expect(upload).toBeVisible({ timeout: 10_000 });
	const [res] = await Promise.all([
		page.waitForResponse((r) => r.url().includes('/api/v1/storage/') && r.request().method() === 'POST'),
		upload.click()
	]);
	expect(res.status()).toBe(200);
	// The stored row carries the real byte count. It used to be saved as 0 for every
	// upload, which is why the per-account quota could never bite.
	expect((await res.json()).size).toBeGreaterThan(0);
	// The dialog closes only on an upload that produced an id, so this is the signal
	// that the image is on the question.
	await expect(page.locator('.uppy-Dashboard-inner').first()).toBeHidden({ timeout: 15_000 });
});
