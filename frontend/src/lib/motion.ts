// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

/**
 * The motion scale, for Svelte's JS transitions.
 *
 * `app.css` carries the same five durations and four curves as custom properties, for
 * anything animated in CSS. These are the numbers for `fly`, `fade`, `flip` and friends,
 * which take milliseconds rather than a token. The two are asserted equal in
 * `motion.test.ts`, because a scale that exists twice drifts the moment nobody is
 * looking.
 *
 * Chosen by how far a thing travels and how big it is, the way Material and the HIG
 * choose them — not by taste:
 *
 *   micro    a state swap in place: hover, focus, an icon changing
 *   control  a button, a chip, a toggle, a tooltip
 *   surface  a card, a drawer, a row changing places in a list
 *   stage    a full screen on a projector: a question, a result
 *   reveal   the podium building, the one moment worth waiting for
 */
export const DUR = {
	micro: 120,
	control: 200,
	surface: 320,
	stage: 500,
	reveal: 750
} as const;

/** The same curves as `--fq-ease-*`, as the control points Svelte's easing takes. */
export const EASE = {
	out: [0.2, 0, 0, 1],
	in: [0.3, 0, 1, 1],
	inOut: [0.4, 0, 0.2, 1],
	spring: [0.2, 1.3, 0.4, 1]
} as const;

/**
 * Whether this viewer asked for less motion.
 *
 * Read at call time rather than cached: somebody can change it while a game is running,
 * and a host screen can be up for an hour.
 */
export const reduced = (): boolean =>
	typeof window !== 'undefined' &&
	window.matchMedia?.('(prefers-reduced-motion: reduce)').matches === true;

/**
 * A duration that collapses to nothing when less motion was asked for.
 *
 * `app.css` already clamps every CSS transition and animation, but Svelte's transitions
 * are JavaScript and never see that media query — so anything using `fly`, `fade` or
 * `flip` has to pass its duration through here.
 */
export const dur = (ms: number): number => (reduced() ? 0 : ms);

/** The same, for a stagger: the delay between one element arriving and the next. */
export const stagger = (index: number, step: number): number => (reduced() ? 0 : index * step);
