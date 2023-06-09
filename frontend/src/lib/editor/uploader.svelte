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
	import { onMount } from 'svelte';

	const { t } = getLocalization();

	export let modalOpen = false;
	export let edit_id: string;
	export let data: EditorData;
	export let selected_question: number;
	export let video_upload = false;

	// eslint-disable-next-line no-undef
	let video_popup: undefined | WindowProxy = undefined;

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
			endpoint: `/api/v1/storage/`
		});
	const props = {
		inline: true,
		restrictions: {
			maxFileSize: 10_490_000,
			maxNumberOfFiles: 1,
			allowedFileTypes: ['image/*']
			// allowedFileTypes: ['.gif', '.jpg', '.jpeg', '.png', '.svg', '.webp']
		}
	};
	let image_id;
	uppy.on('upload-success', (file, response) => {
		image_id = response.body.id;
	});
	uppy.on('complete', (_) => {
		if (selected_question === undefined) {
			data.cover_image = image_id;
		} else if (selected_question === -1) {
			data.background_image = image_id;
		} else {
			data.questions[selected_question].image = image_id;
		}
		console.log(selected_question, data);

		modalOpen = false;
	});
	console.log(edit_id);

	onMount(() => {
		window.addEventListener('storage', (e) => {
			if (e.key !== 'video_upload_id') {
				return;
			}
			localStorage.removeItem('video_upload_id');
			data.questions[selected_question].image = e.newValue;
		});
	});

	const upload_video = async () => {
		video_popup = window.open(
			'/edit/videos',
			'_blank',
			'popup=true,toolbar=false,menubar=false,location=false,'
		);
		video_popup.addEventListener('beforeunload', () => {
			console.log('Unloaded');
			video_popup = undefined;
		});
	};
</script>

{#if modalOpen}
	<div
		class="w-full h-full absolute top-0 left-0 bg-opacity-60 z-20 flex justify-center"
		transition:fade|local
	>
		<div>
			<div>
				<button
					type="button"
					class="rounded-t-lg bg-black text-white px-1"
					on:click={() => {
						modalOpen = false;
					}}
					>Close
				</button>
				{#if video_upload}
					<button
						class="rounded-t-lg bg-black text-white px-1"
						on:click={upload_video}
						type="button"
						>Upload video
					</button>
				{/if}
			</div>
			{#if video_popup}
				<div class="flex w-full h-1/3 bg-white dark:bg-gray-700 p-4">
					<h2 class="text-4xl m-auto">Popup open</h2>
				</div>
			{:else}
				<div>
					<SvelteDashboard {uppy} width="100%" {props} />
				</div>
			{/if}
		</div>
	</div>
{/if}
<div class="flex justify-center w-full pt-10" transition:fade|local>
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
