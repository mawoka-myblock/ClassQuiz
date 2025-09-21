<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	interface Props {
		data: any;
		editor?: boolean;
	}

	let { data = $bindable(), editor = true }: Props = $props();
</script>

{#if editor}
	<textarea bind:value={data} class="w-full h-full dark:text-black resize-none"></textarea>
{:else}
	<p>{data}</p>
{/if}
