<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	interface Props {
		hovering: boolean;
		children?: import('svelte').Snippet<[any]>;
	}

	let { hovering = $bindable(), children }: Props = $props();

	function enter() {
		hovering = true;
	}

	function leave() {
		hovering = false;
	}
</script>

<div onmouseenter={enter} onmouseleave={leave}>
	{@render children?.({ hovering, })}
</div>
