<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { FFmpeg } from '@ffmpeg/ffmpeg';
	import { fetchFile } from '@ffmpeg/util';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { navbarVisible } from '$lib/stores.svelte.ts';
	import { getLocalization } from '$lib/i18n';
	const { t } = getLocalization();

	let file_input: HTMLInputElement = $state();
	navbarVisible.visible = false;

	let stats: { progress: number; time_elapsed: number; speed: number } = $state({
		progress: 0,
		time_elapsed: 0,
		speed: 0
	});

	let upload_stats: { progress: number; upload_started: undefined | Date; time_elapsed: number } =
		$state({
			progress: 0,
			upload_started: undefined,
			time_elapsed: 0
		});

	const speed_extraction_regex = /speed=(\d+\.\d+)x(?![\s\S]*speed=\d+\.\d+x)/;

	const time_remaining = (time_elapsed: number, progress: number): string => {
		if (progress <= 0) {
			return '-';
		}
		return `${(time_elapsed / progress - time_elapsed).toFixed(2)}s`;
	};

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

	let status: Status = $state(Status.Idle);

	let file_size_in_mi: undefined | number = $state(undefined);
	let original_file_size_in_mi: undefined | number = undefined;
	let file_data: undefined | Blob = undefined;
	let error_message: undefined | string = $state(undefined);

	// Fixed names inside ffmpeg's own file system, so a file called "out.mp4" can't clash.
	const input_name = 'input.mp4';
	const output_name = 'output.mp4';

	// The server refuses an upload when the storage is full, but it answers before the whole
	// file has arrived, and with a big file the browser often can't read that answer.
	const storage_is_full = async (): Promise<boolean> => {
		try {
			const response = await fetch('/api/v1/storage/limit');
			return response.ok && (await response.json()).limit_reached === true;
		} catch {
			return false;
		}
	};

	const compress_video = async () => {
		if (status !== Status.Idle) {
			return;
		}
		const file = file_input.files?.[0];
		if (!file) {
			error_message = $t('video_uploader.choose_file');
			return;
		}
		error_message = undefined;
		status = Status.Compressing;
		// Compressing can take minutes, so don't start if the upload would be refused anyway.
		if (await storage_is_full()) {
			status = Status.Idle;
			error_message = $t('video_uploader.storage_full');
			return;
		}
		const compression_started = Date.now();
		const ffmpeg = new FFmpeg();
		original_file_size_in_mi = file.size / 1_048_576;
		ffmpeg.on('log', ({ message }) => {
			// Most log lines carry no speed; keep the last one that did.
			const speed_match = message.match(speed_extraction_regex);
			if (speed_match) {
				stats.speed = parseFloat(speed_match[1]);
			}
		});
		ffmpeg.on('progress', (p) => {
			// ffmpeg.wasm: only accurate if input and output have the same length,
			// so keep it between 0 and 1.
			stats.progress = Math.min(Math.max(p.progress ?? 0, 0), 1);
			stats.time_elapsed = (Date.now() - compression_started) / 1000;
		});
		try {
			await ffmpeg.load({
				// log: true,
			});
			await ffmpeg.writeFile(input_name, await fetchFile(file));
			const exit_code = await ffmpeg.exec([
				'-i',
				input_name,
				'-vcodec',
				'libx264',
				'-crf',
				'20',
				'-vf',
				'scale=1080:-2',
				output_name
			]);
			if (exit_code !== 0) {
				throw new Error(`ffmpeg exited with code ${exit_code}`);
			}
			const data = await ffmpeg.readFile(output_name);
			file_size_in_mi = data.length / 1_048_576;
			file_data = new Blob([data]);
			status = Status.CompressDone;
			stats.progress = 1;
		} catch (e) {
			console.error('Video compression failed', e);
			stats = { progress: 0, time_elapsed: 0, speed: 0 };
			status = Status.Idle;
			error_message = $t('video_uploader.compression_failed');
		} finally {
			ffmpeg.terminate();
		}
	};

	const upload_video = async () => {
		if (status !== Status.CompressDone || !file_data) {
			return;
		}
		error_message = undefined;
		status = Status.Uploading;
		upload_stats.progress = 0;
		upload_stats.time_elapsed = 0;
		upload_stats.upload_started = new Date();
		/*        const progressTrackingStream = new TransformStream({
            transform(chunk, controller) {
                controller.enqueue(chunk);
                bytesUploaded += chunk.byteLength;
                console.log("upload progress:", bytesUploaded / totalBytes);
                upload_stats.progress = bytesUploaded / totalBytes;
                upload_stats.time_elapsed = (new Date() - upload_stats.upload_started) / 1000;
            },
            flush(_controller) {
                console.log("completed stream");
            }
        });*/
		/*        const response = await fetch("/api/v1/storage/raw", {
                    method: "POST",
                    headers: {
                        "Content-Type": "video/mp4"
                    },
                    body: file_data.stream().pipeThrough(progressTrackingStream),
                    duplex: "half"
                });
                const json = await response.json()*/
		const xhr = new XMLHttpRequest();
		const response: { status: number; body: string } = await new Promise((resolve) => {
			xhr.upload.addEventListener('progress', (event) => {
				if (event.lengthComputable) {
					upload_stats.progress = event.loaded / event.total;
					upload_stats.time_elapsed = (new Date() - upload_stats.upload_started) / 1000;
				}
			});
			xhr.addEventListener('loadend', () => {
				resolve({ status: xhr.status, body: xhr.responseText });
			});
			xhr.open('POST', '/api/v1/storage/raw', true);
			xhr.setRequestHeader('Content-Type', 'video/mp4');
			xhr.send(file_data);
		});
		let video_id: undefined | string = undefined;
		if (response.status === 200) {
			try {
				video_id = JSON.parse(response.body).id;
			} catch {
				video_id = undefined;
			}
		}
		if (!video_id) {
			// Without an id there is nothing to attach; stay here so the user can try again.
			if (response.status === 413) {
				error_message = $t('video_uploader.too_large');
			} else if (response.status === 409 || (await storage_is_full())) {
				error_message = $t('video_uploader.storage_full');
			} else {
				error_message = $t('video_uploader.upload_failed');
			}
			status = Status.CompressDone;
			return;
		}
		localStorage.setItem('video_upload_id', video_id);
		status = Status.Done;
		window.close();
	};
