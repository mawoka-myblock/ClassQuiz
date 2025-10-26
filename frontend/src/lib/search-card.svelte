<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();
	import ImportedOrNot from '$lib/view_quiz/imported_or_not.svelte';
	let { quiz } = $props();
</script>

<div class="flex justify-center">
	<a href="/view/{quiz.id}" class="h-max w-fit">
		<div class="max-w-md py-4 px-8 bg-white shadow-lg rounded-lg my-20 dark:bg-slate-800">
			<div>
				<div class="flex w-full items-center">
					<h2
						class="text-gray-800 dark:text-gray-200 text-3xl font-semibold truncate pr-2"
					>
						{@html quiz.title}
					</h2>
					<span class="inline-block ml-auto">
						<ImportedOrNot imported={quiz.imported_from_kahoot} />
					</span>
				</div>
				<p
					class="mt-2 text-gray-600 dark:text-gray-300 break-all overflow-hidden text-ellipsis max-h-[4.5rem] block"
				>
					{@html quiz.description}
				</p>
			</div>
			<div class="flex mt-4">
				<span
					>{#if quiz.imported_from_kahoot === true}
						{$t('explore_page.imported_by')}
					{:else}
						{$t('explore_page.made_by')}
					{/if}
					{@html quiz.user}</span
				>
			</div>
		</div>
	</a>
</div>
