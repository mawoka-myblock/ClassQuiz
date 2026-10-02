// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// The two states a player spends almost all of their time on /play looking at: an empty
// PIN box, and a Submit they cannot press yet. Both were misleading on 2026-10-02.

import { expect, test, type Locator } from '@playwright/test';
import {
	gotoPlayHydrated,
	hostFromViewPage,
	mc,
	PHONE,
	rememberAnonQuiz,
	saveQuiz
} from './helpers';

test.use({ viewport: PHONE });

const QUIZ = {
	title: 'Join states',
	description: 'e2e',
	questions: [
		mc('Capital of Portugal?', [
			['Lisbon', true],
			['Porto', false]
		])
	]
};

/**
 * A control's painted colour as sRGB.
 *
 * `getComputedStyle` hands back `oklch(...)` verbatim for a token defined in oklch, so
 * parsing the numbers out of the string gives lightness and chroma, not channels -- the
 * first version of this file did exactly that and read `oklch(0.967 ...)` as a luminance
 * of 0.9. Painting the colour onto a canvas makes the browser resolve it, whatever the
 * notation.
 */
function painted(prop: 'backgroundColor' | 'color') {
	return (l: Locator) =>
		l.evaluate((e, p) => {
			const value = getComputedStyle(e)[p as 'backgroundColor' | 'color'];
			const c = document.createElement('canvas');
			c.width = c.height = 1;
			const ctx = c.getContext('2d')!;
			ctx.fillStyle = value;
			ctx.fillRect(0, 0, 1, 1);
			const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data;
			return [r, g, b] as [number, number, number];
		}, prop);
}
const bg = painted('backgroundColor');
const fg = painted('color');

type Rgb = [number, number, number];

/** Rough perceptual lightness, 0-255. Enough to tell a dark button from a light one. */
const luminance = ([r, g, b]: Rgb) => 0.2126 * r + 0.7152 * g + 0.0722 * b;

/**
 * WCAG contrast ratio. The unit suite has a tested implementation, but it reads app.css
 * rather than a live computed style, so this is the browser-side twin.
 */
const contrast = (a: Rgb, b: Rgb) => {
	const rel = (c: Rgb) => {
		const [r, g, bl] = c.map((v) => {
			const srgb = v / 255;
			return srgb <= 0.03928 ? srgb / 12.92 : ((srgb + 0.055) / 1.055) ** 2.4;
		});
		return 0.2126 * r + 0.7152 * g + 0.0722 * bl;
	};
	const [x, y] = [rel(a), rel(b)].sort((m, n) => n - m);
	return (x + 0.05) / (y + 0.05);
};

test('the PIN box is empty rather than pre-filled with something that looks like a PIN', async ({
	page
}) => {
	await gotoPlayHydrated(page);
	const pin = page.getByRole('textbox', { name: 'Game PIN' });

	// It used to carry placeholder="000000", which in a mono face at 0.35em tracking is
	// indistinguishable from a real entry -- most visibly on the error state, where the
	// page said "No game with that PIN" above what looked like a typed PIN.
	await expect(pin).toHaveValue('');
	const placeholder = await pin.getAttribute('placeholder');
	expect(placeholder ?? '', 'a placeholder that reads as a value').not.toMatch(/\d/);

	// The digit count has to be stated somewhere, and the hint is where it belongs.
	await expect(page.getByText(/6-digit PIN/i)).toBeVisible();
});

test('a Submit that is not ready reads as inert, not as a broken primary button', async ({
	page,
	request
}) => {
	// A real game, so the enabled state can be reached. A rejected PIN is not a way in:
	// `set_game_pin` clears the field on failure, so the button correctly goes straight
	// back to disabled. (My first version of this test assumed otherwise and failed
	// against correct code.)
	const saved = await saveQuiz(request, QUIZ);
	expect(saved.status).toBe(200);
	await rememberAnonQuiz(page, saved.body.id, saved.secret!);
	const pin = await hostFromViewPage(page, saved.body.id);

	await gotoPlayHydrated(page);
	const submit = page.getByRole('button', { name: 'Submit' });
	await expect(submit).toBeDisabled();
	const disabledBg = await bg(submit);
	const disabledFg = await fg(submit);

	// `disabled:opacity-50` over a near-black primary gave a flat mid-grey with pale
	// text, which is what a player stares at for the whole time they are typing. The
	// waiting state has to be a light, inert surface in light mode -- not a dark button
	// turned down.
	expect(luminance(disabledBg), `disabled background rgb(${disabledBg})`).toBeGreaterThan(200);
	// And its label still has to be readable, which opacity-50 on white does not
	// guarantee. 4.5:1 is AA for body text.
	expect(
		contrast(disabledFg, disabledBg),
		`rgb(${disabledFg}) on rgb(${disabledBg})`
	).toBeGreaterThan(4.5);

	// Now the enabled state, from the nickname step of a game that exists.
	await page.getByRole('textbox', { name: 'Game PIN' }).fill(pin);
	const nickname = page.getByRole('textbox', { name: 'Username' });
	await expect(nickname).toBeVisible({ timeout: 15_000 });
	await nickname.fill('ana');
	await expect(submit).toBeEnabled();

	// Polled, not read once: the button carries `transition-all`, so the background
	// animates from the disabled surface to the primary one. Reading it immediately after
	// the state flips returns a colour partway between the two -- this test first failed
	// on rgb(236,236,237), which is neither token and looked like a bug in the app.
	await expect.poll(async () => luminance(await bg(submit)), { timeout: 5000 }).toBeLessThan(100);

	// And the two are genuinely different surfaces, not one colour at two opacities.
	expect(await bg(submit)).not.toEqual(disabledBg);
});
