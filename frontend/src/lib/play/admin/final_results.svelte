<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { onMount } from 'svelte';
	import { getLocalization } from '$lib/i18n';
	import { fly, fade } from 'svelte/transition';
	import { cubicOut } from 'svelte/easing';
	import confetti from 'canvas-confetti';
	import Crown from '@lucide/svelte/icons/crown';

	const { t } = getLocalization();

	interface Props {
		data: any;
		username?: any;
		show_final_results: boolean;
	}

	let { data = $bindable(), username, show_final_results }: Props = $props();

	let ranked = $derived(
		Object.keys(data)
			.sort((a, b) => (parseFloat(data[b]) || 0) - (parseFloat(data[a]) || 0))
			.map((name, i) => ({ name, score: parseFloat(data[name]) || 0, place: i + 1 }))
	);

	// Somebody watching this has just played for five minutes; the podium is the payoff,
	// and it was over in two seconds. Kahoot reveals third, then second, then first with
	// a beat between each, and that beat is the whole effect -- a room reacts to each
	// name. 1.4s apart, so the three reveals run about four seconds in total.
	const REVEAL_GAP_MS = 1400;
	const FIRST_REVEAL_MS = 600;
	const winner_lands = FIRST_REVEAL_MS + 2 * REVEAL_GAP_MS + 500;

	// Nobody should be made ill by a results screen. With reduced motion the whole
	// podium is simply there, and no confetti is fired.
	const reduced =
		typeof window !== 'undefined' &&
		window.matchMedia?.('(prefers-reduced-motion: reduce)').matches === true;

	// Podium reads 2nd, 1st, 3rd left to right, the way a real one does.
	let podium = $derived(
		[ranked[1], ranked[0], ranked[2]].filter(Boolean).map((p) => ({
			...p,
			// Fixed pixel heights (h-48/h-36/h-28) made the podium a small object adrift
			// in the middle of a projector screen, and 192 vs 144 vs 112 does not read as
			// a rank order from the back of a room. Viewport-relative so the podium scales
			// with the screen it is thrown on, with a floor for short windows.
			height:
				p.place === 1
					? 'h-[38vh] min-h-44'
					: p.place === 2
						? 'h-[26vh] min-h-32'
						: 'h-[18vh] min-h-24',
			// Built up from last place to first, so the winner lands last.
			delay: reduced ? 0 : FIRST_REVEAL_MS + (3 - p.place) * REVEAL_GAP_MS
		}))
	);
	let runners_up = $derived(ranked.slice(3, 8));
	const medal = (place: number) =>
		place === 1 ? 'is-gold' : place === 2 ? 'is-silver' : 'is-bronze';
	let place_label = (place: number) =>
		place === 1
			? $t('play_page.1st_place')
			: place === 2
				? $t('play_page.2nd_place')
				: $t('play_page.3rd place');

	let canvas: HTMLCanvasElement = $state();
	let winner_shown = $state(reduced);
	onMount(() => {
		const timers = [
			setTimeout(() => (winner_shown = true), reduced ? 0 : winner_lands)
		];
		if (!reduced) {
			// Two bursts rather than one: a single symmetrical puff reads as a graphic,
			// two from the lower corners reads as a room.
			const fire = () => {
				const shoot = confetti.create(canvas, { resize: true, useWorker: true });
				shoot({ particleCount: 140, spread: 70, angle: 60, origin: { x: 0, y: 0.9 } });
				shoot({ particleCount: 140, spread: 70, angle: 120, origin: { x: 1, y: 0.9 } });
			};
			timers.push(setTimeout(fire, winner_lands));
			timers.push(setTimeout(fire, winner_lands + 600));
		}
		return () => timers.forEach(clearTimeout);
	});
</script>

