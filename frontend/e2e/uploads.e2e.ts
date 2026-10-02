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
import zlib from 'node:zlib';
import { mc, saveQuiz, rememberAnonQuiz } from './helpers';

/** The ceiling the server publishes, so this spec does not hardcode a second copy. */
async function serverLimit(request): Promise<number> {
	const res = await request.get('/api/v1/storage/limits');
	expect(res.status()).toBe(200);
	return (await res.json()).max_file_size as number;
}

/** A valid single-colour PNG of a given size, built with zlib so the bytes stay small.
 *  Used to get an image past Uppy's byte cap and the client-side Compressor while being
 *  over the server's pixel cap. */
function pngOfSize(width: number, height: number): Buffer {
	const chunk = (type: string, data: Buffer) => {
		const len = Buffer.alloc(4);
		len.writeUInt32BE(data.length, 0);
		const tag = Buffer.from(type, 'ascii');
		const body = Buffer.concat([tag, data]);
		const c = Buffer.alloc(4);
		c.writeUInt32BE(zlib.crc32(body) >>> 0, 0);
		return Buffer.concat([len, body, c]);
	};
	const ihdr = Buffer.alloc(13);
	ihdr.writeUInt32BE(width, 0);
	ihdr.writeUInt32BE(height, 4);
	ihdr[8] = 8; // bit depth
	ihdr[9] = 2; // colour type: truecolour
	const row = Buffer.concat([Buffer.from([0]), Buffer.alloc(width * 3, 0)]);
	const raw = Buffer.concat(Array.from({ length: height }, () => row));
	const sig = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
	return Buffer.concat([
		sig,
		chunk('IHDR', ihdr),
		chunk('IDAT', zlib.deflateSync(raw)),
		chunk('IEND', Buffer.alloc(0))
	]);
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

	await page
		.locator('.uppy-Dashboard-input')
		.first()
		.setInputFiles({
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
	await page
		.locator('.uppy-Dashboard-input')
		.first()
		.setInputFiles({
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
		page.waitForResponse(
			(r) => r.url().includes('/api/v1/storage/') && r.request().method() === 'POST'
		),
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

test('an image over the pixel cap is refused, with advice about dimensions not bytes', async ({
	page,
	request
}) => {
	// A decompression bomb: a 20000x20000 PNG of one colour is under the byte cap but a
	// ~1.6GB bitmap in every browser that renders it -- every player's phone and the
	// projector. The server rejects it on dimensions (see TestStorage); this checks the
	// editor turns that 413 into advice a person can act on, which is different from the
	// byte-size 413's advice: shrinking the file does not help.
	//
	// The test image is a 9000x8 strip, not a true square bomb: it is over the 8000 cap
	// in one dimension but only 72k pixels, so Uppy's client-side Compressor decodes it in
	// the test browser without allocating the raster the real bomb would.
	await openPicker(page, request);
	const limit = await serverLimit(request);

	const strip = pngOfSize(9000, 8);
	expect(
		strip.length,
		'the strip must be under the byte cap, or this tests the wrong 413'
	).toBeLessThan(limit);

	await page
		.locator('.uppy-Dashboard-input')
		.first()
		.setInputFiles({ name: 'wide.png', mimeType: 'image/png', buffer: strip });
	const upload = page.getByRole('button', { name: /Upload 1 file/i });
	await expect(upload).toBeVisible({ timeout: 10_000 });

	const [res] = await Promise.all([
		page.waitForResponse(
			(r) => r.url().includes('/api/v1/storage/') && r.request().method() === 'POST'
		),
		upload.click()
	]);
	// It was sent -- Uppy cannot know the dimensions -- and the server refused it.
	expect(res.status()).toBe(413);
	expect((await res.json()).detail).toMatch(/pixel/i);

	// And the editor explains the real problem rather than showing the byte-size message.
	await expect(page.getByText(/pixel dimensions are too big/i)).toBeVisible({ timeout: 10_000 });
	// The dialog stays open so another file can be chosen.
	await expect(page.locator('.uppy-Dashboard-inner').first()).toBeVisible();
});
