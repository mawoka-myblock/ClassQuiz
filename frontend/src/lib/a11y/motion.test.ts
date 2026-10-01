// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { DUR, EASE } from '$lib/motion';

/**
 * The motion scale, kept honest.
 *
 * It exists twice — as custom properties for anything animated in CSS, and as numbers in
 * `lib/motion.ts` for Svelte's JS transitions, which never see a CSS variable. Two copies
 * of one scale drift the moment nobody is looking, so they are asserted equal here.
 *
 * The tree had fifteen different durations and almost no easing before this.
 */
const SRC = new URL('../..', import.meta.url).pathname;
const css = readFileSync(join(SRC, 'app.css'), 'utf8');

const cssVar = (name: string): string => {
	const m = css.match(new RegExp(`--${name}:\\s*([^;]+);`));
	if (!m) throw new Error(`--${name} is not declared in app.css`);
	return m[1].trim();
};

const walk = (dir: string): string[] =>
	readdirSync(dir).flatMap((entry) => {
		const path = join(dir, entry);
		if (statSync(path).isDirectory()) return entry === 'node_modules' ? [] : walk(path);
		return entry.endsWith('.svelte') ? [path] : [];
	});

describe('the motion scale', () => {
	it('is the same in CSS and in TypeScript', () => {
		for (const [name, ms] of Object.entries(DUR)) {
			expect(cssVar(`fq-dur-${name}`), `--fq-dur-${name}`).toBe(`${ms}ms`);
		}
	});

	it('runs shortest to longest, so a step always means something', () => {
		const values = Object.values(DUR);
		expect([...values].sort((a, b) => a - b)).toEqual(values);
		// The longest is the podium build. Anything beyond a second on a control is a
		// hang, not a flourish.
		expect(values.at(-1)).toBeLessThanOrEqual(1000);
	});

	it('declares all four curves, matching the control points in motion.ts', () => {
		for (const [name, points] of Object.entries(EASE)) {
			const token = name === 'inOut' ? 'in-out' : name;
			expect(cssVar(`fq-ease-${token}`)).toBe(`cubic-bezier(${points.join(', ')})`);
		}
	});

	it('turns itself off for anyone who asks for less motion', () => {
		const i = css.indexOf('@media (prefers-reduced-motion: reduce)');
		expect(i, 'no global reduced-motion block in app.css').toBeGreaterThan(-1);
		const block = css.slice(i, i + 900);
		expect(block).toMatch(/animation-duration:\s*1ms\s*!important/);
		expect(block).toMatch(/transition-duration:\s*1ms\s*!important/);
		for (const name of Object.keys(DUR)) {
			expect(block, `--fq-dur-${name} is not clamped`).toContain(`--fq-dur-${name}: 1ms`);
		}
	});

	it('animates nothing that forces layout', () => {
		// transform and opacity are composited; width, height, top, left and margin all
		// make the browser lay the page out again, 60 times a second, on a projector.
		const banned = /transition-\[?(width|height|top|left|right|bottom|margin|padding)\b/;
		const offenders: string[] = [];
		for (const file of walk(SRC)) {
			readFileSync(file, 'utf8')
				.split('\n')
				.forEach((line, i) => {
					if (banned.test(line)) offenders.push(`${file.replace(SRC, '')}:${i + 1}`);
				});
		}
		expect(offenders, 'animate transform/opacity instead').toEqual([]);
	});
});