</script>

<div class="w-screen h-screen m-auto flex flex-col dark:bg-gray-700 p-2 bg-white">
	<input type="file" bind:this={file_input} class="m-auto" accept="video/mp4" />
	<div class="mt-auto flex justify-center">
		{#if status === Status.Compressing || status === Status.CompressDone}
			<table class="border-separate border-spacing-x-4 text-center">
				<thead>
					<tr>
						<th>{$t('words.speed')}</th>
						<th>{$t('words.progress')}</th>
						<th>{$t('video_uploader.time_elapsed')}</th>
						<th>{$t('video_uploader.time_remaining')}</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td>{stats.speed}</td>
						<td>{Math.round(stats.progress * 100)}%</td>
						<td>{stats.time_elapsed.toFixed(2)}s</td>
						<td>{time_remaining(stats.time_elapsed, stats.progress)}</td>
					</tr></tbody
				>
			</table>
		{:else if status === Status.Uploading}
			<table class="border-separate border-spacing-x-4 text-center">
				<thead>
					<tr>
						<th>{$t('words.progress')}</th>
						<th>{$t('video_uploader.time_elapsed')}</th>
						<th>{$t('video_uploader.time_remaining')}</th>
					</tr>
				</thead>
				<tbody>
					<tr>
						<td>{Math.round(upload_stats.progress * 100)}%</td>
						<td>{upload_stats.time_elapsed.toFixed(2)}s</td>
						<td>{time_remaining(upload_stats.time_elapsed, upload_stats.progress)}</td>
					</tr>
				</tbody>
			</table>
		{/if}
	</div>
	{#if error_message}
		<p class="mt-2 text-center font-semibold text-red-600 dark:text-red-300" role="alert">
			{error_message}
		</p>
	{/if}
	<div class="flex relative my-2">
		<div class="w-full">
			<BrownButton disabled={status !== Status.CompressDone} onclick={upload_video}>
				{$t('words.upload')}
				{file_size_in_mi ? `(${file_size_in_mi.toFixed(2)} Mi)` : ''}</BrownButton
			>
		</div>
		<span
			class="h-full transition-all absolute rounded-sm bg-black/50"
			style="width: {100 - stats.progress * 100}%"
		></span>
	</div>
	<div class="flex justify-center">
		<BrownButton onclick={compress_video} disabled={status !== Status.Idle}
			>{$t('words.submit')}</BrownButton
		>
	</div>
</div>
