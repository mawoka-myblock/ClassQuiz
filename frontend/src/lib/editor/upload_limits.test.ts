// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';

/**
 * The browser's upload rules, kept no looser than the server's.
 *
 * `uploader.svelte` fetches the real numbers from `GET /api/v1/storage/limits` on mount,
 * so these constants only apply until that answers and if it never does. That makes them
 * easy to forget when `config.py` changes -- and a fallback that is *larger* than the
 * server's ceiling is the bad direction: the person picks a file, waits for the upload,
 * and gets a 413 at the end of it.
 *
 * Two things this also pins, each of which was broken:
 *
 * - `restrictions` is an Uppy **Core** option. It used to be passed through the Dashboard
 *   plugin's props, where it does nothing at all, so the picker had no size cap and no
 *   type filter and would accept an SVG.
 * - The server accepted `video/mp4` while the editor passed `video_upload={false}` and
 *   `/edit/videos` was hidden, which is an upload path with no UI in front of it.
 */
const SRC = new URL('../../..', import.meta.url).pathname;
const uploader = readFileSync(`${SRC}/src/lib/editor/uploader.svelte`, 'utf8');
const config = readFileSync(`${SRC}/../frogquiz/config.py`, 'utf8');

/** Reads an int setting out of config.py, underscores and all (8_000_000). */
const setting = (name: string): number => {
	const m = config.match(new RegExp(`${name}:\\s*int\\s*=\\s*([0-9_]+)`));
	if (!m) throw new Error(`${name} is not declared in frogquiz/config.py`);
	return Number(m[1].replace(/_/g, ''));
};

const fallbackMax = (): number => {
	const m = uploader.match(/FALLBACK_MAX_FILE_SIZE\s*=\s*([0-9_]+)/);
	if (!m) throw new Error('FALLBACK_MAX_FILE_SIZE is gone from uploader.svelte');
	return Number(m[1].replace(/_/g, ''));
};

const fallbackTypes = (): string[] => {
	const m = uploader.match(/FALLBACK_TYPES\s*=\s*\[([^\]]+)\]/);
	if (!m) throw new Error('FALLBACK_TYPES is gone from uploader.svelte');
	return [...m[1].matchAll(/'([^']+)'/g)].map((x) => x[1]);
};

describe('the uploader fallbacks', () => {
	it('are no looser than max_image_upload_size', () => {
		expect(fallbackMax()).toBeLessThanOrEqual(setting('max_image_upload_size'));
	});

	it('offer only types the server accepts', () => {
		// The allow-list the server builds from max_image_upload_size. Video is excluded
		// by enable_video_upload and must not appear here while that is off.
		const serverImageTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/webp'];
		for (const type of fallbackTypes()) {
			expect(serverImageTypes, `${type} is not in upload_limits()`).toContain(type);
		}
		expect(fallbackTypes().length).toBeGreaterThan(0);
	});

	it('never offer SVG, which is a script-injection vector', () => {
		expect(fallbackTypes()).not.toContain('image/svg+xml');
		expect(config).not.toContain('image/svg+xml');
	});

	it('are on the Uppy instance, not the Dashboard plugin', () => {
		// `new Uppy({ restrictions: ... })`. Passed as a Dashboard option it is silently
		// ignored, which is how the cap came to be absent for as long as it was.
		expect(uploader).toMatch(/new Uppy\(\{\s*restrictions:/);
		const dashboardOpts = uploader.match(/const dashboard_options = \{[^}]*\}/s)?.[0] ?? '';
		expect(dashboardOpts, 'restrictions are back on the Dashboard').not.toContain(
			'restrictions'
		);
	});

	it('are replaced at runtime by the server, so config.py is the only source', () => {
		expect(uploader).toContain('/api/v1/storage/limits');
		expect(uploader).toMatch(/uppy\.setOptions\(/);
	});
});

describe('video upload', () => {
	it('stays off until enable_video_upload and the hidden route move together', () => {
		expect(config).toMatch(/enable_video_upload:\s*bool\s*=\s*False/);
		const hidden = readFileSync(`${SRC}/src/lib/hidden_routes.ts`, 'utf8');
		expect(hidden).toContain("'/edit/videos'");
	});
});
