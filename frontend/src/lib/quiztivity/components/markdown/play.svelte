<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { Markdown } from '$lib/quiztivity/types';
	import DOMPurify from 'dompurify';
	import { marked } from 'marked';
	import { browser } from '$app/environment';

	export let data: Markdown | undefined;

	let rendered_html = '';

	$: rendered_html = browser ? DOMPurify.sanitize(marked.parse(data.markdown ?? '')) : '';
</script>

<div class="prose dark:prose-invert">
	{@html rendered_html}
</div>
