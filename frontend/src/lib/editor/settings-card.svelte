<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import type { EditorData } from '$lib/quiz_types';
	import { getLocalization } from '$lib/i18n';
	import Spinner from '$lib/Spinner.svelte';
	import { Button } from '$lib/components/ui/button';
	import Globe from '@lucide/svelte/icons/globe';
	import Link2 from '@lucide/svelte/icons/link-2';
	import X from '@lucide/svelte/icons/x';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import ChevronUp from '@lucide/svelte/icons/chevron-up';
	import { htmlToPlainText } from '$lib/sanitize';
	import { TITLE_MAX_LENGTH, DESCRIPTION_MAX_LENGTH } from '$lib/yupSchemas';
	import { cn } from '$lib/utils';

	const { t } = getLocalization();

	let uppyOpen = $state(false);
	let bg_uppy_open = $state(false);

	interface Props {
		edit_id: string;
		data: EditorData;
	}

	let { edit_id = $bindable(), data = $bindable() }: Props = $props();

	let custom_bg_color = $state(Boolean(data.background_color));
	// An <input type="color"> rejects an empty value and logs a format warning for it on
	// every editor load, so the swatch always holds a real colour and the checkbox decides
	// whether the quiz keeps it.
	let bg_color_value = $state(data.background_color || '#d6edc9');

	$effect(() => {
		data.background_color = custom_bg_color ? bg_color_value : undefined;
	});

	// Everything past title and description is decoration. A new quiz opened on six
	// fields, four of them optional, before a single question was in sight; they fold
	// away now and the questions sit directly under this card.
	let more_open = $state(false);

	// Length was only ever enforced at Save, so a long paste blew up the title box and
	// the editor header (see editor.svelte) long before the author got any feedback.
	// Measuring the title on its visible text, not its HTML, matches the yup schema.
	let title_length = $derived(htmlToPlainText(data.title).length);
	let description_length = $derived(data.description.length);
</script>

