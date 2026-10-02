<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->
<script lang="ts">
	import { Dashboard as SvelteDashboard } from '@uppy/svelte';
	import Uppy from '@uppy/core';
	import DropTarget from '@uppy/drop-target';
	import XHRUpload from '@uppy/xhr-upload';
	import ImageEditor from '@uppy/image-editor';
	import Compressor from '@uppy/compressor';
	import { fade } from 'svelte/transition';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { Button } from '$lib/components/ui/button';
	import ImagePlus from '@lucide/svelte/icons/image-plus';

	// CSS imports
	import '@uppy/core/dist/style.css';
	import '@uppy/dashboard/dist/style.css';
	import '@uppy/drop-target/dist/style.css';
	import '@uppy/image-editor/dist/style.css';
	import type { EditorData } from '../quiz_types';
	import { getLocalization } from '$lib/i18n';
	import { onMount } from 'svelte';
	import Library from '$lib/editor/uploader/Library.svelte';
	import Pixabay from '$lib/editor/uploader/Pixabay.svelte';

	const { t } = getLocalization();
	let {
		modalOpen = $bindable(),
		// card.svelte passes these with `bind:`, and this file passes `data` on to
		// Library/Pixabay the same way, so they have to be declared bindable.
		data = $bindable(),
		selected_question = $bindable(),
		video_upload = false,
		library_enabled = true,
		pixabay_enabled = true
	}: {
		modalOpen: boolean;
		data: EditorData;
		selected_question?: number;
		video_upload: boolean;
		library_enabled?: boolean;
		pixabay_enabled?: boolean;
	} = $props();

	// eslint-disable-next-line no-undef
	let video_popup: undefined | WindowProxy = $state(undefined);

	let selected_type: AvailableUploadTypes | null = $state(null);

	// Used only until GET /api/v1/storage/limits answers, and if it never does. Keep them
	// no larger than config.py's max_image_upload_size, so a failed fetch errs tight
	// rather than letting through a file the server will reject after the upload.
	const FALLBACK_MAX_FILE_SIZE = 5_000_000;
	const FALLBACK_TYPES = ['image/png', 'image/jpeg', 'image/gif', 'image/webp'];
	// Shown under the picker, so the rule is visible before a file is chosen rather than
	// only in an error after one is.
	let max_file_size = $state(FALLBACK_MAX_FILE_SIZE);
	const max_file_size_mb = $derived(Math.round(max_file_size / 1_000_000));

	// eslint-disable-next-line no-unused-vars
	enum AvailableUploadTypes {
		// eslint-disable-next-line no-unused-vars
		Image,
		// eslint-disable-next-line no-unused-vars
		Video,
		// eslint-disable-next-line no-unused-vars
		Library,
		// eslint-disable-next-line no-unused-vars
		Pixabay
	}

	// The Dashboard plugin is installed by @uppy/svelte's <Dashboard> component below
	// (under the id "svelte:Dashboard", with our `dashboard_options` spread in). This
	// file used to ALSO call `.use(Dashboard)` here with no target, which left a second,
	// never-mounted Dashboard in the instance and -- because ImageEditor was targeted at
	// the Dashboard *class* -- attached the image editor to that dead one instead of the
	// visible one. Install ImageEditor untargeted and let the visible Dashboard list it.
	// `restrictions` is a Core option. It was being passed through the Dashboard's props
	// instead -- and `restrictions` appears nowhere in @uppy/dashboard's types, so the
	// picker has in fact never had a size cap or a type filter: it accepted an SVG and a
	// 2GB file alike and left the server to answer. The earlier fix in this file (`props`
	// rather than `properties`) was real but in the wrong place.
	//
	// These are starting values. `onMount` replaces them with the server's own numbers
	// from GET /api/v1/storage/limits, so config.py is the only place they are written.
	const uppy = new Uppy({
		restrictions: {
			maxFileSize: FALLBACK_MAX_FILE_SIZE,
			maxNumberOfFiles: 1,
			allowedFileTypes: FALLBACK_TYPES
		}
	})
		.use(DropTarget, {
			target: document.body
		})
		.use(ImageEditor, {
			quality: 0.8
		})
		.use(Compressor, {
			quality: 0.6
		})
		.use(XHRUpload, {
			endpoint: `/api/v1/storage/`
		});
	// @uppy/svelte v4's Dashboard prop for the plugin's options is `props`, not
	// `properties`. `inline: true` is the component's own default. Restrictions are not
	// a Dashboard option and live on the Uppy instance above.
	const dashboard_options = {
		plugins: ['ImageEditor']
	};
	// Read eagerly rather than inside the `complete` callback: that fires from Uppy, not
	// from the component, and `$t` is a store read that wants component context.
	const upload_failed_msg = $derived($t('uploader.upload_failed'));
	const too_large_msg = $derived($t('uploader.too_large', { size: max_file_size_mb }));
	const quota_msg = $derived($t('uploader.quota_reached'));
	let image_id: string | undefined;
	uppy.on('upload', () => {
		// Don't let an id from an earlier attempt stand in for this one.
		image_id = undefined;
	});
	uppy.on('upload-success', (file, response) => {
		image_id = (response.body as { id?: string } | undefined)?.id;
	});
	// Uppy's own error text for a failed XHR is the status line, which tells a person
	// nothing. The two refusals they can actually act on get their own words.
	uppy.on('upload-error', (file, error, response) => {
		const status = response?.status;
		if (status === 413) {
			uppy.info(too_large_msg, 'error', 8000);
		} else if (status === 409) {
			uppy.info(quota_msg, 'error', 8000);
		}
	});
	// A failed upload used to look exactly like a successful one: `complete` wrote
	// `undefined` into the quiz and closed the modal either way, which is why a 401 from
	// the storage endpoint showed up as "the dialog closes and nothing happens". Only
	// close on an upload that actually produced an id; otherwise leave the Dashboard up,
	// where Uppy's own status bar shows the error.
	uppy.on('complete', (result) => {
		const ok = result.failed.length === 0 && result.successful.length > 0;
		if (!ok || image_id === undefined) {
			if (ok) {
				uppy.info(upload_failed_msg, 'error', 8000);
			}
			return;
		}

		if (selected_question === undefined) {
			data.cover_image = image_id;
		} else if (selected_question === -1) {
			data.background_image = image_id;
		} else {
			data.questions[selected_question].image = image_id;
		}

		modalOpen = false;
		selected_type = null;
	});

	onMount(() => {
		window.addEventListener('storage', (e) => {
			if (e.key !== 'video_upload_id') {
				return;
			}
			localStorage.removeItem('video_upload_id');
			data.questions[selected_question].image = e.newValue;
			selected_type = null;
		});
	});

	// The limits come from the server so there is one copy of them. A person finding out
	// their file is too big from Uppy, before it uploads, is the whole point: the server
	// answers 413 either way, but only after they have waited for the transfer.
	onMount(async () => {
		try {
			const res = await fetch('/api/v1/storage/limits');
			if (!res.ok) return;
			const limits: { max_file_size: number; accepted_types: string[] } = await res.json();
			if (!limits.max_file_size || !limits.accepted_types?.length) return;
			uppy.setOptions({
				restrictions: {
					maxFileSize: limits.max_file_size,
					maxNumberOfFiles: 1,
					allowedFileTypes: limits.accepted_types
				}
			});
			max_file_size = limits.max_file_size;
		} catch {
			// Keep the fallbacks. An unreachable API is about to fail the upload anyway.
		}
	});

	const upload_video = async () => {
		video_popup = window.open(
			'/edit/videos',
			'_blank',
			'popup=true,toolbar=false,menubar=false,location=false,'
		);
		video_popup.addEventListener('beforeunload', () => {
			video_popup = undefined;
		});
	};

	const handle_on_click = (e: Event) => {
		if (e.target === e.currentTarget) {
			modalOpen = false;
			selected_type = null;
		}
	};
	onMount(() => {
		window.addEventListener('keydown', (e: KeyboardEvent) => {
			if (e.key === 'Escape') {
				modalOpen = false;
				selected_type = null;
			}
		});
	});
