<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	import { getLocalization } from '$lib/i18n';
	import { Button } from '$lib/components/ui/button/index.js';
	import BarChart3 from '@lucide/svelte/icons/chart-column';

	const { t } = getLocalization();

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();
</script>

<!-- The table used gray-300/gray-500 borders and had no scroll container, and the
     empty state was one centred sentence stating a fact with nothing to do about it.
     An empty state should say what would fill it and offer the way there. -->
<div class="mx-auto w-full max-w-5xl px-4 py-8">
	<h1 class="mb-6 text-2xl font-bold tracking-tight">{$t('results_page.title')}</h1>

	{#if data.results.length === 0}
		<div class="flex flex-col items-center gap-4 py-16 text-center">
			<span
				class="bg-muted text-muted-foreground flex size-14 items-center justify-center rounded-full"
			>
				<BarChart3 class="size-7" aria-hidden="true" />
			</span>
			<div class="space-y-1">
				<p class="text-lg font-semibold tracking-tight">
					{$t('results_page.no_results_so_far')}
				</p>
				<p class="text-muted-foreground max-w-[42ch] text-sm">
					{$t('results_page.no_results_explanation')}
				</p>
			</div>
			<Button href="/my-quizzes">{$t('results_page.go_to_quizzes')}</Button>
		</div>
	{:else}
		<div class="border-border fq-scroll-x rounded-xl border">
			<table class="w-full text-left text-sm">
				<thead
					class="bg-muted/50 text-muted-foreground text-xs font-medium tracking-wider uppercase"
				>
					<tr>
						<th scope="col" class="px-4 py-3">{$t('results_page.quiz_title')}</th>
						<th scope="col" class="px-4 py-3">{$t('results_page.date_played')}</th>
						<th scope="col" class="px-4 py-3">{$t('results_page.player_count')}</th>
						<th scope="col" class="px-4 py-3">{$t('words.note')}</th>
					</tr>
				</thead>
				<tbody class="divide-border divide-y">
					{#each data.results as result}
						<tr>
							<td class="px-4 py-3">
								<a
									href="/results/{result.id}"
									class="font-medium underline-offset-4 hover:underline"
									>{result.title}</a
								>
							</td>
							<td class="text-muted-foreground px-4 py-3 whitespace-nowrap">
								{new Date(result.timestamp).toLocaleString()}
							</td>
							<td class="px-4 py-3 tabular-nums">{result.player_count}</td>
							<td class="text-muted-foreground px-4 py-3">{result.note ?? ''}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
