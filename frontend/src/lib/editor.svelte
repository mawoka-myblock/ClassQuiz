<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { onDestroy } from 'svelte';
	import { goto, replaceState } from '$app/navigation';
	import { dataSchema } from '$lib/yupSchemas';
	import type { EditorData } from './quiz_types';
	import Sidebar from '$lib/editor/sidebar.svelte';
	import QuestionStrip from '$lib/editor/question-strip.svelte';
	import SettingsCard from '$lib/editor/settings-card.svelte';
	import QuizCard from '$lib/editor/card.svelte';
	import AddNewQuestionPopup from '$lib/editor/AddNewQuestionPopup.svelte';
	import Spinner from './Spinner.svelte';
	import { getLocalization } from '$lib/i18n';
	import { isQuestionComplete } from '$lib/editor/question_complete';
	import { editorValidation } from '$lib/editor/validation.svelte';
	import { Button } from '$lib/components/ui/button';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Save from '@lucide/svelte/icons/save';
	import Plus from '@lucide/svelte/icons/plus';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import CloudCheck from '@lucide/svelte/icons/cloud-check';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';
	import { getAnonSecret, setAnonSecret } from '$lib/anon_quiz';
	import { htmlToPlainText, sanitizeTitleHtml } from '$lib/sanitize';
	import ThemeToggle from '$lib/theme-toggle.svelte';

	const { t } = getLocalization();

	let schemaInvalid = $state(false);
	let yupErrorMessage = $state('');

	interface Props {
		data: EditorData;
		quiz_id: string | null;
	}

	let { data = $bindable(), quiz_id }: Props = $props();
	let selected_question = $state(-1);
	// The rail collapses to a slim strip at lg and up; below that the horizontal
	// QuestionStrip carries the same navigation. Neither ever leaves the layout.
	let rail_collapsed = $state(false);
	// The canvas gets its own add control, so adding a question does not mean going
	// back to the rail first. Own state and own dialog instance, matching how the rail
	// and the mobile strip each hold theirs.
	let add_open = $state(false);

	// Nothing is marked missing until the first Save (see validation.svelte.ts). The flag
	// lives in a module, so it would otherwise carry over from the last quiz edited.
	editorValidation.shown = false;

	const validateInput = async (data: EditorData) => {
		try {
			await dataSchema.validate(data, { abortEarly: false });
			schemaInvalid = false;
			yupErrorMessage = '';
		} catch (err) {
			schemaInvalid = true;
			yupErrorMessage = err.errors ? err.errors[0] : '';
		}
	};
	$effect(() => {
		validateInput(data);
	});

	// Same rule the rail marks each question against, counted for the header.
	const incomplete_count = $derived(
		(data.questions ?? []).filter((q) => !isQuestionComplete(q)).length
	);
	// Playable is what Start needs, and the server refuses anything less (D14). Save used
	// to be disabled until the quiz was playable, so half a quiz could not be kept at all.
	const playable = $derived(!schemaInvalid && incomplete_count === 0);
	// Savable is what the server needs to store a draft: something to call it, and at
	// least one question with at least one answer.
	const savable = $derived(
		htmlToPlainText(data.title ?? '').trim().length > 0 &&
			(data.questions ?? []).length > 0 &&
			data.questions.every((q) => !Array.isArray(q.answers) || q.answers.length > 0)
	);
	// One list for everyone now: the account's quizzes signed in, this browser's signed out.
	const back_href = '/my-quizzes';
	let edit_id: string = $state();

	// --- Autosave (MVP.md D14) ---------------------------------------------------------
	// The quiz this editor writes to. Null until a new quiz's first save creates it.
	let current_id: string | null = $state(quiz_id);
	// What was last stored, as JSON. A snapshot comparison rather than form events:
	// adding, reordering and deleting questions happen outside the form's input events,
	// and missing one would lose someone's work.
	let saved_snapshot: string | null = $state(null);
	const snapshot = $derived(JSON.stringify(data));
	const unsaved = $derived(
		current_id === null ? savable : saved_snapshot !== null && snapshot !== saved_snapshot
	);
	let saving = $state(false);
	// A failed save used to be `alert('Error')`: no status, no reason, and dismissing it
	// left you staring at the same form with no idea whether your work had gone anywhere.
	let save_error: string | null = $state(null);
	let inflight: Promise<void> | null = null;
	let timer: ReturnType<typeof setTimeout> | undefined;
	const AUTOSAVE_DELAY_MS = 2500;

	const getEditID = async () => {
		const anon_secret = quiz_id === null ? null : getAnonSecret(quiz_id);
		const headers: Record<string, string> = anon_secret ? { 'X-Anon-Secret': anon_secret } : {};
		let res: Response;
		if (quiz_id === null) {
			res = await fetch(`/api/v1/editor/start?edit=false`, {
				method: 'POST',
				headers
			});
		} else {
			res = await fetch(`/api/v1/editor/start?edit=true&quiz_id=${quiz_id}`, {
				method: 'POST',
				headers
			});
		}
		if (res.status === 200) {
			const json = await res.json();
			edit_id = json.token;
			// The baseline is taken once the editor has rendered: the rich-text fields
			// normalise what they are given on load, and that is not an edit.
			setTimeout(() => (saved_snapshot = JSON.stringify(data)), 500);
			return;
		}
		// Was `alert('Error!')` -- a native dialog with no status, no reason, and
		// which left the promise resolved so the editor rendered behind it anyway.
		// Throwing lets the {:catch} below show what actually happened.
		let detail = '';
		try {
			detail = (await res.json())?.detail ?? '';
		} catch {
			/* not JSON; the status is still worth showing */
		}
		throw new Error(detail ? `${res.status}: ${detail}` : String(res.status));
	};

	const send = async (keepalive: boolean) => {
		const body = snapshot;
		const anon_secret = current_id === null ? null : getAnonSecret(current_id);
		saving = true;
		try {
			const res = await fetch(`/api/v1/editor/save?edit_id=${edit_id}`, {
				method: 'POST',
				// Browsers refuse a keepalive request over 64 KB outright. A big quiz is sent
				// normally; the leave prompt holds the page open while it goes.
				keepalive: keepalive && body.length < 60_000,
				headers: {
					'Content-Type': 'application/json',
					...(anon_secret ? { 'X-Anon-Secret': anon_secret } : {})
				},
				body
			});
			if (!res.ok) {
				let detail = '';
				try {
					const json = await res.json();
					// A 422 carries a list of pydantic errors rather than a sentence.
					detail = Array.isArray(json?.detail)
						? (json.detail[0]?.msg ?? '')
						: (json?.detail ?? '');
				} catch {
					/* not JSON */
				}
				save_error = detail ? `${res.status}: ${detail}` : `${res.status}`;
				return;
			}
			const saved = await res.json();
			// The server only ever hands back a secret for a quiz created without an
			// account, once, on the save that creates it.
			const new_anon_secret = res.headers.get('X-Anon-Secret');
			if (new_anon_secret) {
				setAnonSecret(saved.id, new_anon_secret);
			}
			if (current_id === null) {
				current_id = saved.id;
				// A reload now reopens the saved quiz instead of an empty /create.
				replaceState(`/edit?quiz_id=${saved.id}`, {});
			}
			saved_snapshot = body;
			save_error = null;
		} catch {
			save_error = $t('editor.offline');
		} finally {
			saving = false;
		}
	};

	// Saves whatever has changed, one request at a time: two saves of a new quiz racing
	// each other would both try to create it.
	const flush = async (keepalive = false) => {
		clearTimeout(timer);
		while (inflight) await inflight;
		if (!savable || !edit_id || !unsaved) return;
		inflight = send(keepalive);
		try {
			await inflight;
		} finally {
			inflight = null;
		}
	};

	$effect(() => {
		// Re-armed on every change, so it fires once typing pauses.
		void snapshot;
		if (!unsaved || !savable) return;
		clearTimeout(timer);
		timer = setTimeout(() => flush(), AUTOSAVE_DELAY_MS);
	});
	onDestroy(() => clearTimeout(timer));

	const confirmUnload = (event: BeforeUnloadEvent) => {
		if (!unsaved) {
			return;
		}
		// Try to keep it anyway: keepalive lets the request outlive the page.
		flush(true);
		event.preventDefault();
		event.returnValue = 'Are you sure you want to leave?';
		return 'unload';
	};

	// Back saves first, and goes to the quiz once it exists rather than to the list.
	const leave = async () => {
		await flush();
		goto(current_id && !save_error ? `/view/${current_id}` : back_href);
	};

	const saveQuiz = async (e: Event) => {
		e.preventDefault();
		// The first Save is when the editor starts pointing at what is missing.
		editorValidation.shown = true;
		if (!savable) {
			return;
		}
		await flush();
		if (save_error || !playable) {
			// Kept as a draft; the header now says what is left to do.
			return;
		}
		// Every save lands on the quiz's view page, new or existing, signed in or not.
		window.location.href = `/view/${current_id}`;
	};
