<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
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
