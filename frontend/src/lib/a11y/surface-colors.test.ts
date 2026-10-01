// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { contrastRatio, toRgb } from './contrast';

/**
 * Colours that are written into a component rather than into app.css.
 *
 * `theme-tokens.test.ts` guards the palette; this guards the handful of surfaces that
 * deliberately sit outside it. They exist because they are drawn on the quiz author's
 * own background colour rather than on the app's theme — a token surface there went
 * near-black on near-black in dark mode — so nothing in app.css can check them, and
 * nobody would notice them drifting until a room of people was looking at it.
 */
const read = (path: string) => readFileSync(new URL(path, import.meta.url), 'utf8');

/** Every `--token: value` and `property: #hex` pair this file sets, by selector-ish key. */
const hexesIn = (css: string, after: string): string[] => {
	const i = css.indexOf(after);
	if (i === -1) throw new Error(`no rule matching ${after}`);
	const body = css.slice(i, css.indexOf('}', i));
	return [...body.matchAll(/#[0-9a-fA-F]{6}\b/g)].map((m) => m[0]);
};

describe('the podium', () => {
	const css = read('../play/admin/final_results.svelte');

	it('puts readable ink on the winner', () => {
		// The one block that carries a colour of its own. Everything else on the podium is
		// a theme surface, which theme-tokens.test.ts already covers.
		const gold = hexesIn(css, '.podium-block.is-gold');
		const [bg, , ink] = gold;
		expect(gold.length, 'is-gold should set background, border and colour').toBe(3);
		const ratio = contrastRatio(toRgb(ink), toRgb(bg));
		expect(ratio, `${ink} on ${bg} is ${ratio.toFixed(2)}:1`).toBeGreaterThanOrEqual(4.5);
	});

	it('keeps second and third on theme surfaces, so they follow the theme', () => {
		// They were gradients in silver and bronze, which put a third accent into an
		// identity that is "zinc neutrals plus one loud element".
		for (const rule of ['.podium-block.is-silver', '.podium-block.is-bronze']) {
			expect(hexesIn(css, rule), `${rule} should use tokens, not literals`).toEqual([]);
		}
	});
});

describe('the player result card', () => {
	const css = read('../play/results_kahoot.svelte');

	it('never says right or wrong with colour alone', () => {
		// About one man in twelve cannot separate the green from the red, and this is the
		// one screen of the game that has to land.
		expect(css).toContain('answer_correct');
		expect(css).toContain('answer_wrong');
		for (const icon of ['Check', 'X', 'Minus']) {
			expect(css, `${icon} icon missing`).toContain(`icons/${icon.toLowerCase()}`);
		}
	});
});
