<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->
<script lang="ts">
	import { Dashboard as SvelteDashboard } from '@uppy/svelte';
	import Uppy from '@uppy/core';
	import DropTarget from '@uppy/drop-target';
	import XHRUpload from '@uppy/xhr-upload';
	import ImageEditor from '@uppy/image-editor';
	import Dashboard from '@uppy/dashboard';
	import Compressor from '@uppy/compressor';
	import { fade } from 'svelte/transition';

	// CSS imports
	import '@uppy/core/dist/style.css';
	import '@uppy/dashboard/dist/style.css';
	import '@uppy/drop-target/dist/style.css';
	// import '@uppy/file-input/dist/style.css'
	import '@uppy/image-editor/dist/style.css';
	import type { EditorData } from '../quiz_types';
	import { getLocalization } from '$lib/i18n';
	const { t } = getLocalization();

	export let modalOpen = false;
	export let edit_id: string;
	export let data: EditorData;
	export let selected_question: number;
	export let pow_data;
	export let pow_salt: string;

	console.log(pow_data);
	const uppy = new Uppy()
		.use(DropTarget, {
			target: document.body
		})
		.use(Dashboard)
		.use(ImageEditor, {
			target: Dashboard,
			quality: 0.8
		})
		.use(Compressor, {
			quality: 0.6
		})
		.use(XHRUpload, {
			endpoint: `/api/v1/editor/image?edit_id=${edit_id}&pow_data=${pow_data}`
		});
	const props = {
		inline: true,
		restrictions: {
			maxFileSize: 2_000_000,
			maxNumberOfFiles: 1,
			allowedFileTypes: ['.gif', '.jpg', '.jpeg', '.png', '.svg', '.webp']
		}
	};
	let image_id;
	uppy.on('upload-success', (file, response) => {
		image_id = response.body.id;
		pow_salt = response.body.pow_data;
		console.log(pow_salt, response.body);
		pow_data = undefined;
	});
	uppy.on('complete', (_) => {
		console.log(pow_data);
		if (selected_question === undefined) {
			data.cover_image = `${window.location.origin}/api/v1/storage/download/${image_id}`;
		} else {
			data.questions[
				selected_question
			].image = `${window.location.origin}/api/v1/storage/download/${image_id}`;
		}
		console.log(selected_question, data);

		modalOpen = false;
	});
	console.log(edit_id);
</script>

{#if modalOpen}
	<div
		class="w-full h-full absolute top-0 left-0 bg-opacity-60 z-20 flex justify-center"
		transition:fade
	>
		<div>
			<button
				type="button"
				class="rounded-t-lg bg-black text-white px-1"
				on:click={() => {
					modalOpen = false;
				}}
				>Close
			</button>
			<div>
				<SvelteDashboard {uppy} width="100%" {props} />
			</div>
		</div>
	</div>
{/if}
<div class="flex justify-center w-full pt-10" transition:fade>
	<button
		class="rounded-lg p-4 flex justify-center bg-transparent border-gray-500 border-2 w-1/2 hover:bg-gray-300 dark:hover:bg-gray-600 transition"
		type="button"
		on:click={() => {
			modalOpen = true;
		}}
		><span class="italic">{$t('uploader.add_image')}</span>
		<svg
			class="w-6 h-6 inline-block"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
			xmlns="http://www.w3.org/2000/svg"
		>
			<path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
			/>
		</svg>
	</button>
</div>
