<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
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