</script>

<svelte:window onbeforeunload={confirmUnload} />
{#await getEditID()}
	<Spinner />
{:then _}
	<form onsubmit={saveQuiz}>
		<!-- w-screen is 100vw, which includes the scrollbar, and put a horizontal
		     scrollbar on every editor session. w-full is the width we actually want.
		     h-dvh rather than h-screen: 100vh is the wrong number on a phone, where
		     the browser chrome is counted in and the toolbar ends up off-screen. -->
		<div class="flex h-dvh w-full overflow-hidden">
			<Sidebar bind:data bind:selected_question bind:collapsed={rail_collapsed} />
			<div class="flex min-w-0 flex-1 flex-col">
				<header
					class="border-border bg-background flex h-14 shrink-0 items-center gap-2 border-b px-3 sm:gap-3 sm:px-4"
				>
					<Button
						href={back_href}
						variant="ghost"
						size="icon"
						aria-label={$t('words.back')}
						onclick={(e: MouseEvent) => {
							e.preventDefault();
							leave();
						}}
					>
						<ArrowLeft />
					</Button>
					<!-- A long title and a long error message were both bare flex items with no
					     basis/flex ratio between them, so a long title's intrinsic width ate almost
					     all the row before shrinking, leaving the error squeezed to a couple of
					     characters. Capping the title and giving the error flex-1 splits the row
					     predictably instead of letting title dominate. The error grows to claim
					     that room but aligns its contents right, so it still reads as sitting at
					     the end of the header next to the theme switch rather than trailing the
					     title. -->
					<p class="min-w-0 max-w-[45%] shrink truncate font-medium">
						{@html sanitizeTitleHtml(data.title)}
					</p>
					<!-- One line of status, most urgent first. A failed save always shows. What is
					     missing shows only after the first Save (D14): a new quiz is empty, and saying so
					     in red before anyone had typed was the complaint. -->
					{#if save_error}
						<p
							class="text-destructive ml-auto flex min-w-0 flex-1 items-center justify-end gap-2 text-sm font-medium"
							role="alert"
						>
							<TriangleAlert class="size-4 shrink-0" />
							<span class="truncate">
								{$t('editor.save_failed', { detail: save_error })}
							</span>
						</p>
					{:else if editorValidation.shown && !playable}
						<!-- The old header showed a raw yup message, which named a field path rather than
						     telling the author what to go and fix. The count points at the rail, where each
						     unfinished question is already flagged. -->
						<p
							class="text-destructive ml-auto flex min-w-0 flex-1 items-center justify-end gap-2 text-sm font-medium"
							role="status"
						>
							<TriangleAlert class="size-4 shrink-0" />
							<span class="truncate">
								{#if !savable}
									{$t('editor.cannot_save_yet')}
								{:else if incomplete_count > 0}
									<!-- The full sentence truncates to "Saved a..." on a phone. -->
									<span class="sm:hidden">
										{$t('editor.draft_needs_attention_short', {
											count: incomplete_count
										})}
									</span>
									<span class="hidden sm:inline">
										{$t('editor.draft_needs_attention', {
											count: incomplete_count
										})}
									</span>
								{:else}
									{yupErrorMessage}
								{/if}
							</span>
						</p>
					{:else if saving || current_id}
						<p
							class="text-muted-foreground ml-auto flex min-w-0 flex-1 items-center justify-end gap-1.5 text-sm"
							role="status"
						>
							{#if saving}
								<LoaderCircle class="size-4 shrink-0 animate-spin" />
								<span class="truncate">{$t('editor.saving')}</span>
							{:else if !unsaved}
								<CloudCheck class="size-4 shrink-0" />
								<span class="truncate">
									{playable ? $t('editor.saved') : $t('editor.saved_draft')}
								</span>
							{/if}
						</p>
					{/if}
					<!-- The editor hides the navbar, which is where the theme switch used to live and only
					     live -- so the one screen people sit in longest was the one with no way to change it. -->
					<ThemeToggle
						class={save_error ||
						(editorValidation.shown && !playable) ||
						saving ||
						current_id
							? 'ml-3'
							: 'ml-auto'}
					/>
					<Button type="submit" disabled={saving}>
						<Save />
						{$t('words.save')}
					</Button>
				</header>
				<!-- The canvas had no measure. Content stretched to whatever the panel
				     was, so on a wide screen the settings form ran to 900px of label and
				     field with a lake ofdead space between them. Cap it and centre it, the
				     way any document editor does. -->
				<QuestionStrip bind:data bind:selected_question />
				<div class="min-h-0 flex-1 overflow-y-auto px-4 py-6 sm:px-6 sm:py-8">
					<div class="mx-auto w-full max-w-2xl">
						{#if selected_question === -1}
							<SettingsCard bind:data bind:edit_id />
						{:else}
							<QuizCard bind:data bind:selected_question bind:edit_id />
						{/if}
						<!-- Sits at the end of the canvas column, in the measure, the way
						     a document editor puts "add" where the content ends. It is the
						     scroll container's last child so it is always reachable. -->
						<Button
							type="button"
							variant="outline"
							class="border-border/70 text-muted-foreground hover:text-foreground mt-6 h-14 w-full border-dashed"
							onclick={() => (add_open = true)}
						>
							<Plus />
							{$t('editor.add_new_question')}
						</Button>
					</div>
				</div>
			</div>
		</div>
	</form>
	<AddNewQuestionPopup
		bind:questions={data.questions}
		bind:open={add_open}
		bind:selected_question
	/>
{:catch error}
	<div class="flex min-h-dvh items-center justify-center px-6">
		<div class="w-full max-w-sm text-center">
			<h1 class="text-xl font-semibold tracking-tight">{$t('editor.start_failed')}</h1>
			<p class="text-muted-foreground mt-2 text-sm">{$t('editor.start_failed_detail')}</p>
			<p class="text-muted-foreground mt-4 font-mono text-xs break-all">{error.message}</p>
			<div class="mt-6 flex justify-center gap-2">
				<Button onclick={() => location.reload()}>{$t('words.retry')}</Button>
				<Button href="/" variant="outline">{$t('words.home')}</Button>
			</div>
		</div>
	</div>
{/await}
