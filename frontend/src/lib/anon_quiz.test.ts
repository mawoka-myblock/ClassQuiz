// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

import { describe, expect, it } from 'vitest';
import { anonDaysLeft } from './anon_quiz';

const DAY = 86_400_000;
const HOUR = 3_600_000;
const now = Date.UTC(2026, 8, 29, 12);

describe('anonDaysLeft', () => {
	it('calls a fresh quiz 30 days even when the window crosses a clock change', () => {
		// 30 local days across the end of summer time is 30 days and one hour.
		expect(anonDaysLeft(new Date(now + 30 * DAY + HOUR), now)).toBe(30);
	});

	it('never says 0 days for a quiz that still exists', () => {
		expect(anonDaysLeft(new Date(now + HOUR), now)).toBe(1);
	});

	it('says 0 once it has expired, and nothing when there is no expiry', () => {
		expect(anonDaysLeft(new Date(now - HOUR), now)).toBe(0);
		expect(anonDaysLeft(null, now)).toBeNull();
	});
});
