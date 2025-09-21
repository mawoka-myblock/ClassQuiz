<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { navbarVisible} from '$lib/stores.svelte.ts';
	interface Props {
		children?: import('svelte').Snippet;
	}

	let { children }: Props = $props();

	navbarVisible.visible= true;
</script>

{@render children?.()}
