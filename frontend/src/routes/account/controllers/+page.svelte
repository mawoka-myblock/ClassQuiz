<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { getLocalization } from '$lib/i18n';
	const { t } = getLocalization();
	export let data: PageData;

	const controllers: [] = data.controllers;
</script>

<div class="w-full h-full">
	{#if controllers.length === 0}
		<div class="w-full h-full flex">
			<div class="m-auto">
				<BrownButton href="/account/controllers/add"
					>{$t('controllers.add_new_controller')}</BrownButton
				>
			</div>
		</div>
	{:else}
		<div class="p-2">
			<div class="flex">
				<div class="mx-auto">
					<BrownButton href="/account/controllers/add"
						>{$t('controllers.add_new_controller')}</BrownButton
					>
				</div>
			</div>
			<table class="w-full">
				<tr class="border-b-2 dark:border-gray-500 text-left border-gray-300">
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
						>{$t('words.name')}</th
					>
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
						>{$t('controllers.player_name')}
					</th>
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
						>{$t('controllers.first_seen')}
					</th>
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
						>{$t('controllers.last_seen')}
					</th>
					<th class="mx-auto p-1">{$t('words.version')}</th>
				</tr>
				{#each data.controllers as controller}
					<tr class="text-left">
						<td class="border-r dark:border-gray-500 p-1 border-gray-300"
							><a
								href="/account/controllers/{controller.id}"
								class="underline text-lg">{controller.name}</a
							></td
						>
						<td class="border-r dark:border-gray-500 p-1 border-gray-300"
							>{controller.player_name}</td
						>
						<td class="border-r dark:border-gray-500 p-1 border-gray-300"
							>{controller.first_seen
								? new Date(controller.first_seen).toLocaleString()
								: $t('words.never')}</td
						>
						<td class="border-r dark:border-gray-500 p-1 border-gray-300"
							>{controller.last_seen
								? new Date(controller.last_seen).toLocaleString()
								: $t('words.never')}</td
						>
						<td class="mx-auto p-1">{controller.os_version ?? $t('words.unknown')}</td>
					</tr>
				{/each}
			</table>
		</div>
	{/if}
</div>
