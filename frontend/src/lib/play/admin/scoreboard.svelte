<!--
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { flip } from 'svelte/animate';
	import { fly } from 'svelte/transition';
	import { getLocalization } from '$lib/i18n';
	import { DUR, dur, stagger } from '$lib/motion';
	import ChevronUp from '@lucide/svelte/icons/chevron-up';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import Minus from '@lucide/svelte/icons/minus';

	const { t } = getLocalization();

	interface Props {
		/** Running totals, already including this question. */
		data: Record<string, number>;
		/** This question's results, for the points each player just gained. */
		new_data: Array<{ username: string; score: number }>;
	}

	let { data, new_data }: Props = $props();

	const gained = $derived(
		Object.fromEntries((new_data ?? []).map((r) => [r.username, r.score ?? 0]))
	);

	const ranked = $derived(
		Object.keys(data ?? {})
			.sort((a, b) => (Number(data[b]) || 0) - (Number(data[a]) || 0))
			.map((name, i) => ({ name, score: Number(data[name]) || 0, place: i + 1 }))
	);

	// Where each player stood before this question's points landed. Movement is the thing
	// a scoreboard is for: a number that only goes up says nothing about the race.
	const previous = $derived(
		Object.keys(data ?? {})
			.map((name) => ({ name, before: (Number(data[name]) || 0) - (gained[name] ?? 0) }))
			.sort((a, b) => b.before - a.before)
			.map((p, i) => [p.name, i + 1] as const)
	);
	const place_before = $derived(Object.fromEntries(previous));

	// Kahoot shows five. More than that stops being readable across a room, and the rest
	// of the field is on the spreadsheet and on each player's own screen.
	const top = $derived(ranked.slice(0, 5));
	const rest = $derived(ranked.length - top.length);
</script>

<!-- The standings on a screen of their own, between the answers and the next question --
     the step the host advances into. It is read from the back of a room, so it is set
     for that: five rows, big type, and the movement spelled out. -->
<div class="fq-stage">
	<div
		class="w-full max-w-2xl overflow-hidden rounded-2xl border border-neutral-200 bg-white text-neutral-900 shadow-sm lg:max-w-4xl"
	>
		<h2
			class="border-b border-neutral-200 bg-neutral-100 px-6 py-3 text-center text-sm font-semibold tracking-wider uppercase lg:text-base"
		>
			{$t('admin_page.scoreboard')}
		</h2>
		<ul class="divide-y divide-neutral-200">
			{#each top as player (player.name)}
				{@const moved = (place_before[player.name] ?? player.place) - player.place}
				<li
					class="flex items-center gap-4 px-6 py-3 lg:gap-6 lg:py-4"
					animate:flip={{ duration: dur(DUR.stage) }}
				>
					<span class="w-8 text-xl font-bold tabular-nums lg:w-12 lg:text-3xl">
						{player.place}
					</span>
					<span class="min-w-0 flex-1 truncate text-lg font-medium lg:text-3xl">
						{player.name}
					</span>
					<!-- Up, down or held. Shape as well as direction, so it does not rest on
					     a colour nobody can see from four metres away. -->
					<span
						class="flex w-10 shrink-0 items-center justify-center text-neutral-500"
						aria-label={moved > 0
							? $t('admin_page.moved_up', { count: moved })
							: moved < 0
								? $t('admin_page.moved_down', { count: -moved })
								: $t('admin_page.held_place')}
					>
						{#if moved > 0}
							<ChevronUp class="size-5 lg:size-7" />
						{:else if moved < 0}
							<ChevronDown class="size-5 lg:size-7" />
						{:else}
							<Minus class="size-4 lg:size-5" />
						{/if}
					</span>
					<span class="w-20 text-right text-lg font-semibold tabular-nums lg:w-28 lg:text-3xl">
						{player.score}
					</span>
					<span
						class="w-16 text-right text-sm tabular-nums lg:w-24 lg:text-xl"
						class:text-neutral-400={!gained[player.name]}
						in:fly|global={{ x: 40, duration: dur(DUR.surface), delay: stagger(player.place, 60) }}
					>
						+{gained[player.name] ?? 0}
					</span>
				</li>
			{/each}
		</ul>
		{#if rest > 0}
			<p class="border-t border-neutral-200 px-6 py-2.5 text-center text-sm text-neutral-500">
				{$t('admin_page.and_more_players', { count: rest })}
			</p>
		{/if}
	</div>
</div>
