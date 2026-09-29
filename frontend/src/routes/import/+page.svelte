<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import * as Card from '$lib/components/ui/card/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';
	import Upload from '@lucide/svelte/icons/upload';
	import { navbarVisible } from '$lib/stores.svelte.ts';
	import { onMount } from 'svelte';
	import { page } from '$app/state';

	navbarVisible.visible = true;

	const { t } = getLocalization();
	let url_input = $state('');
	let file_input: File[] = $state();
	let kahoot_regex = /^https:\/\/create\.kahoot\.it\/details\/.*\/?([a-zA-Z-\d]{36})\/?$/;

	let url_valid = $derived(kahoot_regex.test(url_input));
	let is_loading = $state(false);

	const submit = async (e: Event) => {
		e.preventDefault();
		if (!url_valid) {
			return;
		}
		is_loading = true;
		const regex_res = kahoot_regex.exec(url_input);
		const res = await fetch(`/api/v1/quiz/import/${regex_res[1]}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (res.status === 200) {
			window.location.href = '/my-quizzes';
		} else if (res.status === 400) {
			/*			alertModal.set({
				open: true,
				title: 'Import failed',
				body: "This quiz isn't (yet) supported!"
			});*/
			alert("This quiz isn't (yet) supported!");
		} else if (res.status === 403) {
			/*			alertModal.set({
				open: true,
				title: 'Import failed',
				body: 'Unknown error while importing the quiz!'
			});*/
			alert('Quiz is probably private!');
		} else {
			alert(`Kahoot replied with ${res.status}`);
		}
		is_loading = false;
	};

	const file_submit = async (e: Event) => {
		e.preventDefault();
		is_loading = true;
		const formdata = new FormData();
		formdata.append('file', file_input[0]);
		let res;
		if (file_input[0].name.includes('.xlsx')) {
			res = await fetch('/api/v1/quiz/excel-import', {
				method: 'POST',
				body: formdata
			});
		} else if (file_input[0].name.includes('.cqa')) {
			res = await fetch('/api/v1/eximport/', {
				method: 'POST',
				body: formdata
			});
		} else {
			alert('Wrong file type');
			is_loading = false;
			return;
		}

		if (res.status === 200) {
			window.location.href = '/my-quizzes';
		} else {
			/*			alertModal.set({
				open: true,
				title: 'Import failed',
				body: 'Something went wrong!'
			});*/
			alert('Something went wrong!');
		}
		is_loading = false;
	};

	onMount(() => {
		let url_from_path = page.url.searchParams.get('url');
		if (url_from_path === '') {
			url_from_path = null;
		}
		url_input = url_from_path ?? '';
	});
</script>

<svelte:head>
	<title>frogQuiz - Import</title>
</svelte:head>

<div class="flex items-center justify-center h-full px-4">
	<!-- Was one card holding a grid-cols-2 with no breakpoint and a border-l divider,
	     so on a phone each method got about 170px and its prose wrapped every two or
	     three words. Two cards that stack instead: the cards do the separating, so the
	     divider goes, and each method carries its own heading, explanation and action.
	     The card also carried w-screen, which is 100vw and so includes the scrollbar. -->
	<div class="mx-auto w-full max-w-4xl px-4 py-8">
		<h1 class="mb-1 text-center text-3xl font-bold tracking-tight">{$t('words.import')}</h1>
		<p class="text-muted-foreground mb-6 text-center text-sm">
			{$t('import_page.choose_a_source')}
		</p>

		<div class="grid gap-4 md:grid-cols-2">
			<Card.Root class="flex flex-col">
				<Card.Header>
					<Card.Title>{$t('import_page.a_kahoot_quiz')}</Card.Title>
					<Card.Description>{$t('import_page.side_import_kahoot')}</Card.Description>
				</Card.Header>
				<Card.Content class="flex flex-1 flex-col">
					<form onsubmit={submit} class="flex flex-1 flex-col gap-4">
						<div class="grid gap-2">
							<Label for="url">{$t('words.url')}</Label>
							<Input
								id="url"
								bind:value={url_input}
								name="url"
								type="url"
								placeholder="https://create.kahoot.it/details/..."
								aria-invalid={url_input !== '' && !url_valid}
							/>
							<p class="text-muted-foreground text-xs">
								{$t('import_page.url_should_look_like_this')}
							</p>
						</div>
						<Button
							type="submit"
							class="mt-auto w-full"
							disabled={!url_valid || is_loading}
						>
							{#if is_loading}
								<LoaderCircle class="size-4 animate-spin" aria-hidden="true" />
								<span class="sr-only">{$t('words.submit')}</span>
							{:else}
								{$t('words.submit')}
							{/if}
						</Button>
					</form>
				</Card.Content>
			</Card.Root>

			<Card.Root class="flex flex-col">
				<Card.Header>
					<Card.Title>{$t('import_page.frogquiz_quiz')}</Card.Title>
					<Card.Description>
						{$t('import_page.this_side_frogquiz')}
						{$t('import_page.this_side_frogquiz_excel')}
					</Card.Description>
				</Card.Header>
				<Card.Content class="flex flex-1 flex-col">
					<form onsubmit={file_submit} class="flex flex-1 flex-col gap-4">
						<div class="grid gap-2">
							<Label for="file">{$t('words.file')}</Label>
							<!-- A raw file input renders as "Choose File | No file chosen",
							     truncates on a phone, and cannot be styled. The label is the
							     control; the input is visually hidden but still focusable. -->
							<label
								for="file"
								class="border-input bg-background hover:bg-muted focus-within:ring-ring flex min-h-11 cursor-pointer items-center gap-2 rounded-md border px-3 py-2 text-sm transition-colors focus-within:ring-2"
							>
								<Upload class="text-muted-foreground size-4 shrink-0" />
								<span class="min-w-0 truncate">
									{file_input?.[0]?.name ?? $t('import_page.choose_a_file')}
								</span>
								<input
									id="file"
									bind:files={file_input}
									name="file"
									type="file"
									accept=".cqa,.xlsx"
									class="sr-only"
								/>
							</label>
							<p class="text-muted-foreground text-xs">
								{$t('import_page.upload_file_ending')}
							</p>
						</div>
						<Button
							type="submit"
							class="mt-auto w-full"
							disabled={!file_input || is_loading}
						>
							{#if is_loading}
								<LoaderCircle class="size-4 animate-spin" aria-hidden="true" />
								<span class="sr-only">{$t('words.submit')}</span>
							{:else}
								{$t('words.submit')}
							{/if}
						</Button>
					</form>
				</Card.Content>
			</Card.Root>
		</div>

		<p
			class="text-muted-foreground mt-6 flex items-center justify-center gap-1.5 text-center text-sm"
		>
			{$t('import_page.need_help')}
			<a
				href="/docs/import-from-kahoot"
				class="text-primary fq-touch-target relative inline-flex min-h-11 items-center font-medium underline-offset-4 transition-colors hover:underline"
				>{$t('import_page.visit_docs')}</a
			>
		</p>
	</div>
</div>
<!--{/if}-->
