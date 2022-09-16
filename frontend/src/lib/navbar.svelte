<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import '@fontsource/marck-script/index.css';
	import { getLocalization } from '$lib/i18n';
	import { signedIn, pathname } from '$lib/stores';
	import { createTippy } from 'svelte-tippy';
	import { browser } from '$app/environment';

	const tippy = createTippy({
		arrow: true,
		animation: 'perspective-subtle',
		placement: 'bottom'
	});

	const { t } = getLocalization();

	let openMenu = true;
	const toggleMenu = () => {
		openMenu = !openMenu;
	};
	let darkMode = false;
	if (browser) {
		darkMode =
			localStorage.theme === 'dark' ||
			(!('theme' in localStorage) &&
				window.matchMedia('(prefers-color-scheme: dark)').matches);
	}

	const switchDarkMode = (on: boolean): void => {
		if (on) {
			localStorage.setItem('theme', 'dark');
		} else {
			localStorage.setItem('theme', 'light');
		}
		window.location.reload();
	};
</script>

<nav
	class="w-screen px-4 lg:px-10 py-2 flex flex-col lg:flex-row lg:items-center fixed backdrop-blur-2xl bg-white/70 shadow-md z-30 top-0"
>
	<section class="w-full lg:w-max grid grid-cols-3 lg:grid-cols-2">
		<a href="/" class="font-black tracking-tight text-xl text-black marck-script link-hover"
			>ClassQuiz</a
		>
		<div class="flex justify-center">
			<a
				class="lg:pl-6 text-lg font-medium lg:px-4 text-gray-600 hover:text-green-600 link-hover"
				href="/play">{$t('words.play')}</a
			>
		</div>
		<div class="flex justify-end">
			<button
				class="lg:hidden dark:text-black"
				id="open-menu"
				on:click={toggleMenu}
				class:hidden={!openMenu}
				aria-label="Open navbar"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="24"
					height="24"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
					stroke-linecap="round"
					stroke-linejoin="round"
					display="block"
					id="TextAlignJustified"
				>
					<path d="M3 6h18M3 12h18M3 18h18" />
				</svg>
			</button>

			<!-- Close menu -->
			<button
				class="hidden dark:text-black"
				id="close-menu"
				class:hidden={openMenu}
				on:click={toggleMenu}
				aria-label="Close navbar"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="14"
					height="14"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="3"
					stroke-linecap="round"
					stroke-linejoin="round"
					display="block"
					id="Cross"
				>
					<path d="M20 20L4 4m16 0L4 20" />
				</svg>
			</button>
		</div>
	</section>

	<ul id="menu-items" class="lg:flex w-full flex-col lg:flex-row" class:hidden={openMenu}>
		{#if $signedIn}
			<li class="py-2">
				<a
					class="text-lg font-medium lg:px-4 text-gray-600 hover:text-green-600 link-hover"
					href="/dashboard">{$t('words.dashboard')}</a
				>
			</li>
			<li class="py-2">
				<a
					class="text-lg font-medium lg:px-4 text-gray-600 hover:text-green-600 link-hover"
					href="/explore">{$t('words.explore')}</a
				>
			</li>
			<li class="py-2">
				<a
					class="text-lg font-medium lg:px-4 text-gray-600 hover:text-green-600 link-hover"
					href="/search">{$t('words.search')}</a
				>
			</li>
			<li class="py-2">
				<a
					class="text-lg font-medium lg:px-4 text-gray-600 hover:text-green-600 link-hover"
					href="/api/v1/users/logout">{$t('words.logout')}</a
				>
			</li>
		{:else}
			<li class="py-2">
				<a
					class="text-lg font-medium lg:px-4 text-gray-600 hover:text-green-600 link-hover"
					href="/account/register">{$t('words.register')}</a
				>
			</li>

			<li class="py-2">
				<a
					class="text-lg font-medium lg:px-4 text-gray-600 hover:text-green-600 link-hover"
					href="/account/login?returnTo={$pathname}">{$t('words.login')}</a
				>
			</li>
			<li class="py-2">
				<a
					class="text-lg font-medium lg:px-4 text-gray-600 hover:text-green-600 link-hover"
					href="/explore">{$t('words.explore')}</a
				>
			</li>
			<li class="py-2">
				<a
					class="text-lg font-medium lg:px-4 text-gray-600 hover:text-green-600 link-hover"
					href="/search">{$t('words.search')}</a
				>
			</li>
			<li class="py-2">
				<a
					class="text-lg font-medium lg:px-4 text-gray-600 hover:text-green-600 link-hover"
					href="https://github.com/mawoka-myblock/classquiz">GitHub</a
				>
			</li>
			<li class="py-2">
				<a
					class="text-lg font-medium lg:px-4 text-gray-600 hover:text-green-600 link-hover"
					href="/docs">{$t('words.docs')}</a
				>
			</li>
		{/if}
	</ul>
	<div
		class="justify-self-end h-full flex justify-center items-center lg:relative fixed right-12 -top-1/2 pt-11 lg:right-0 lg:top-0 lg:p-0"
	>
		{#if darkMode}
			<button
				on:click={() => {
					switchDarkMode(false);
				}}
				use:tippy={{ content: 'Switch light mode on' }}
			>
				<!-- Heroicons: sun -->
				<svg
					class="w-6 h-6 text-black"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						stroke="currentColor"
						d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
					/>
				</svg>
			</button>
		{:else}
			<button
				on:click={() => {
					switchDarkMode(true);
				}}
				use:tippy={{ content: 'Switch dark mode on' }}
			>
				<!-- Heroicons: moon -->
				<svg
					class="w-6 h-6"
					fill="none"
					stroke="currentColor"
					viewBox="0 0 24 24"
					xmlns="http://www.w3.org/2000/svg"
				>
					<path
						stroke-linecap="round"
						stroke-linejoin="round"
						stroke-width="2"
						d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
					/>
				</svg>
			</button>
		{/if}
	</div>
</nav>
