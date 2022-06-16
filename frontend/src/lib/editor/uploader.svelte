<script lang="ts">
	import { Dashboard as SvelteDashboard } from '@uppy/svelte';
	import Uppy from '@uppy/core';
	import DropTarget from '@uppy/drop-target';
	import XHRUpload from '@uppy/xhr-upload';
	import ImageEditor from '@uppy/image-editor';
	import Dashboard from '@uppy/dashboard';
	import Compressor from '@uppy/compressor';

	// CSS imports
	import '@uppy/core/dist/style.css';
	import '@uppy/dashboard/dist/style.css';
	import '@uppy/drop-target/dist/style.css';
	// import '@uppy/file-input/dist/style.css'
	import '@uppy/image-editor/dist/style.css';
	import type { EditorData } from '../quiz_types';

	export let modalOpen = false;
	export let edit_id: string;
	export let data: EditorData;
	export let selected_question: number;

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
			endpoint: `/api/v1/editor/image?edit_id=${edit_id}`
		});
	const props = { inline: true };
	let image_id;
	uppy.on('upload-success', (file, response) => {
		image_id = response.body.id;
	});
	uppy.on('complete', (res) => {
		data.questions[
			selected_question
		].image = `https://${window.location.hostname}/api/v1/storage/download/${image_id}`;
		modalOpen = false;
	});
	console.log(edit_id);
</script>

{#if modalOpen}
	<div class="w-full h-full absolute top-0 left-0 bg-opacity-60 z-20 flex justify-center">
		<div>
			<button
				type="button"
				on:click={() => {
					modalOpen = false;
				}}>Close</button
			>
			<div>
				<SvelteDashboard {uppy} width="100%" {props} />
			</div>
		</div>
	</div>
{:else}
	<button
		on:click={() => {
			modalOpen = true;
		}}>Add Image</button
	>
{/if}
