<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { PageData } from './$types';
	import { fade } from 'svelte/transition';
	// import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { onMount } from 'svelte';
	import Uploader from './uploader.svelte';
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	export let data: PageData;
	let edit_popup = null;
	const files = data.images;

	const close_popup_handler = (e: Event) => {
		if (e.target !== e.currentTarget) return;
		edit_popup = null;
	};
	onMount(() => {
		window.onkeydown = (e: KeyboardEvent) => {
			if (e.key === 'Escape') {
				edit_popup = null;
			}
		};
	});

	const save_file_metadata = async () => {
		await fetch(`/api/v1/storage/meta/${edit_popup.id}`, {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({ filename: edit_popup.filename, alt_text: edit_popup.alt_text })
		});
		edit_popup = null;
		window.location.reload();
	};

	const delete_file = async (id: string) => {
		await fetch(`/api/v1/storage/meta/${id}`, { method: 'DELETE' });
		window.location.reload();
	};
</script>

<div>
	<h2 class="text-center text-4xl">
		{$t('file_dashboard.storage_usage', {
			used: (data.storage_usage.used / (1024 * 1024)).toFixed(2),
			total: (data.storage_usage.limit / (1024 * 1024)).toFixed(0),
			percent: ((data.storage_usage.used / data.storage_usage.limit) * 100).toFixed(0)
		})}
	</h2>
	<Uploader />
	<div class="grid grid-cols-1 lg:grid-cols-2 p-4 gap-4">
		{#each files as file}
			<div
				class="border-2 border-[#B07156] rounded p-2 grid grid-cols-2 hover:opacity-100 transition-all"
				class:opacity-40={file.quiztivities.length === 0 && file.quizzes.length === 0}
			>
				{#if file.mime_type === 'music/mp3'}
					<svg
						height="15vh"
						width="100%"
						version="1.1"
						id="Layer_1"
						xmlns="http://www.w3.org/2000/svg"
						xmlns:xlink="http://www.w3.org/1999/xlink"
						viewBox="0 0 496.158 496.158"
						xml:space="preserve"
						class="m-auto h-auto w-auto max-h-[15vh]"
					>
						<path
							style="fill:#337180;"
							d="M496.158,248.085c0-137.022-111.068-248.082-248.074-248.082C111.07,0.003,0,111.063,0,248.085
					c0,137.001,111.07,248.07,248.084,248.07C385.09,496.155,496.158,385.086,496.158,248.085z"
						/>
						<g>
							<path
								style="fill:#DFF2F4;"
								d="M73.412,251.075c0,3.313-2.686,6-6,6H56.746c-3.314,0-6-2.687-6-6v-6.5c0-3.313,2.686-6,6-6h10.666
						c3.314,0,6,2.687,6,6V251.075z"
							/>
							<path
								style="fill:#DFF2F4;"
								d="M104.412,266.825c0,3.313-2.686,6-6,6H87.746c-3.314,0-6-2.687-6-6v-37.5c0-3.313,2.686-6,6-6
						h10.666c3.314,0,6,2.687,6,6V266.825z"
							/>
						</g>
						<g>
							<path
								style="fill:#B5E3EA;"
								d="M135.412,274.579c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-53c0-3.313,2.686-6,6-6h10.666
						c3.314,0,6,2.687,6,6V274.579z"
							/>
							<path
								style="fill:#B5E3EA;"
								d="M166.412,290.079c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-84c0-3.313,2.686-6,6-6h10.666
						c3.314,0,6,2.687,6,6V290.079z"
							/>
						</g>
						<g>
							<path
								style="fill:#A3D5E0;"
								d="M197.412,321.079c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-146c0-3.313,2.686-6,6-6
						h10.666c3.314,0,6,2.687,6,6V321.079z"
							/>
							<path
								style="fill:#A3D5E0;"
								d="M228.412,336.579c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-177c0-3.313,2.686-6,6-6
						h10.666c3.314,0,6,2.687,6,6V336.579z"
							/>
						</g>
						<path
							style="fill:#8EC5CE;"
							d="M259.412,383.079c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-270c0-3.313,2.686-6,6-6h10.666
					c3.314,0,6,2.687,6,6V383.079z"
						/>
						<g>
							<path
								style="fill:#A3D5E0;"
								d="M290.412,321.079c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-146c0-3.313,2.686-6,6-6
						h10.666c3.314,0,6,2.687,6,6V321.079z"
							/>
							<path
								style="fill:#A3D5E0;"
								d="M321.412,290.079c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-84c0-3.313,2.686-6,6-6h10.666
						c3.314,0,6,2.687,6,6V290.079z"
							/>
						</g>
						<g>
							<path
								style="fill:#B5E3EA;"
								d="M352.412,305.579c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-115c0-3.313,2.686-6,6-6
						h10.666c3.314,0,6,2.687,6,6V305.579z"
							/>
							<path
								style="fill:#B5E3EA;"
								d="M383.412,274.575c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-53c0-3.313,2.686-6,6-6h10.666
						c3.314,0,6,2.687,6,6V274.575z"
							/>
						</g>
						<g>
							<path
								style="fill:#DFF2F4;"
								d="M445.412,251.261c0,3.314-2.686,6-6,6h-10.666c-3.314,0-6-2.686-6-6v-6.5c0-3.313,2.686-6,6-6
						h10.666c3.314,0,6,2.687,6,6V251.261z"
							/>
							<path
								style="fill:#DFF2F4;"
								d="M414.412,259.079c0,3.313-2.686,6-6,6h-10.666c-3.314,0-6-2.687-6-6v-22c0-3.313,2.686-6,6-6h10.666
						c3.314,0,6,2.687,6,6V259.079z"
							/>
						</g>
					</svg>
				{:else}
					<img
						src="/api/v1/storage/download/{file.id}"
						class="m-auto h-auto w-auto max-h-[30vh]"
						loading="lazy"
						alt={file.alt_text || $t('file_dashboard.not_available')}
					/>
				{/if}
				<div class="flex flex-col my-auto ml-4">
					<p>
						{$t('file_dashboard.size', {
							size: (file.size / (1024 * 1024)).toFixed(2)
						})}
					</p>
					<p>
						{$t('file_dashboard.caption', {
							caption: file.alt_text ?? $t('file_dashboard.missing')
						})}
					</p>
					<p>
						{$t('file_dashboard.filename', {
							filename: file.filename ?? $t('file_dashboard.missing')
						})}
					</p>
					<p>
						{$t('file_dashboard.type', {
							type: file.mime_type ?? $t('file_dashboard.missing')
						})}
					</p>
					<p>
						{$t('file_dashboard.uploaded', {
							date: new Date(file.uploaded_at).toLocaleString()
						})}
					</p>
					<p>
						{$t('file_dashboard.imported', {
							yes_or_no: file.imported ? $t('words.yes') : $t('words.no')
						})}
					</p>
					<div class="flex flex-col gap-2">
						<BrownButton
							on:click={() => {
								edit_popup = file;
							}}
							>{$t('file_dashboard.edit_details')}
						</BrownButton>
						<BrownButton
							on:click={() => {
								delete_file(file.id);
							}}>{$t('file_dashboard.delete_file')}</BrownButton
						>
					</div>
				</div>
			</div>
		{/each}
	</div>
</div>

{#if edit_popup}
	<div
		transition:fade|local={{ duration: 100 }}
		class="fixed top-0 left-0 h-screen w-screen z-40 flex bg-black bg-opacity-50"
		on:click={close_popup_handler}
	>
		<div class="w-auto h-auto m-auto rounded bg-white dark:bg-gray-700 p-4">
			<h1 class="text-2xl text-center">{$t('file_dashboard.edit_the_file')}</h1>
			<form class="flex flex-col" on:submit|preventDefault={save_file_metadata}>
				<div class="flex flex-row">
					<div class="flex flex-col mr-4">
						<label for="name" class="m-auto">{$t('file_dashboard.filename_word')}</label
						>
						<label for="alt_text" class="m-auto">{$t('file_dashboard.alt_text')}</label>
					</div>
					<div class="flex flex-col gap-3">
						<input
							class="rounded outline-none dark:bg-gray-500 p-0.5 border-4 border-transparent"
							id="name"
							type="text"
							bind:value={edit_popup.filename}
						/>
						<input
							class:border-red-700={!edit_popup.alt_text}
							class="transition rounded outline-none dark:bg-gray-500 p-0.5 border-4 border-transparent"
							id="alt_text"
							type="text"
							bind:value={edit_popup.alt_text}
						/>
					</div>
				</div>
				<div class="mt-4">
					<BrownButton type="submit">{$t('words.save')}</BrownButton>
				</div>
			</form>
		</div>
	</div>
{/if}