<div class="w-full">
	<div class="border-border bg-card flex flex-col gap-6 rounded-xl border p-6 shadow-sm">
		<div class="flex flex-col gap-2">
			<span class="text-muted-foreground text-sm font-medium">{$t('words.title')}</span>
			<!-- The title is a rich-text field, and with no content it rendered as a label
			     over blank space: on a new quiz the page said "A title is required" with
			     no visible box to type in. min-h-11 and the field styling give it the same
			     affordance as every other input on the page. -->
			{#await import('$lib/inline-editor.svelte')}
				<Spinner my_20={false} />
			{:then c}
				<div
					class="[&_[contenteditable]]:min-h-11 [&_[contenteditable]]:w-full [&_[contenteditable]]:text-left"
				>
					<c.default bind:text={data.title} label={$t('editor.quiz_title')} />
				</div>
			{/await}
			<span
				class={cn(
					'self-end text-xs tabular-nums',
					title_length > TITLE_MAX_LENGTH
						? 'text-destructive font-medium'
						: 'text-muted-foreground'
				)}
			>
				{title_length}/{TITLE_MAX_LENGTH}
			</span>
			{#if title_length > TITLE_MAX_LENGTH}
				<p class="text-destructive text-sm" role="alert">
					{$t('editor.title_too_long', { max: TITLE_MAX_LENGTH })}
				</p>
			{/if}
		</div>

		<label class="flex flex-col gap-2">
			<span class="text-muted-foreground text-sm font-medium">
				{$t('words.description')}
				<span class="font-normal">({$t('editor.optional')})</span>
			</span>
			<textarea
				bind:value={data.description}
				placeholder={$t('editor.description_placeholder')}
				class="border-input bg-background focus-visible:ring-ring h-24 w-full resize-none rounded-md border p-3 focus-visible:ring-2 focus-visible:outline-none"
			></textarea>
			<span
				class={cn(
					'self-end text-xs tabular-nums',
					description_length > DESCRIPTION_MAX_LENGTH
						? 'text-destructive font-medium'
						: 'text-muted-foreground'
				)}
			>
				{description_length}/{DESCRIPTION_MAX_LENGTH}
			</span>
			{#if description_length > DESCRIPTION_MAX_LENGTH}
				<p class="text-destructive text-sm" role="alert">
					{$t('editor.description_too_long', { max: DESCRIPTION_MAX_LENGTH })}
				</p>
			{/if}
		</label>

		<div>
			<Button
				type="button"
				variant="ghost"
				size="sm"
				class="text-muted-foreground -ml-2"
				aria-expanded={more_open}
				onclick={() => (more_open = !more_open)}
			>
				{#if more_open}
					<ChevronUp />
					{$t('editor.fewer_settings')}
				{:else}
					<ChevronDown />
					{$t('editor.more_settings')}
				{/if}
			</Button>
		</div>

		{#if more_open}
		<div class="flex flex-col gap-2">
			<span class="text-muted-foreground text-sm font-medium">{$t('words.cover_image')}</span>
			{#if data.cover_image != undefined && data.cover_image !== ''}
				<div class="relative w-fit">
					<img
						src="/api/v1/storage/download/{data.cover_image}"
						alt=""
						class="max-h-56 w-auto rounded-lg"
					/>
					<button
						type="button"
						class="border-border bg-card text-muted-foreground hover:text-destructive focus-visible:ring-ring absolute -top-2 -right-2 rounded-full border p-1 shadow-sm transition focus-visible:ring-2 focus-visible:outline-none"
						title={$t('words.delete')}
						aria-label={$t('words.delete')}
						onclick={() => {
							data.cover_image = null;
						}}
					>
						<X class="size-4" />
					</button>
				</div>
			{:else}
				{#await import('$lib/editor/uploader.svelte')}
					<Spinner my_20={false} />
				{:then c}
					<c.default
						bind:modalOpen={uppyOpen}
						bind:data
						video_upload={false}
						library_enabled={false}
						pixabay_enabled={false}
					/>
				{/await}
			{/if}
		</div>

		<div class="flex flex-col gap-2">
			<span class="text-muted-foreground text-sm font-medium">{$t('words.visibility')}</span>
			<Button
				type="button"
				variant="outline"
				class="w-fit"
				onclick={() => {
					data.public = !data.public;
				}}
			>
				{#if data.public}
					<Globe />
					{$t('words.public')}
				{:else}
					<Link2 />
					{$t('words.private')}
				{/if}
			</Button>
			<!-- "Private" was never private: the view page loads any quiz by link. It is
			     labelled Unlisted now, and says so (MVP.md D13). -->
			<p class="text-muted-foreground text-sm">{$t('editor.visibility_hint')}</p>
		</div>

		<div class="flex flex-col gap-2">
			<span class="text-muted-foreground text-sm font-medium">{$t('editor.bg_color')}</span>
			<div class="flex items-center gap-3">
				<!-- The label used to be a sibling of the checkbox rather than its parent, so
				     the tap target was the 20px box alone and the words beside it did
				     nothing. Wrapping makes the whole row one target. -->
				<label class="flex min-h-11 cursor-pointer items-center gap-3 text-sm">
					<input
						type="checkbox"
						id="custom-bg-color"
						bind:checked={custom_bg_color}
						class="accent-primary size-5"
					/>
					{$t('editor.bg_color_custom')}
				</label>
				<input
					type="color"
					class="border-input min-h-11 w-16 cursor-pointer rounded-md border p-1 disabled:cursor-not-allowed disabled:opacity-50"
					disabled={!custom_bg_color}
					bind:value={bg_color_value}
				/>
			</div>
		</div>

		<div class="flex flex-col gap-2">
			<span class="text-muted-foreground text-sm font-medium">{$t('editor.bg_image')}</span>
			{#if data.background_image}
				<div class="relative w-fit">
					<img
						src="/api/v1/storage/download/{data.background_image}"
						alt=""
						class="max-h-40 w-auto rounded-lg"
					/>
					<button
						type="button"
						class="border-border bg-card text-muted-foreground hover:text-destructive focus-visible:ring-ring absolute -top-2 -right-2 rounded-full border p-1 shadow-sm transition focus-visible:ring-2 focus-visible:outline-none"
						title={$t('words.delete')}
						aria-label={$t('words.delete')}
						onclick={() => {
							data.background_image = undefined;
						}}
					>
						<X class="size-4" />
					</button>
				</div>
			{:else}
				{#await import('$lib/editor/uploader.svelte')}
					<Spinner my_20={false} />
				{:then c}
					<c.default
						bind:modalOpen={bg_uppy_open}
						bind:data
						selected_question={-1}
						video_upload={false}
						library_enabled={false}
						pixabay_enabled={false}
					/>
				{/await}
			{/if}
		</div>
		{/if}
	</div>
</div>
