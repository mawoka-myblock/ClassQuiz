<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import { Button } from '$lib/components/ui/button/index.js';
	import { DateTime } from 'luxon';
	import { UAParser } from 'ua-parser-js';
	import Spinner from '$lib/Spinner.svelte';
	import * as Card from '$lib/components/ui/card/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import DeleteAccount from './delete-account.svelte';
	import UnverifiedBanner from './unverified-banner.svelte';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';

	const { t } = getLocalization();

	interface UserAccount {
		id: string;
		email: string;
		username: string;
		verified: boolean;
		created_at: string;
		auth_type: string;
	}

	interface ChangePasswordData {
		oldPassword: string;
		newPassword: string;
		newPasswordConfirm: string;
	}

	let changePasswordData: ChangePasswordData = $state({
		oldPassword: '',
		newPassword: '',
		newPasswordConfirm: ''
	});

	// Replaces the alert() pair this form used to end in -- the idiom the rest of
	// the account surface dropped.
	let passwordError = $state('');
	// Every other form on this surface (register, reset-password, delete-account)
	// disables its submit button and shows a spinner while the request is in
	// flight; this one didn't, so a double click fired the change twice and there
	// was no feedback at all while a slow request was pending.
	let isSubmittingPassword = $state(false);

	let this_session = $state();
	// The avatar endpoint can 404, and a failed <img> paints its alt text across the
	// layout, which is what put "Profile image of reviewer" beside the heading.
	let avatar_ok = $state(true);

	let mismatch = $derived(
		changePasswordData.newPasswordConfirm !== '' &&
			changePasswordData.newPassword !== changePasswordData.newPasswordConfirm
	);

	let passwordChangeDataValid = $derived(
		changePasswordData.newPassword === changePasswordData.newPasswordConfirm &&
			changePasswordData.newPassword.length >= 8 &&
			changePasswordData.oldPassword !== changePasswordData.newPassword &&
			changePasswordData.oldPassword !== ''
	);

	const changePassword = async (e: Event) => {
		e.preventDefault();
		// The client half of the double-submit guard, same as delete-account: the
		// server has its own via rate_limit_key, but this is what stops an
		// impatient double click from spending two of those attempts on one click.
		if (!passwordChangeDataValid || isSubmittingPassword) {
			return;
		}
		isSubmittingPassword = true;
		passwordError = '';
		let res: Response;
		try {
			res = await fetch('/api/v1/users/password/update', {
				method: 'PUT',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					old_password: changePasswordData.oldPassword,
					new_password: changePasswordData.newPassword
				})
			});
		} catch {
			// A network failure used to leave the button live with no feedback at
			// all -- the fetch above was never wrapped, so it rejected into nothing
			// and the form just sat there looking like it hadn't been submitted.
			isSubmittingPassword = false;
			passwordError = $t('settings_page.password_change_failed');
			return;
		}
		if (res.status === 200) {
			// A full document load, not goto(): the redirect below relies on the
			// server having just cleared the session cookies for this response.
			window.location.assign('/account/login?password_changed=true');
			return;
		}
		isSubmittingPassword = false;
		if (res.status === 400) {
			// Also the response for an OAuth account with no password to confirm
			// with, but the form is hidden for those accounts below, so a caller
			// only reaches this from the UI by way of a wrong current password.
			passwordError = $t('settings_page.password_change_wrong');
		} else if (res.status === 429) {
			passwordError = $t('settings_page.password_change_too_many');
		} else {
			passwordError = $t('settings_page.password_change_failed');
		}
	};

	const getUser = async (): Promise<UserAccount> => {
		const response = await fetch('/api/v1/users/me', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		if (response.status === 200) {
			return await response.json();
		} else {
			// Same returnTo as getSessions() below, so whichever of the two 401s
			// first -- this one fires first in practice -- sends the visitor back
			// here after signing in again instead of dropping them on /dashboard.
			window.location.assign('/account/login?returnTo=/account/settings');
		}
	};

	const formatDate = (date: string): string => {
		const dt = DateTime.fromISO(date);
		return dt.toLocaleString(DateTime.DATETIME_MED);
	};

	const getSessions = async () => {
		const res = await fetch('/api/v1/users/sessions/list');
		if (res.status === 200) {
			const res2 = await fetch('/api/v1/users/session');
			if (res2.status === 200) {
				this_session = await res2.json();
			}
			return await res.json();
		} else {
			window.location.assign('/account/login?returnTo=/account/settings');
		}
		return await res.json();
	};

	const getFormattedUserAgent = (userAgent: string): string => {
		const parser = new UAParser(userAgent);
		const result = parser.getResult();
		// A session created without an ordinary browser User-Agent -- a script, an
		// API key, curl -- leaves every field undefined, and this used to print the
		// literal string "undefined undefined (undefined)" into the sessions table.
		if (!result.browser.name && !result.os.name) {
			return $t('settings_page.unknown_browser');
		}
		return `${result.browser.name ?? '?'} ${result.browser.version ?? ''} (${result.os.name ?? '?'})`;
	};

	const deleteSession = async (session_id: string) => {
		const res = await fetch(`/api/v1/users/sessions/${session_id}`, {
			method: 'DELETE'
		});
		if (res.status === 200) {
			window.location.reload();
		}
	};
</script>

<svelte:head>
	<title>frogQuiz - {$t('words.my_account')}</title>
</svelte:head>

<!-- Was a grid-cols-6 with the avatar pinned to a one-sixth column and the rest in a
     nested grid-rows-2 / grid-cols-2. On a phone that collapsed into a broken image
     with its alt text wrapping round the heading, a clipped "change avatar", and three
     password fields squeezed into a row. Settings pages are a single column of
     labelled sections -- one concern per card, its own description, its own action --
     which is what every tool that does this well looks like and what survives a narrow
     screen without any reflow guesswork. -->
<div class="mx-auto w-full max-w-3xl px-4 py-8">
	<h1 class="mb-6 text-2xl font-bold tracking-tight">{$t('words.my_account')}</h1>

	{#await getUser()}
		<Spinner />
	{:then user}
		<div class="flex flex-col gap-6">
			{#if !user.verified}
				<UnverifiedBanner email={user.email} />
			{/if}
			<Card.Root>
				<Card.Header>
					<Card.Title>{$t('settings_page.profile')}</Card.Title>
				</Card.Header>
				<Card.Content class="flex flex-wrap items-center gap-5">
					<!-- The avatar endpoint can 404, and an <img> that fails paints its alt
					     text across the layout. Fall back to the initial instead. -->
					{#if avatar_ok}
						<img
							class="border-border size-20 shrink-0 rounded-full border object-cover"
							src="/api/v1/users/avatar"
							alt=""
							onerror={() => (avatar_ok = false)}
						/>
					{:else}
						<span
							class="bg-muted text-muted-foreground border-border flex size-20 shrink-0 items-center justify-center rounded-full border text-2xl font-semibold"
							aria-hidden="true"
						>
							{user.username?.[0]?.toUpperCase() ?? '?'}
						</span>
					{/if}

					<div class="min-w-0 flex-1">
						<p class="truncate text-lg font-semibold">{user.username}</p>
						<p class="text-muted-foreground truncate text-sm">{user.email}</p>
					</div>

					<!-- Change avatar (/account/settings/avatar) and Public profile (/user/[id])
					     are hidden for the MVP (MVP.md D15); both routes 404. -->
				</Card.Content>
			</Card.Root>

			<Card.Root>
				<Card.Header>
					<Card.Title>{$t('settings_page.password_section')}</Card.Title>
					<Card.Description>{$t('settings_page.password_requirements')}</Card.Description>
				</Card.Header>
				<Card.Content>
					{#if user.auth_type !== 'LOCAL'}
						<!-- OAuth accounts are created with no password at all (frogquiz/oauth/*),
						     so PUT /password/update 400s for them. Same reasoning as
						     delete-account.svelte: say so up front rather than after a submit
						     that can never succeed. -->
						<p class="text-muted-foreground text-sm">
							{$t('settings_page.password_change_oauth')}
						</p>
					{:else}
						<!-- Stacked, not md:flex-row: three password fields side by side is
						     cramped at every width and gives each one about a word of room. -->
						<form class="grid max-w-sm gap-4" onsubmit={changePassword}>
							<div class="grid gap-2">
								<Label for="old-password">{$t('settings_page.old_password')}</Label>
								<Input
									id="old-password"
									type="password"
									autocomplete="current-password"
									bind:value={changePasswordData.oldPassword}
								/>
							</div>
							<div class="grid gap-2">
								<Label for="new-password">{$t('settings_page.new_password')}</Label>
								<Input
									id="new-password"
									type="password"
									autocomplete="new-password"
									bind:value={changePasswordData.newPassword}
								/>
							</div>
							<div class="grid gap-2">
								<Label for="repeat-password"
									>{$t('settings_page.repeat_password')}</Label
								>
								<Input
									id="repeat-password"
									type="password"
									autocomplete="new-password"
									aria-invalid={mismatch}
									bind:value={changePasswordData.newPasswordConfirm}
								/>
								{#if mismatch}
									<p class="text-destructive text-sm">
										{$t('settings_page.passwords_do_not_match')}
									</p>
								{/if}
							</div>
							{#if passwordError !== ''}
								<p class="text-destructive text-sm" aria-live="polite">
									{passwordError}
								</p>
							{/if}
							<div>
								<Button
									disabled={!passwordChangeDataValid || isSubmittingPassword}
									type="submit"
								>
									{#if isSubmittingPassword}
										<LoaderCircle
											class="size-4 animate-spin"
											aria-hidden="true"
										/>
									{/if}
									{$t('settings_page.change_password_submit')}
								</Button>
							</div>
						</form>
					{/if}
				</Card.Content>
			</Card.Root>

			<Card.Root>
				<Card.Header>
					<Card.Title>{$t('settings_page.sessions')}</Card.Title>
					<Card.Description>{$t('settings_page.sessions_description')}</Card.Description>
				</Card.Header>
				<Card.Content>
					{#await getSessions()}
						<Spinner />
					{:then sessions}
						<!-- A table may be wider than the page only inside its own scroll
						     container, and contain:paint stops its content contributing to the
						     document's scroll width. Delete was a bare <button> with no box, so
						     its target was the 42x20 of its own text. -->
						<div class="border-border fq-scroll-x rounded-lg border">
							<table class="w-full text-left text-sm">
								<thead
									class="bg-muted/50 text-muted-foreground text-xs font-medium tracking-wider uppercase"
								>
									<tr>
										<th scope="col" class="px-4 py-3"
											>{$t('overview_page.created_at')}</th
										>
										<th scope="col" class="px-4 py-3"
											>{$t('settings_page.last_seen')}</th
										>
										<th scope="col" class="px-4 py-3">{$t('words.browser')}</th>
										<th scope="col" class="px-4 py-3"
											>{$t('settings_page.this_session?')}</th
										>
										<th scope="col" class="px-4 py-3">
											<span class="sr-only"
												>{$t('settings_page.delete_this_session')}</span
											>
										</th>
									</tr>
								</thead>
								<tbody class="divide-border divide-y">
									{#each sessions as session}
										<tr>
											<td
												class="text-muted-foreground px-4 py-3 whitespace-nowrap"
											>
												{formatDate(session.created_at)}
											</td>
											<td
												class="text-muted-foreground px-4 py-3 whitespace-nowrap"
											>
												{formatDate(session.last_seen)}
											</td>
											<td class="px-4 py-3"
												>{getFormattedUserAgent(session.user_agent)}</td
											>
											<td class="px-4 py-3 whitespace-nowrap">
												{#if session.id === this_session?.id}
													<span
														class="bg-primary/10 text-primary rounded-full px-2 py-0.5 text-xs font-medium"
														>{$t('settings_page.this_session?')}</span
													>
												{:else}
													<span class="text-muted-foreground"
														>&mdash;</span
													>
												{/if}
											</td>
											<td class="px-4 py-3 text-right whitespace-nowrap">
												<Button
													type="button"
													variant="destructive"
													size="sm"
													onclick={() => {
														deleteSession(session.id);
													}}
												>
													{$t('words.delete')}
												</Button>
											</td>
										</tr>
									{/each}
								</tbody>
							</table>
						</div>
					{/await}
				</Card.Content>
			</Card.Root>

			<DeleteAccount authType={user.auth_type} />
		</div>
	{/await}
</div>
