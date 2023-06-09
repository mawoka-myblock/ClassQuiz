<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->

<script lang="ts">
	export let src: string;
	let type: 'img' | 'video' | undefined = undefined;

	const get_media = async () => {
		const res = await fetch(src, { method: 'HEAD' });
		const fileType = res.headers.get('Content-Type');
		console.log(fileType, 'fileType');
		if (fileType.includes('video')) {
			console.log('Setting type to video');
			type = 'video';
		} else {
			type = 'img';
			console.log(res);
			return {
				data: URL.createObjectURL(await res.blob()),
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
		<img src={data.data} alt={data.alt_text ?? 'Not available'} />
	{:else if type === 'video'}
		<p>Video!</p>
		<video
			disablepictureinpicture
			disableremoteplayback
			x-webkit-airplay="deny"
			loop
			preload="metadata"
		>
			<source {src} />
		</video>
	{:else}
		<p>Unknown media type</p>
	{/if}
{/await}
