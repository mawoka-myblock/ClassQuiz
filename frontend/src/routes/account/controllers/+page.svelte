<script lang="ts">
	import type { PageData } from './$types';
	import BrownButton from '$lib/components/buttons/brown.svelte';

	export let data: PageData;

	console.log(data.controllers);
	const controllers: [] = data.controllers;
</script>

<div class="w-full h-full">
	{#if controllers.length === 0}
		<div class="w-full h-full flex">
			<div class="m-auto">
				<BrownButton>Add new controller</BrownButton>
			</div>
		</div>
	{:else}
		<div class="p-2">
			<table class="w-full">
				<tr class="border-b-2 dark:border-gray-500 text-left border-gray-300">
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300">Name</th>
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
						>Player name</th
					>
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
						>First seen</th
					>
					<th class="border-r dark:border-gray-500 p-1 mx-auto border-gray-300"
						>Last seen</th
					>
					<th class="mx-auto p-1">Version</th>
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
								: 'Never'}</td
						>
						<td class="border-r dark:border-gray-500 p-1 border-gray-300"
							>{controller.last_seen
								? new Date(controller.last_seen).toLocaleString()
								: 'Never'}</td
						>
						<td class="mx-auto p-1">{controller.os_version ?? 'Unknown'}</td>
					</tr>
				{/each}
			</table>
		</div>
	{/if}
</div>
