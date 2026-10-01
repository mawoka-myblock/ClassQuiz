<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import { signedIn, pathname } from '$lib/stores';
	import { beforeNavigate } from '$app/navigation';
	import { slide } from 'svelte/transition';
	import { registration_disabled } from './config';
	import Wordmark from '$lib/components/Wordmark.svelte';
	import ThemeToggle from '$lib/theme-toggle.svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import Menu from '@lucide/svelte/icons/menu';
	import X from '@lucide/svelte/icons/x';
	import { page } from '$app/state';

	const { t } = getLocalization();

	// A real "you are here". Play used to be drawn permanently highlighted, which read
	// as the current page on every page.
	const is_current = (href: string) =>
		page.url.pathname === href || page.url.pathname.startsWith(`${href}/`);
	const nav_class = (href: string) =>
		is_current(href) ? 'btn-nav bg-muted text-foreground' : 'btn-nav';

	// The three surfaces, the same whether or not you are signed in (MVP.md section 1).
	const surfaces = [
		{ href: '/explore', key: 'words.discover' },
		{ href: '/my-quizzes', key: 'words.my_quizzes' },
		{ href: '/play', key: 'words.join' }
	];

	let menuIsClosed = $state(true);
	const toggleMenu = () => {
		menuIsClosed = !menuIsClosed;
	};

	beforeNavigate(() => {
		menuIsClosed = true; // Closes menu to let the user see the page beneath
	});
</script>

<nav
	class="border-border/60 bg-background/80 fixed inset-x-0 top-0 z-30 border-b px-5 py-3 backdrop-blur-xl [clip-path:inset(0)] lg:px-8"
>
	<!-- Desktop navbar -->
	<div class="hidden lg:flex lg:items-center lg:flex-row lg:justify-between">
		<div class="lg:flex lg:items-center lg:flex-row gap-1">
			<a
				href="/"
				class="fq-touch-target text-foreground hover:opacity-80 relative mr-2 flex min-h-11 items-center text-lg transition-opacity"
				aria-label="frogQuiz home"
			>
				<Wordmark />
			</a>
			<!-- Discover is /explore, which also serves /search. -->
			{#each surfaces as s (s.href)}
				<a
					class={nav_class(s.href)}
					href={s.href}
					aria-current={is_current(s.href) ? 'page' : undefined}>{$t(s.key)}</a
				>
			{/each}
			<!-- Docs and GitHub hidden for the MVP (MVP.md §4.2), for signed-out visitors
			     only as before. To bring them back, restore under {#if !$signedIn}:
			     <a class="btn-nav" href="/docs">{$t('words.docs')}</a> and an external link
			     to https://github.com/ogfrench/frogQuiz with the ExternalLink icon. -->
		</div>
		<div class="lg:flex lg:items-center lg:flex-row gap-1">
			{#if $signedIn}
				<a
					class={nav_class('/account/settings')}
					href="/account/settings"
					aria-current={is_current('/account/settings') ? 'page' : undefined}
					>{$t('words.my_account')}</a
				>
				<a class="btn-nav" href="/api/v1/users/logout">{$t('words.logout')}</a>
			{:else}
				<!-- Making a quiz needs no account, so it sits at the same level as Log in
				     rather than below it. Outline, so Log in stays the plainer of the two. -->
				<Button href="/create" variant="outline" size="sm" class="mr-1">
					{$t('index_page.create_cta')}
				</Button>
				<a class="btn-nav" href="/account/login?returnTo={$pathname}">{$t('words.login')}</a
				>
				<!-- Inherited inverted from upstream: this read `{#if registration_disabled}`,
				     so the only sign-up link in the navbar appeared exactly when signing up was
				     turned off. A visitor had to find it on the login page. -->
				{#if !registration_disabled}
					<a class="btn-nav" href="/account/register">{$t('words.register')}</a>
				{/if}
			{/if}

			<div class="fit-content flex items-center justify-center gap-2">
				<div class="lg:flex items-center justify-center">
					<ThemeToggle />
				</div>
			</div>
		</div>
	</div>

	<!-- Mobile navbar -->
	<div class="lg:hidden">
		<!-- Navbar header -->
		<div class="flex items-center justify-between">
			<a
				href="/"
				class="fq-touch-target text-foreground hover:opacity-80 relative mr-2 flex min-h-11 items-center text-lg transition-opacity"
				aria-label="frogQuiz home"
			>
				<Wordmark />
			</a>
			<a class="{nav_class('/play')} flex" href="/play">{$t('words.join')}</a>

			<!-- Dark/Light mode toggle + Open/Close menu -->
			<div class="flex items-center">
				<ThemeToggle />

				{#if menuIsClosed}
					<button
						class="fq-touch-target text-muted-foreground hover:text-foreground hover:bg-muted relative inline-flex size-9 shrink-0 items-center justify-center rounded-md transition-colors"
						id="open-menu"
						onclick={toggleMenu}
						aria-label="Open navbar"
					>
						<Menu class="size-6" aria-hidden="true" />
					</button>
				{:else}
					<button
						class="fq-touch-target text-muted-foreground hover:text-foreground hover:bg-muted relative inline-flex size-9 shrink-0 items-center justify-center rounded-md transition-colors"
						id="close-menu"
						onclick={toggleMenu}
						aria-label="Close navbar"
					>
						<X class="size-6" aria-hidden="true" />
					</button>
				{/if}
			</div>
		</div>

		<!-- Navbar content -->
		{#if !menuIsClosed}
			<div class="flex flex-col" transition:slide|global={{ duration: 400 }}>
				{#each surfaces as s (s.href)}
					<a
						class={nav_class(s.href)}
						href={s.href}
						aria-current={is_current(s.href) ? 'page' : undefined}>{$t(s.key)}</a
					>
				{/each}
				<!-- Docs and GitHub hidden for the MVP; see the desktop navbar above. -->

				<hr class="my-1 border" />
				{#if !$signedIn}
					<Button href="/create" variant="outline" size="sm" class="my-1 justify-center">
						{$t('index_page.create_cta')}
					</Button>
				{/if}
				{#if $signedIn}
					<a class={nav_class('/account/settings')} href="/account/settings"
						>{$t('words.my_account')}</a
					>
					<a class="btn-nav" href="/api/v1/users/logout">{$t('words.logout')}</a>
				{:else}
					<a class="btn-nav" href="/account/login?returnTo={$pathname}"
						>{$t('words.login')}</a
					>
					{#if !registration_disabled}
						<a class="btn-nav" href="/account/register">{$t('words.register')}</a>
					{/if}
				{/if}
			</div>
		{/if}
	</div>
</nav>
