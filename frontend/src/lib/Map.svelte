<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { browser } from '$app/environment';
	import { Map, Marker } from '@beyonk/svelte-mapbox';

	export let lng: number;
	export let lat: number;
	export let markerText: string;
	export let zoom = 12;
	let center: [number, number];
	$: center = [lng, lat];
</script>

{#if browser}
	<Map accessToken={import.meta.env.VITE_MAPBOX_ACCESS_TOKEN} bind:center bind:zoom>
		<Marker bind:lat bind:lng bind:label={markerText} />
	</Map>
{/if}
