// SPDX-FileCopyrightText: 2026 frogQuiz contributors
//
// SPDX-License-Identifier: MPL-2.0

// A user journey, not a feature test: somebody signs up, forgets their password a week
// later, and gets back in.
//
// MVP.md lists "registration/password recovery validated end-to-end" as a must-do before
// sharing, and until 2026-10-02 it could not be tested at all: `/forgot-password` answers
// 503 unless `mail_configured` is true, and the e2e stack had no relay. `e2e/mailsink.py`
// is that relay now, so this walks the whole path a person walks -- including the parts
// that only exist inside the email, which is where this breaks in practice: the template
// rendering, and the link being built from ROOT_ADDRESS rather than the API's own host.
//
// What this still does not prove is that a real provider accepts and delivers the mail.
// That is a deployment question and stays on the manual checklist in DEPLOY.md.

import fs from 'node:fs';
import path from 'node:path';
import { expect, test, type Page } from '@playwright/test';

const MAIL_DIR = path.resolve(process.cwd(), '../e2e/.data/mail');
const NEW_PASSWORD = 'Frog-recovered-password-2';
const OLD_PASSWORD = 'Frog-e2e-password-1';

/** Messages the sink has written, newest first. */
function mailbox(): string[] {
	if (!fs.existsSync(MAIL_DIR)) return [];
	return fs
		.readdirSync(MAIL_DIR)
		.filter((f) => f.endsWith('.eml'))
		.sort()
		.reverse()
		.map((f) => fs.readFileSync(path.join(MAIL_DIR, f), 'utf8'));
}

/** Waits for a message addressed to `to` and returns it. */
async function waitForMail(to: string): Promise<string> {
	let found: string | undefined;
	await expect
		.poll(
			() => {
				found = mailbox().find((m) => m.includes(to));
				return found !== undefined;
			},
			{ timeout: 20_000, message: `no message to ${to} in ${MAIL_DIR}` }
		)
		.toBe(true);
	return found!;
}

/** The login page is two forms: identify, then prove. */
async function logInThroughUI(page: Page, email: string, password: string) {
	await page.goto('/account/login');
	await page.getByRole('textbox', { name: 'Email or Username' }).fill(email);
	await page.getByRole('button', { name: 'Continue' }).click();
	await page.getByRole('textbox', { name: 'Password' }).fill(password);
	await page.getByRole('button', { name: 'Continue' }).last().click();
}

test('somebody signs up, forgets their password, and gets back in through the email', async ({
	page
}) => {
	const username = `recover${Date.now().toString(36)}`;
	const email = `${username}@example.com`;

	await test.step('they sign up', async () => {
		await page.goto('/account/register');
		await page.getByRole('textbox', { name: 'E-mail address' }).fill(email);
		await page.getByRole('textbox', { name: 'Username' }).fill(username);
		await page.getByRole('textbox', { name: 'Password', exact: true }).fill(OLD_PASSWORD);
		await page.getByRole('textbox', { name: 'Repeat password' }).fill(OLD_PASSWORD);
		await page.getByRole('checkbox', { name: /Privacy policy/ }).check();
		await page.getByRole('checkbox', { name: /Terms of Service/ }).check();
		await page.getByRole('button', { name: 'Register' }).click();
		await expect(page.getByRole('status')).toBeVisible();
		await expect(page.getByRole('status')).not.toHaveClass(/destructive/);
	});

	await test.step('a week later they cannot remember the password', async () => {
		await logInThroughUI(page, email, 'Definitely-not-the-password-9');
		await expect(page.getByText("That email address and password don't match.")).toBeVisible();
	});

	let resetUrl = '';
	await test.step('they ask for a reset and the email arrives', async () => {
		// Reached the way a person reaches it, from the login page, not by URL.
		await page.getByRole('link', { name: /Forgot/i }).click();
		await expect(page).toHaveURL(/\/account\/reset-password/);
		await page.getByRole('textbox', { name: 'E-mail' }).fill(email);
		await page.getByRole('button', { name: /Send|Reset|Continue/i }).click();

		const message = await waitForMail(email);
		// The link has to point at the site people browse (ROOT_ADDRESS), not at the API
		// host. On a split deploy those differ, and getting it wrong sends everyone to a
		// hostname that serves no page -- the failure DEPLOY.md warns about.
		const match = message.match(
			/https?:\/\/[^\s"'<>]*\/account\/password-reset\?token=[^\s"'<>&]+/
		);
		expect(match, `no reset link in the message:\n${message.slice(0, 1200)}`).not.toBeNull();
		resetUrl = match![0].replace(/&amp;/g, '&');
		expect(resetUrl).toContain('localhost:3000');
	});

	await test.step('the link lets them set a new password', async () => {
		await page.goto(resetUrl);
		await page.getByRole('textbox', { name: 'Password', exact: true }).fill(NEW_PASSWORD);
		await page.getByRole('textbox', { name: 'Repeat password' }).fill(NEW_PASSWORD);
		await page.getByRole('button', { name: /Reset|Save|Continue|Submit/i }).click();
		await expect(page.getByText(/password/i).first()).toBeVisible();
	});

	await test.step('the new password works and the old one does not', async () => {
		await logInThroughUI(page, email, NEW_PASSWORD);
		// Landing anywhere other than the login form is the signal; My Quizzes is where
		// a signed-in person goes.
		await page.waitForURL((u) => !u.pathname.startsWith('/account/login'), { timeout: 15_000 });

		await page.goto('/account/settings');
		await page
			.getByRole('button', { name: /Log out|Sign out/i })
			.first()
			.click();
		await logInThroughUI(page, email, OLD_PASSWORD);
		await expect(page.getByText("That email address and password don't match.")).toBeVisible();
	});

	await test.step('the link cannot be used a second time', async () => {
		// The token is consumed with GETDEL, so a forwarded or re-opened email is dead.
		await page.goto(resetUrl);
		await expect(page.getByText(/link|expired|used|invalid/i).first()).toBeVisible();
	});
});
