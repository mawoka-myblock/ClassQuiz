<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	export let data;
	export let editor = true;
</script>

{#if editor}
	<textarea bind:value={data} class="w-full h-full dark:text-black resize-none" />
{:else}
	<p>{data}</p>
{/if}
