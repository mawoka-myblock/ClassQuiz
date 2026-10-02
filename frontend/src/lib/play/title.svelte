<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import Check from '@lucide/svelte/icons/check';

	interface Props {
		title: string;
		description: string;
		cover_image: string | undefined;
		/** Shown back to the player so they can see the join actually took. */
		username?: string;
	}

	let { title, description, cover_image, username = undefined }: Props = $props();

	const { t } = getLocalization();
</script>

<!-- This is the first thing a player sees after typing their nickname, and it used
     to be the quiz title and nothing else: no confirmation the join worked, no sign
     of their own name, no indication anything was going to happen next. Same failure
     as the blank screen after answering -- a player cannot tell the app from a dead
     connection. It now says they are in, under their own name, and that the host is
     the one holding things up.
     w-screen is 100vw, which includes the scrollbar, and h-screen is the wrong
     number on a phone; both were here. -->
<div class="fq-stage">
	<div class="flex flex-col items-center gap-3 text-center">
		{#if username}
			<span
				class="bg-foreground/5 ring-border flex size-14 items-center justify-center rounded-full ring-1
					motion-safe:animate-in motion-safe:zoom-in-95"
			>
				<Check class="text-foreground/70 size-7" />
			</span>
			<p class="text-lg font-semibold tracking-tight">
				{$t('play_page.youre_in', { username })}
			</p>
		{/if}
		<p class="text-muted-foreground text-sm">{$t('play_page.waiting_for_host')}</p>
		<span class="flex gap-1.5" aria-hidden="true">
			{#each [0, 1, 2] as d}
				<span
					class="waiting-dot bg-foreground/30 h-2 w-2 rounded-full"
					style="animation-delay: {d * 160}ms"
				></span>
			{/each}
		</span>
	</div>

	<div class="flex flex-col items-center gap-3 text-center">
		<!-- Sized down from text-4xl/5xl on 2026-10-02. A player's first need here is the
		     confirmation that they are in; the quiz title is context. At the old size a
		     real title like "Q4 Security Awareness Refresher" ran to three lines on a
		     phone and pushed "You're in" into the corner of the screen it was meant to
		     own. Still the largest thing on the page, no longer the loudest. -->
		<h1 class="max-w-[18ch] text-balance text-2xl font-bold tracking-tight sm:text-4xl">
			{title}
		</h1>
		{#if description}
			<p class="text-muted-foreground max-w-[36ch] text-balance text-base sm:text-lg">
				{description}
			</p>
		{/if}
	</div>

	{#if cover_image}
		<img
			class="max-h-[28vh] w-auto max-w-full rounded-xl object-contain shadow-sm"
			src="/api/v1/storage/download/{cover_image}"
			alt=""
		/>
	{/if}
</div>

<style>
	.waiting-dot {
		animation: waiting-pulse 1.1s ease-in-out infinite;
	}

	@keyframes waiting-pulse {
		0%,
		100% {
			opacity: 0.25;
			transform: translateY(0);
		}
		50% {
			opacity: 0.9;
			transform: translateY(-3px);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.waiting-dot {
			animation: none;
		}
	}
</style>
