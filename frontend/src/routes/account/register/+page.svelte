<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { createForm } from 'felte';
	import { getLocalization } from '$lib/i18n';
	import { validateSchema } from '@felte/validator-yup';
	import { navbarVisible } from '$lib/stores.svelte.ts';
	import Footer from '$lib/footer.svelte';
	import * as Card from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';
	import CircleCheck from '@lucide/svelte/icons/circle-check';
	import CircleAlert from '@lucide/svelte/icons/circle-alert';
	import { page } from '$app/state';
	import { safeReturnTo } from '$lib/return_to';

	const { t } = getLocalization();

	// "Create an account to keep this quiz" sends people here with returnTo=/view/{id}.
	// This page ignored it, so a new account had no route back to the quiz it was made
	// to claim. Registering does not sign you in, so it is carried on to the login link.
	const return_to = $derived(safeReturnTo(page.url.searchParams.get('returnTo'), ''));
	const login_href = $derived(
		return_to ? `/account/login?returnTo=${encodeURIComponent(return_to)}` : '/account/login'
	);
	import reporter from '@felte/reporter-tippy';

	navbarVisible.visible = true;
	import * as yup from 'yup';

	const registerSchema = yup.object({
		email: yup.string().email('Email must be valid!').required(),
		password1: yup
			.string()
			.required()
			.min(8, 'Password must be at least 8 characters long!')
			.max(100, 'Password must be at most 100 characters long!'),
		password2: yup
			.string()
			.required()
			.test('equal', 'Passwords do not match!', function (v) {
				const ref = yup.ref('password1');
				return v === this.resolve(ref);
			}),
		username: yup
			.string()
			.required()
			.min(3, 'Username must be at least 3 characters long')
			.max(20, 'Username must be at most 20 characters long'),
		privacy_accept: yup
			.boolean()
			.oneOf([true], 'You must accept the privacy policy to register!'),
		tos_accept: yup.boolean().oneOf([true], 'You must accept the terms of service to register!')
	});

	const { form, errors, isValid, isSubmitting } = createForm<
		yup.InferType<typeof registerSchema>
	>({
		validate: validateSchema(registerSchema),
		extend: [reporter()],
		onSubmit: async (values) => {
			registeredEmail = values.email;
			try {
				const res = await fetch('/api/v1/users/create', {
					method: 'post',
					body: JSON.stringify({
						email: values.email,
						password: values.password1,
						username: values.username
					}),
					headers: {
						'Content-Type': 'application/json'
					}
				});
				if (res.status === 200) {
					const data = await res.json();
					if (data.verified) {
						responseData.data = '200_verified';
					} else {
						responseData.data = '200';
					}
				} else if (res.status === 409) {
					responseData.data = '409';
				} else if (res.status === 400) {
					responseData.data = '400';
				} else if (res.status === 429) {
					responseData.data = '429';
				} else if (res.status === 503) {
					responseData.data = '503';
				} else if (res.status === 423) {
					responseData.data = '423';
				} else {
					responseData.data = 'error';
				}
			} catch {
				responseData.data = 'error';
			}
			responseData.open = true;
		}
	});
	let responseData = $state({
		open: false,
		data: ''
	});

	// Registration had no way back: if the confirmation mail was lost or filtered,
	// signing up again just returned 409 and the address stayed unverified forever.
	let resend = $state({ busy: false, result: '' });
	let registeredEmail = $state('');

	const resendVerification = async () => {
		resend.busy = true;
		resend.result = '';
		try {
			const res = await fetch('/api/v1/users/resend-verification', {
				method: 'post',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email: registeredEmail })
			});
			resend.result = res.ok ? 'sent' : res.status === 429 ? 'too_many' : 'failed';
		} catch {
			resend.result = 'failed';
		} finally {
			resend.busy = false;
		}
	};
</script>

<svelte:head>
	<title>frogQuiz - Register</title>
</svelte:head>

<!-- Rebuilt on the same Card/Label/Input/Button primitives as the login page, which
     this sits directly beside in the flow and looked nothing like. What was here was
     entirely upstream: floating labels over bg-white/dark:bg-gray-800, gray-500 rings
     that turned sky-600 on focus -- a fourth accent the design system does not have,
     and CLAUDE.md is explicit that adding one is what makes this look generic -- an
     inlined spinner with hardcoded fill-blue-800, and a gray-700 submit. -->
