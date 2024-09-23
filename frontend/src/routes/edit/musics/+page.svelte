<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { navbarVisible } from '$lib/stores';
	import { getLocalization } from '$lib/i18n';
	const { t } = getLocalization();

	let file_input: HTMLInputElement;
	navbarVisible.set(false);

	let stats: { progress: number; time_elapsed: number; speed: number } = {
		progress: 0,
		time_elapsed: 0,
		speed: 0
	};

	let upload_stats: { progress: number; upload_started: undefined | Date; time_elapsed: number } =
		{
			progress: 0,
			upload_started: undefined,
			time_elapsed: 0
		};

	const speed_extraction_regex = /speed=(\d+\.\d+)x(?![\s\S]*speed=\d+\.\d+x)/;
	let last_time_elapsed = 0;

	// eslint-disable-next-line no-unused-vars
	enum Status {
		// eslint-disable-next-line no-unused-vars
		Idle,
		// eslint-disable-next-line no-unused-vars
		Compressing,
		// eslint-disable-next-line no-unused-vars
		CompressDone,
		// eslint-disable-next-line no-unused-vars
		Uploading,
		// eslint-disable-next-line no-unused-vars
		Done
	}

	let status: Status = Status.Idle;

	let file_size_in_mi: undefined | number = undefined;
	let original_file_size_in_mi: undefined | number = undefined;
	let file: File;
	let file_data: undefined | Blob = undefined;

	const compress_music = async () => {
		if (status !== Status.Idle) {
			return;
		}
		status = Status.Compressing;
		file = file_input.files[0];
		original_file_size_in_mi = file.size / 1_048_576;
		file_size_in_mi = file.size / 1_048_576;
		file_data = file;
		status = Status.CompressDone;
		stats.progress = 1;
	};

	const upload_music = async () => {
		status = Status.Uploading;
		upload_stats.upload_started = new Date();
		const xhr = new XMLHttpRequest();
		const success = await new Promise((resolve) => {
			xhr.upload.addEventListener('progress', (event) => {
				if (event.lengthComputable) {
					upload_stats.progress = event.loaded / event.total;
					upload_stats.time_elapsed = (new Date() - upload_stats.upload_started) / 1000;
				}
			});
			xhr.addEventListener('loadend', () => {
				resolve({
					success: xhr.readyState === 4 && xhr.status === 200,
					body: xhr.responseText
				});
			});
			xhr.open('POST', `/api/v1/storage/raw/${file.name}`, true);
			xhr.setRequestHeader('Content-Type', 'music/mp3');
			xhr.send(file_data);
		});
		console.log('success:', success);
		const json = JSON.parse(success.body);
		localStorage.setItem('music_upload_id', json.id);
		console.log(json, 'done');
		status = Status.Done;
		window.close();
	};
</script>

<div class="w-screen h-screen m-auto flex flex-col dark:bg-gray-700 p-2 bg-white">
	<input type="file" bind:this={file_input} class="m-auto" accept="music/mp3" />
	<div class="mt-auto flex justify-center">
		{#if status === Status.Compressing || status === Status.CompressDone}
			<table>
				<tr>
					<th>{$t('words.speed')}</th>
					<th>{$t('words.progress')}</th>
					<th>{$t('music_uploader.time_elapsed')}</th>
					<th>{$t('music_uploader.time_remaining')}</th>
				</tr>
				<tr>
					<td>{stats.speed}</td>
					<td>{Math.round(stats.progress * 100)}%</td>
					<td>{upload_stats.time_elapsed.toFixed(2)}s</td>
					<td
						>{(stats.time_elapsed / stats.progress - upload_stats.time_elapsed).toFixed(
							2
						)}s</td
					>
				</tr>
			</table>
		{:else if status === Status.Uploading}
			<table>
				<tr>
					<th>{$t('words.progress')}</th>
					<th>{$t('music_uploader.time_elapsed')}</th>
					<th>{$t('music_uploader.time_remaining')}</th>
				</tr>
				<tr>
					<td>{Math.round(upload_stats.progress * 100)}%</td>
					<td>{stats.time_elapsed.toFixed(2)}s</td>
					<td>{(stats.time_elapsed / stats.progress - stats.time_elapsed).toFixed(2)}s</td
					>
				</tr>
			</table>
		{/if}
	</div>
	<div class="flex relative my-2">
		<div class="w-full">
			<BrownButton disabled={status !== Status.CompressDone} on:click={upload_music}>
				{$t('words.upload')}
				{file_size_in_mi ? `(${file_size_in_mi.toFixed(2)} Mi)` : ''}</BrownButton
			>
		</div>
		<span
			class="h-full transition-all absolute rounded bg-black bg-opacity-50"
			style="width: {100 - stats.progress * 100}%"
		/>
	</div>
	<div class="flex justify-center">
		<BrownButton on:click={compress_music} disabled={status !== Status.Idle}
			>{$t('words.submit')}</BrownButton
		>
	</div>
</div>
