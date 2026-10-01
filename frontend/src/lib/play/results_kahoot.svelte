<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import { scale } from 'svelte/transition';
	import { backOut } from 'svelte/easing';
	import { DUR, dur } from '$lib/motion';
	import Check from '@lucide/svelte/icons/check';
	import X from '@lucide/svelte/icons/x';
	import Minus from '@lucide/svelte/icons/minus';

	const { t } = getLocalization();

	function sortObjectbyValue(obj) {
		const ret = {};
		Object.keys(obj)
			.sort((a, b) => obj[b] - obj[a])
			.forEach((s) => (ret[s] = obj[s]));
		return ret;
	}

	interface Props {
		scores: any;
		question_results: Array<{
			username: string;
			answer: string;
			right: boolean;
			time_taken: number;
			score: number;
		}>;
		username: any;
	}

	let { scores = $bindable(), question_results, username }: Props = $props();
	let score_by_username = $state({});

	if (JSON.stringify(scores) === '{}') {
		for (const i of question_results) {
			scores[i.username] = 0;
		}
	}
	for (const i of question_results) {
		score_by_username[i.username] = i.score;
	}
	for (const username of Object.keys(score_by_username)) {
		scores[username] = (score_by_username[username] ?? 0) + (scores[username] ?? 0);
	}
	scores = scores;
	let sorted_scores = $derived(sortObjectbyValue(scores));

	// The screen said "+760" and nothing else, so a player never learned whether they had
	// been right -- and "+0" with no explanation reads as a bug rather than a wrong answer.
	// Everything needed is already in question_results; nothing new crosses the socket.
	const my_result = $derived(question_results.find((r) => r.username === username));
	const answered = $derived(my_result !== undefined);
	const right = $derived(my_result?.right === true);
	const place = $derived(Object.keys(sorted_scores).indexOf(username) + 1);
	const players = $derived(Object.keys(sorted_scores).length);
</script>

<!-- This laid itself out with `h-screen` + `m-auto`, which did two wrong things at
     once: 100vh is the wrong number on a phone, and a second full-height centring
     block inside the route's stage is what left the card visually off-centre with a
     dead half-screen under it. The card now only draws itself and lets the stage
     place it.
     Fixed light "paper" rather than the bg-card token, for the same reason the host
     results card is: it sits on the quiz author's own background colour, not the
     app theme, so in dark mode bg-card made it near-black on near-black. -->
<div
	class="mx-auto flex w-full max-w-xs flex-col items-center gap-3 rounded-2xl border border-neutral-200 bg-white px-8 py-7 text-center text-neutral-900 shadow-sm"
>
	<!-- Shape as well as colour: about one man in twelve cannot tell the green from the
	     red, and this is the one moment of the game that has to land. -->
	<div
		in:scale|global={{ duration: dur(DUR.surface), start: 0.6, easing: backOut }}
		class="flex size-14 items-center justify-center rounded-full {answered
			? right
				? 'bg-emerald-100 text-emerald-700'
				: 'bg-rose-100 text-rose-700'
			: 'bg-neutral-100 text-neutral-500'}"
	>
		{#if !answered}
			<Minus class="size-7" aria-hidden="true" />
		{:else if right}
			<Check class="size-7" aria-hidden="true" />
		{:else}
			<X class="size-7" aria-hidden="true" />
		{/if}
	</div>

	<p
		class="text-2xl font-bold {answered
			? right
				? 'text-emerald-700'
				: 'text-rose-700'
			: 'text-neutral-500'}"
	>
		{#if !answered}
			{$t('play_page.answer_none')}
		{:else if right}
			{$t('play_page.answer_correct')}
		{:else}
			{$t('play_page.answer_wrong')}
		{/if}
	</p>

	<p class="text-4xl font-bold tabular-nums">
		+{score_by_username[username] ?? '0'}
	</p>

	<div class="text-sm text-neutral-500">
		<p class="tabular-nums">{$t('play_page.total_score', { score: sorted_scores[username] ?? 0 })}</p>
		{#if place > 0 && players > 1}
			<p class="tabular-nums">
				{$t('play_page.place_of', { place, total: players })}
			</p>
		{/if}
	</div>
</div>
