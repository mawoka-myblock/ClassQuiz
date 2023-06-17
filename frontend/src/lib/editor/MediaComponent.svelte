<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->

<script lang="ts">
	import { browser } from '$app/environment';

	export let src: string;
	export let css_classes = 'max-h-64 h-auto w-auto';
	export let muted = true;
	let type: 'img' | 'video' | undefined = undefined;

	const get_media = async () => {
		if (!browser) {
			return;
		}
		const res = await fetch(`/api/v1/storage/info/${src}`);
		const fileType = res.headers.get('Content-Type');
		if (fileType.includes('video')) {
			type = 'video';
		} else {
			type = 'img';
			const data = await fetch(`/api/v1/storage/download/${src}`);
			return {
				data: URL.createObjectURL(await data.blob()),
				alt_text: res.headers.get('X-Alt-Text')
			};
		}
	};
	const update_url = () => {
		media = get_media();
	};
	let media = get_media();
	$: {
		src;
		update_url();
	}
</script>

{#await media}
	<p>Placeholder</p>
{:then data}
	{#if type === 'img'}
		<img src={data.data} alt={data.alt_text ?? 'Not available'} class={css_classes} />
	{:else if type === 'video'}
		<video
			class={css_classes}
			disablepictureinpicture
			x-webkit-airplay="deny"
			controls
			autoplay
			loop
			{muted}
			preload="metadata"
		>
			<source src="/api/v1/storage/download/{src}" />
		</video>
	{:else}
		<p>Unknown media type</p>
	{/if}
{/await}