<div class="flex min-h-dvh items-center justify-center px-4 py-10">
	<Card.Root class="w-full max-w-sm">
		<Card.Header class="gap-1 text-center">
			<Card.Title class="text-3xl font-bold tracking-tight">frogQuiz</Card.Title>
			<Card.Description class="grid gap-1">
				<span class="text-foreground text-lg font-medium"
					>{$t('register_page.greeting')}</span
				>
				<span>{$t('register_page.create_account')}</span>
			</Card.Description>
		</Card.Header>

		<Card.Content>
			<form use:form class="grid gap-4">
				<div class="grid gap-2">
					<Label for="email">{$t('words.email')}</Label>
					<Input
						id="email"
						name="email"
						type="email"
						autocomplete="email"
						placeholder={$t('words.email')}
						aria-invalid={!!$errors.email}
					/>
					{#if $errors.email}
						<p class="text-destructive text-sm">{$errors.email}</p>
					{/if}
				</div>

				<div class="grid gap-2">
					<Label for="username">{$t('words.username')}</Label>
					<Input
						id="username"
						name="username"
						type="text"
						autocomplete="username"
						placeholder={$t('words.username')}
						aria-invalid={!!$errors.username}
					/>
					{#if $errors.username}
						<p class="text-destructive text-sm">{$errors.username}</p>
					{/if}
				</div>

				<div class="grid gap-2">
					<Label for="password1">{$t('words.password')}</Label>
					<Input
						id="password1"
						name="password1"
						type="password"
						autocomplete="new-password"
						placeholder={$t('words.password')}
						aria-invalid={!!$errors.password1}
					/>
					{#if $errors.password1}
						<p class="text-destructive text-sm">{$errors.password1}</p>
					{/if}
				</div>

				<div class="grid gap-2">
					<Label for="password2">{$t('register_page.repeat_password')}</Label>
					<Input
						id="password2"
						name="password2"
						type="password"
						autocomplete="new-password"
						placeholder={$t('register_page.repeat_password')}
						aria-invalid={!!$errors.password2}
					/>
					{#if $errors.password2}
						<p class="text-destructive text-sm">{$errors.password2}</p>
					{/if}
				</div>

				<!-- The consent boxes had their label as a sibling of the input, so tapping
				     the words did nothing and the target was the 16px box. Wrapping makes the
				     whole row one target, and the links inside it still work. -->
				<div class="grid gap-2">
					<label class="flex min-h-11 cursor-pointer items-start gap-3 text-sm">
						<input
							type="checkbox"
							name="privacy_accept"
							class="accent-primary mt-0.5 size-5 shrink-0"
							aria-invalid={!!$errors.privacy_accept}
						/>
						<span>
							{$t('register_page.read_privacy_policy_prefix')}
							<a href="/docs/privacy-policy" class="underline underline-offset-4"
								>{$t('register_page.privacy_policy')}</a
							>.
						</span>
					</label>
					{#if $errors.privacy_accept}
						<p class="text-destructive text-sm">{$errors.privacy_accept}</p>
					{/if}

					<label class="flex min-h-11 cursor-pointer items-start gap-3 text-sm">
						<input
							type="checkbox"
							name="tos_accept"
							class="accent-primary mt-0.5 size-5 shrink-0"
							aria-invalid={!!$errors.tos_accept}
						/>
						<span>
							{$t('register_page.agree_tos_prefix')}
							<a href="/docs/tos" class="underline underline-offset-4"
								>{$t('register_page.terms_of_service')}</a
							>.
						</span>
					</label>
					{#if $errors.tos_accept}
						<p class="text-destructive text-sm">{$errors.tos_accept}</p>
					{/if}
				</div>

				<!-- "Forgot password?" was offered on the registration form, which is for
				     people who have no password yet. It lives on the login page, where it is
				     the thing you reach for. -->
				<div class="flex items-center justify-end gap-4">
					<Button type="submit" disabled={!$isValid || $isSubmitting}>
						{#if $isSubmitting}
							<LoaderCircle class="size-4 animate-spin" aria-hidden="true" />
							<span class="sr-only">{$t('words.register')}</span>
						{:else}
							{$t('words.register')}
						{/if}
					</Button>
				</div>
			</form>
		</Card.Content>

		{#if responseData.open}
			{@const ok = responseData.data === '200' || responseData.data === '200_verified'}
			<div class="px-6 pb-2">
				<div
					class="flex gap-3 rounded-lg border p-3 text-sm {ok
						? 'border-border bg-muted/50'
						: 'border-destructive/40 bg-destructive/10'}"
					role="status"
					aria-live="polite"
				>
					{#if ok}
						<CircleCheck
							class="text-foreground mt-0.5 size-4 shrink-0"
							aria-hidden="true"
						/>
					{:else}
						<CircleAlert
							class="text-destructive mt-0.5 size-4 shrink-0"
							aria-hidden="true"
						/>
					{/if}
					<p class={ok ? 'text-foreground' : 'text-destructive'}>
						{#if responseData.data === '200'}
							{$t('register_page.result.check_email')}
						{:else if responseData.data === '200_verified'}
							{$t('register_page.result.ready')}
						{:else if responseData.data === '409'}
							{$t('register_page.result.taken')}
						{:else if responseData.data === '400'}
							{$t('register_page.result.invalid')}
						{:else if responseData.data === '429'}
							{$t('register_page.result.too_many')}
						{:else if responseData.data === '503'}
							{$t('register_page.result.no_mail')}
						{:else if responseData.data === '423'}
							{$t('register_page.result.closed')}
						{:else}
							{$t('register_page.result.failed')}
						{/if}
					</p>
				</div>
			</div>

			{#if responseData.data === '409'}
				<div class="text-muted-foreground px-6 pb-2 text-sm">
					{$t('register_page.taken_hint')}
					<a
						href="/account/resend-verification"
						class="text-primary font-medium underline-offset-4 hover:underline"
						>{$t('register_page.taken_link')}</a
					>.
				</div>
			{/if}

			{#if responseData.data === '200'}
				<div class="text-muted-foreground px-6 pb-2 text-sm">
					{#if resend.result === ''}
						<span>{$t('register_page.resend.prompt')}</span>
						<button
							type="button"
							class="text-primary font-medium underline-offset-4 hover:underline disabled:opacity-50"
							disabled={resend.busy}
							onclick={resendVerification}
						>
							{$t('register_page.resend.action')}
						</button>
					{:else}
						<p role="status" aria-live="polite">
							{#if resend.result === 'sent'}
								{$t('register_page.resend.sent')}
							{:else if resend.result === 'too_many'}
								{$t('register_page.resend.too_many')}
							{:else}
								{$t('register_page.resend.failed')}
							{/if}
						</p>
					{/if}
				</div>
			{/if}
		{/if}

		<Card.Footer class="justify-center gap-1.5 text-sm">
			<span class="text-muted-foreground">{$t('register_page.already_have_account?')}</span>
			<a href={login_href} class="text-primary font-medium underline-offset-4 hover:underline"
				>{$t('words.login')}</a
			>
		</Card.Footer>
	</Card.Root>
</div>
<Footer />
