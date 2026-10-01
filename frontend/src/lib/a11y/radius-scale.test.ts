// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';

/**
 * Corners come off one scale.
 *
 * `--radius` is 0.875rem and `app.css` derives every step from it, but Tailwind v4 keeps
 * its own `--radius: 0.25rem` inside `@theme default inline reference`, which the app's
 * `:root` override does not reach. So a bare `rounded`, `rounded-t` or `rounded-b`
 * compiles to a 4px corner while everything around it is 8.4-25.2px, and nothing says
 * so — it looks like a class that works. Four of them had shipped, one in a modal whose
 * own shell rounds at 14px.
 *
 * This is cheap and textual: it reads the source, not the rendered page, so it cannot
 * see whether a radius is the *right* step. What it does is make the off-scale ones
 * impossible to add back.
 */
const SRC = new URL('../..', import.meta.url).pathname;

const walk = (dir: string): string[] =>
	readdirSync(dir).flatMap((entry) => {
		const path = join(dir, entry);
		if (statSync(path).isDirectory()) return entry === 'node_modules' ? [] : walk(path);
		return /\.(svelte|css|ts)$/.test(entry) ? [path] : [];
	});

const files = walk(SRC).filter((f) => !f.endsWith('.test.ts'));

describe('the radius scale', () => {
	it('has no bare rounded / rounded-t / rounded-b, which compile to 4px', () => {
		// Matches the class on its own, not rounded-lg, rounded-t-xl, rounded-tr-lg…
		const bare = /\brounded(-[tbrl])?(?=["'\s])/;
		const offenders: string[] = [];
		for (const file of files) {
			readFileSync(file, 'utf8')
				.split('\n')
				.forEach((line, i) => {
					if (bare.test(line)) offenders.push(`${file.replace(SRC, '')}:${i + 1}`);
				});
		}
		expect(offenders, 'use a step: rounded-sm/md/lg/xl/2xl/full').toEqual([]);
	});

	it('declares every step it offers, so none falls back to Tailwind s own', () => {
		const css = readFileSync(join(SRC, 'app.css'), 'utf8');
		for (const step of ['xs', 'sm', 'md', 'lg', 'xl', '2xl', '3xl', '4xl']) {
			expect(css, `--radius-${step} is not derived from --radius`).toMatch(
				new RegExp(`--radius-${step}:\\s*(calc\\(var\\(--radius\\)|var\\(--radius\\))`)
			);
		}
	});

	it('sets no border-radius by hand outside the token block', () => {
		const offenders: string[] = [];
		for (const file of files) {
			if (file.endsWith('app.css')) continue;
			readFileSync(file, 'utf8')
				.split('\n')
				.forEach((line, i) => {
					if (/border-radius:/.test(line) && !/var\(--radius/.test(line)) {
						offenders.push(`${file.replace(SRC, '')}:${i + 1} — ${line.trim()}`);
					}
				});
		}
		expect(offenders, 'use a rounded-* class, or var(--radius-*)').toEqual([]);
	});
});
