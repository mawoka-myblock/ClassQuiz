<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import Footer from '$lib/footer.svelte';
	import { navbarVisible } from '$lib/stores.svelte.ts';
	interface Props {
		children?: import('svelte').Snippet;
	}

	let { children }: Props = $props();

	navbarVisible.visible = true;
</script>

<div class="min-h-screen flex flex-col">
	{@render children?.()}
</div>
<div class="pt-4">
	<Footer />
</div>
