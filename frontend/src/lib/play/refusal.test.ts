// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';

/**
 * The player screen handles the server's refusals, and lets go of its listeners.
 *
 * Two bugs, one line apart:
 *
 * 1. `question_not_active` and `already_replied` had no listener anywhere in the
 *    frontend. The screen sets `selected_answer` the moment a tile is tapped, so a
 *    refused answer still read "Answer locked in" and the player learnt the truth only
 *    from a +0 on the results screen -- which looks like a bug, not a wrong answer.
 * 2. `socket.on('everyone_answered', ...)` was registered at component init with no
 *    cleanup, and the play page recreates this component per question (`{#key unique}`).
 *    One listener per question accumulated, each holding a destroyed component's state
 *    alive and writing to it.
 *
 * This is a source guard rather than a browser test on purpose. The refusal itself is
 * already driven over a real socket by `e2e/live-socket.e2e.ts` ("after the timer", "after
 * the host showed the results"). Reaching it *through the UI* needs the player's local
 * countdown to lag the server's while a tile is still tappable, which is a real
 * condition (a throttled phone) but not one Playwright reproduces reliably -- freezing
 * the page clock does not hold the countdown. Rather than land a flaky spec, this pins
 * the wiring, which is what regressed.
 */
const src = readFileSync(new URL('./question.svelte', import.meta.url).pathname, 'utf8');

/** The events this component subscribes to, and whether each is released on destroy. */
const subscriptions = (): { event: string; handler: string }[] =>
	[...src.matchAll(/socket\.on\(\s*'([^']+)'\s*,\s*([A-Za-z_$][\w$]*)\s*\)/g)].map((m) => ({
		event: m[1],
		handler: m[2]
	}));

describe('the player question screen', () => {
	it('listens for the refusal the server actually sends', () => {
		expect(subscriptions().map((s) => s.event)).toContain('question_not_active');
	});

	it('tells the player it did not count, instead of claiming it was locked in', () => {
		// The string is only reachable when `refused` is set, and `refused` is only set
		// from the refusal handler -- so the message cannot drift away from its cause.
		expect(src).toContain('words.answer_too_late');
		expect(src).toMatch(/refused\s*=\s*true/);
		// And it replaces the confirmation rather than appearing beside it.
		const block = src.slice(src.indexOf('answer_too_late'));
		expect(block).toMatch(/answer_too_late[\s\S]{0,200}answer_locked_in/);
	});

	it('only corrects a screen that was claiming an answer', () => {
		// A refusal for a question the player never answered needs no correction: they
		// are already looking at "time is up". Setting `refused` regardless would turn
		// that into "that one did not count" for an answer they never gave.
		const handler = src.slice(src.indexOf('on_question_not_active'));
		expect(handler).toMatch(/selected_answer !== undefined/);
	});

	it('releases every listener it takes, since it is recreated per question', () => {
		const subs = subscriptions();
		expect(subs.length, 'no socket.on(event, namedHandler) found').toBeGreaterThan(0);
		const offs = [...src.matchAll(/socket\.off\(\s*'([^']+)'\s*,\s*([A-Za-z_$][\w$]*)\s*\)/g)].map(
			(m) => `${m[1]}:${m[2]}`
		);
		for (const { event, handler } of subs) {
			expect(offs, `socket.on('${event}') is never released`).toContain(`${event}:${handler}`);
		}
		expect(src, 'the cleanup is not wired to the component lifecycle').toMatch(
			/onDestroy\(\s*\(\)\s*=>/
		);
	});

	it('takes no listener with an inline function, which cannot be released', () => {
		// `socket.on('x', () => ...)` has no reference to pass to socket.off, so it is a
		// leak by construction. This is how the `everyone_answered` one was written.
		expect(src).not.toMatch(/socket\.on\(\s*'[^']+'\s*,\s*(\(|function)/);
	});
});
