<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Markdown } from '$lib/quiztivity/types';
	import { marked } from 'marked';
	import { browser } from '$app/environment';

	export let data: Markdown | undefined;

	if (!data) {
		data = {
			markdown: ''
		};
	}

	let rendered_html = '';

	$: rendered_html = browser ? marked.parse(data.markdown) : '';
</script>

<div class="w-full h-[70vh] flex flex-row p-4 gap-4">
	<textarea
		class="w-full resize-none border-[#B07156] border-2 rounded outline-none p-2 bg-opacity-30 bg-white dark:placeholder-gray-300"
		bind:value={data.markdown}
		placeholder="Enter your markdown here!"
	/>
	<div class="w-full">
		<div
			class="aspect-video prose max-w-none border-[#B07156] border-2 rounded p-2 dark:prose-invert"
		>
			{@html rendered_html}
		</div>
	</div>
</div>