{#if show_final_results}
	<canvas bind:this={canvas} class="pointer-events-none fixed inset-0 z-50 h-full w-full"
	></canvas>

	<div class="fq-stage">
		<!-- The blocks need a floor, or they read as floating cards rather than a
		     podium. border-b-2 border-border was too faint to register as one at
		     projector distance: the blocks looked cut off rather than stood on
		     something. A full-strength rule that runs wider than the blocks reads as
		     ground. -->
		<div
			class="border-foreground/25 flex w-full max-w-4xl items-end justify-center gap-4 border-b-4 px-8 sm:gap-6"
		>
			{#each podium as p (p.name)}
				<div class="flex min-w-0 flex-1 flex-col items-center gap-3">
					<div
						class="flex w-full min-w-0 flex-col items-center gap-0.5 text-center"
						in:fly|global={{ y: -40, duration: 500, delay: p.delay + 150, easing: cubicOut }}
					>
						<!-- The winner gets the one piece of ornament on the screen, and it
						     arrives after their block has landed. -->
						{#if p.place === 1 && winner_shown}
							<span class="crown text-amber-400" in:fade|global={{ duration: 350 }}>
								<Crown class="size-8 sm:size-10" aria-hidden="true" />
							</span>
						{/if}
						<p
							class="fq-answer w-full truncate font-semibold tracking-tight"
							title={p.name}
						>
							{p.name}
						</p>
						<p class="text-sm text-muted-foreground tabular-nums">
							{p.score}
							{$t('words.point', { count: p.score })}
						</p>
					</div>

					<!-- Gold, silver and bronze rather than the theme's primary. The brand has
					     one accent and the rainbow is spent on the wordmark and the answer
					     bars (CLAUDE.md), but a podium is not branding: medal colours are what
					     a podium means, and the winner's block was otherwise a black slab. -->
					<div
						class="podium-block {medal(p.place)} flex w-full {p.height} flex-col items-center
							justify-start gap-1 rounded-t-2xl border border-b-0 border-border pt-3 -mb-[2px]"
						class:is-winner={p.place === 1}
						in:fly|global={{ y: 160, duration: 750, delay: p.delay, easing: cubicOut }}
					>
						<span class="fq-display font-bold tabular-nums">{p.place}</span>
						<span
							class="px-1 text-center text-[0.7rem] font-medium uppercase tracking-wider"
						>
							{place_label(p.place)}
						</span>
					</div>
				</div>
			{/each}
		</div>

		{#if runners_up.length}
			<ul
				class="w-full max-w-md divide-y divide-border overflow-hidden rounded-xl border border-border bg-card"
				in:fade|global={{ duration: 400, delay: reduced ? 0 : winner_lands + 900 }}
			>
				{#each runners_up as p (p.name)}
					<li class="flex items-center gap-3 px-4 py-2.5">
						<span class="w-6 text-sm font-semibold text-muted-foreground tabular-nums"
							>{p.place}</span
						>
						<span class="min-w-0 flex-1 truncate font-medium" title={p.name}
							>{p.name}</span
						>
						<span class="text-sm text-muted-foreground tabular-nums">{p.score}</span>
					</li>
				{/each}
			</ul>
		{/if}
	</div>

	<!-- Not `data[username]`: a player on 0 points is falsy, and lost this line. -->
	{#if username && username in data}
		{@const me = ranked.find((p) => p.name === username)}
		<div class="fixed bottom-0 left-0 mb-6 flex w-full justify-center px-4">
			<div
				class="flex items-center gap-4 rounded-full border border-border bg-card/90 px-5 py-2.5 shadow-lg backdrop-blur"
			>
				<p class="text-sm font-medium tabular-nums">
					{$t('play_page.your_score', { score: data[username] })}
				</p>
				{#if me}
					<span class="h-4 w-px bg-border" aria-hidden="true"></span>
					<p class="text-sm text-muted-foreground tabular-nums">
						{$t('play_page.your_place', { place: me.place })}
					</p>
				{/if}
			</div>
		</div>
	{/if}
{/if}

<style>
	/* Medal colours, not theme tokens: they mean first, second and third everywhere,
	   they are the same in light and dark, and they sit on the quiz author's own
	   background rather than on the app's surface. Ink is near-black on all three --
	   measured at 9.7:1 on the gold, 11.6:1 on the silver and 6.4:1 on the bronze. */
	.podium-block {
		color: #1b1b1f;
		box-shadow: inset 0 1px 0 rgb(255 255 255 / 0.5);
	}

	.podium-block.is-gold {
		background: linear-gradient(to bottom, #ffd969, #e8ab28);
	}

	.podium-block.is-silver {
		background: linear-gradient(to bottom, #e6e9ee, #b8bfc9);
	}

	.podium-block.is-bronze {
		background: linear-gradient(to bottom, #e3a775, #bf7840);
	}

	/* The winner's block is the one thing on this screen that should feel loud. */
	.podium-block.is-winner {
		box-shadow:
			inset 0 1px 0 rgb(255 255 255 / 0.6),
			0 -10px 40px -12px #e8ab28;
	}

	.podium-block :global(span) {
		color: inherit;
	}

	.crown {
		animation: crown-pop 450ms cubic-bezier(0.2, 1.4, 0.4, 1) both;
	}

	@keyframes crown-pop {
		from {
			transform: scale(0.4) translateY(8px);
		}
		to {
			transform: scale(1) translateY(0);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.crown {
			animation: none;
		}
	}
</style>