</script>

{#if modalOpen}
	<div
		class="fixed inset-0 z-20 flex overflow-y-auto bg-black/50 p-4"
		onclick={handle_on_click}
		tabindex="0"
		role="button"
		aria-label="Close modal"
		onkeydown={(e) => (e.key === 'Enter' || e.key === ' ' ? handle_on_click(e) : null)}
		transition:fade={{ duration: 100 }}
	>
		{#if selected_type === null}
			<div
				class="border-border bg-card m-auto w-full max-w-lg rounded-xl border p-6 shadow-xl"
			>
				<h1 class="mb-5 text-center text-xl font-semibold">
					{$t('uploader.select_upload_type')}
				</h1>
				<div class="flex flex-wrap gap-3 sm:flex-nowrap">
					<div class="w-full">
						<BrownButton
							onclick={() => {
								selected_type = AvailableUploadTypes.Image;
							}}
							>{$t('words.image')}
						</BrownButton>
					</div>
					<div class="w-full">
						<BrownButton
							disabled={!video_upload}
							onclick={() => {
								selected_type = AvailableUploadTypes.Video;
							}}
							>{$t('words.video')}
						</BrownButton>
					</div>
					{#if library_enabled}
						<div class="w-full">
							<BrownButton
								onclick={() => {
									selected_type = AvailableUploadTypes.Library;
								}}
								>{$t('words.library')}
							</BrownButton>
						</div>
					{/if}
					{#if pixabay_enabled}
						<div class="w-full">
							<BrownButton
								onclick={() => {
									selected_type = AvailableUploadTypes.Pixabay;
								}}
								>Pixabay
							</BrownButton>
						</div>
					{/if}
				</div>
			</div>
		{:else if selected_type === AvailableUploadTypes.Image}
			<div class="m-auto w-full max-w-3xl" transition:fade={{ duration: 100 }}>
				<div>
					<SvelteDashboard {uppy} props={dashboard_options} />
				</div>
				<!-- State the rule before a file is picked, not only in the error after. -->
				<p class="text-muted-foreground mt-3 text-center text-sm">
					{$t('uploader.size_hint', { size: max_file_size_mb })}
				</p>
			</div>
		{:else if selected_type === AvailableUploadTypes.Video}
			<div
				class="border-border bg-card m-auto w-full max-w-lg rounded-xl border p-6 shadow-xl"
				transition:fade={{ duration: 100 }}
			>
				<h1 class="text-3xl text-center mb-4">{$t('uploader.upload_a_video')}</h1>
				{#if video_popup}
					<p class="text-center">
						{$t('uploader.upload_video_popup_notice')}
					</p>
				{:else}
					<BrownButton onclick={upload_video} type="button"
						>{$t('uploader.upload_video')}</BrownButton
					>
				{/if}
			</div>
		{:else if selected_type === AvailableUploadTypes.Library}
			<div>
				<Library bind:data {selected_question} bind:modalOpen />
			</div>
		{:else if selected_type === AvailableUploadTypes.Pixabay}
			<div>
				<Pixabay bind:data {selected_question} bind:modalOpen />
			</div>
		{/if}
	</div>
{/if}
<!-- Was a hand-rolled button: label set in italic for no reason, no gap between
     that label and its icon so the two collided, pt-10 of hardcoded dead space
     above it, an arbitrary w-1/2, a raw Heroicon path, and gray-500/gray-300
     borders that ignore the theme. It is a shadcn outline button now, full width of
     whatever field it sits in, with the Lucide icon and a real gap. -->
<div class="w-full" transition:fade>
	<Button
		type="button"
		variant="outline"
		class="w-full gap-2"
		onclick={() => {
			modalOpen = true;
			// Image is the only enabled type at every call site today (video/library/
			// Pixabay are hidden, not deleted, per CLAUDE.md's feature-triage rule) --
			// skip straight to the uploader instead of showing a picker with one option.
			if (!video_upload && !library_enabled && !pixabay_enabled) {
				selected_type = AvailableUploadTypes.Image;
			}
		}}
	>
		<ImagePlus class="size-4 shrink-0" />
		{$t('uploader.add_image')}
	</Button>
</div>

<style>
	/* Uppy ships a light-only palette and draws its own chrome, so inside our modal
	   its close control measured 1.09:1 and its footer text 2.79:1 -- both well under
	   AA. Point its variables at the theme instead of letting it choose. */
	:global(.uppy-Dashboard-inner),
	:global(.uppy-Dashboard-AddFiles) {
		background: var(--card);
		border-color: var(--border);
	}

	:global(.uppy-Dashboard-close) {
		color: var(--foreground);
		font-size: 1.75rem;
	}

	:global(.uppy-Dashboard-browse),
	:global(.uppy-Dashboard-AddFiles-title) {
		color: var(--foreground);
	}

	/* Uppy's own branding link, at 3.07:1 against AA's 4.5 and not ours to show.
	   ckeditor's equivalent is hidden the same way. */
	:global(.uppy-Dashboard-poweredBy) {
		display: none;
	}
</style>
