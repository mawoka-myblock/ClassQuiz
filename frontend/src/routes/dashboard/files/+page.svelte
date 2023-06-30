<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	// import FileDahboard from "$lib/files/dashboard.svelte"
	// import { thumbHashToDataURL } from 'thumbhash';

	export let data: PageData;
	const files = data.files;

	/*	const base64ToBytes = (value: string) => {
		const base64 = value.replace(/-/g, '+').replace(/_/g, '/');

		const decodedData =
			typeof Buffer !== 'undefined'
				? Buffer.from(base64, 'base64')
				: Uint8Array.from(atob(base64), (char) => char.charCodeAt(0));

		return new Uint8Array(decodedData);
	};*/
	// let images_loaded = [];
</script>

<div class="w-full h-full">
	<div class="grid grid-cols-2 w-full h-full gap-4">
		{#each files as file, i}
			<div class="w-full h-full flex" />
		{/each}
	</div>
</div>
