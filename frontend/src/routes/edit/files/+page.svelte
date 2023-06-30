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
	const images = data.images;

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

	const save_image_metadata = async () => {
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

	const delete_image = async (id: string) => {
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
		{#each images as image}
			<div
				class="border-2 border-[#B07156] rounded p-2 grid grid-cols-2 hover:opacity-100 transition-all"
				class:opacity-40={image.quiztivities.length === 0 && image.quizzes.length === 0}
			>
				<img
					src="/api/v1/storage/download/{image.id}"
					class="m-auto h-auto w-auto max-h-[30vh]"
					loading="lazy"
					alt={image.alt_text || $t('file_dashboard.not_available')}
				/>
				<div class="flex flex-col my-auto ml-4">
					<p>
						{$t('file_dashboard.size', {
							size: (image.size / (1024 * 1024)).toFixed(2)
						})}
					</p>
					<p>
						{$t('file_dashboard.caption', {
							caption: image.alt_text ?? $t('file_dashboard.missing')
						})}
					</p>
					<p>
						{$t('file_dashboard.filename', {
							filename: image.filename ?? $t('file_dashboard.missing')
						})}
					</p>
					<p>
						{$t('file_dashboard.uploaded', {
							date: new Date(image.uploaded_at).toLocaleString()
						})}
					</p>
					<p>
						{$t('file_dashboard.imported', {
							yes_or_no: image.imported ? $t('words.yes') : $t('words.no')
						})}
					</p>
					<div class="flex flex-col gap-2">
						<BrownButton
							on:click={() => {
								edit_popup = image;
							}}
							>{$t('file_dashboard.edit_details')}
						</BrownButton>
						{#if image.quiztivities.length === 0 && image.quizzes.length === 0}
							<BrownButton
								on:click={() => {
									delete_image(image.id);
								}}>{$t('file_dashboard.delete_image')}</BrownButton
							>
						{/if}
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
			<h1 class="text-2xl text-center">{$t('file_dashboard.edit_the_image')}</h1>
			<form class="flex flex-col" on:submit|preventDefault={save_image_metadata}>
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
