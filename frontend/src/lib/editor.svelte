<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
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
	import { Button } from '$lib/components/ui/button';
	import ArrowLeft from '@lucide/svelte/icons/arrow-left';
	import Save from '@lucide/svelte/icons/save';
	import Plus from '@lucide/svelte/icons/plus';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import { getAnonSecret, setAnonSecret } from '$lib/anon_quiz';
	import { sanitizeTitleHtml } from '$lib/sanitize';
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
	// Save used to be gated on the yup schema alone, which does not require a correct
	// answer. The rail flagged such a question, but the header warning sat inside the
	// schema branch and never showed, so an unplayable question saved silently.
	const save_blocked = $derived(schemaInvalid || incomplete_count > 0);
	// One list for everyone now: the account's quizzes signed in, this browser's signed out.
	const back_href = '/my-quizzes';
	let edit_id: string = $state();
	// The prompt used to be armed from the moment the editor mounted, so opening a quiz and
	// going straight back asked whether you wanted to discard changes you had not made. It
	// now arms on the first real edit. A form-level input/change listener is deliberate over
	// watching `data`: it cannot miss an edit made through a form control, and missing one
	// would lose someone's work.
	let confirm_to_leave = $state(false);
	// A failed save used to be `alert('Error')`: no status, no reason, and dismissing it
	// left you staring at the same form with no idea whether your work had gone anywhere.
	let save_error: string | null = $state(null);

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

	const confirmUnload = (event: BeforeUnloadEvent) => {
		if (!confirm_to_leave) {
			return;
		}
		event.preventDefault();
		event.returnValue = 'Are you sure you want to leave?';
		localStorage.setItem('edit_game', JSON.stringify(data));
		return 'unload';
	};
	const saveQuiz = async (e: Event) => {
		e.preventDefault();
		if (save_blocked) {
			return;
		}
		save_error = null;
		const anon_secret = quiz_id === null ? null : getAnonSecret(quiz_id);
		const res = await fetch(`/api/v1/editor/finish?edit_id=${edit_id}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				...(anon_secret ? { 'X-Anon-Secret': anon_secret } : {})
			},
			body: JSON.stringify(data)
		});
		if (res.ok) {
			confirm_to_leave = false;
			// Every save lands on the quiz's view page, new or existing, signed in or
			// not. It used to depend on all three, which read as the app forgetting
			// what you had just made.
			const saved = await res.json();
			// The server only ever hands back a fresh secret for a quiz created
			// without an account, once, right here.
			const new_anon_secret = res.headers.get('X-Anon-Secret');
			if (new_anon_secret) {
				setAnonSecret(saved.id, new_anon_secret);
			}
			window.location.href = `/view/${saved.id ?? quiz_id}`;
		} else {
			let detail = '';
			try {
				detail = (await res.json())?.detail ?? '';
			} catch {
				/* not JSON */
			}
			save_error = detail ? `${res.status}: ${detail}` : `${res.status}`;
		}
	};
</script>

<svelte:window onbeforeunload={confirmUnload} />
{#await getEditID()}
	<Spinner />
{:then _}
	<form
		onsubmit={saveQuiz}
		oninput={() => (confirm_to_leave = true)}
		onchange={() => (confirm_to_leave = true)}
	>
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
					{#if save_blocked}
						<!-- The old header showed a raw yup message, which named a field path rather
						     than telling the author what to go and fix. The count points at the rail,
						     where each unfinished question is already flagged. -->
						<p
							class="text-destructive ml-auto flex min-w-0 flex-1 items-center justify-end gap-2 text-sm font-medium"
						>
							<TriangleAlert class="size-4 shrink-0" />
							<span class="truncate">
								{incomplete_count > 0
									? $t('editor.needs_attention', { count: incomplete_count })
									: yupErrorMessage}
							</span>
						</p>
					{:else if save_error}
						<p
							class="text-destructive ml-auto flex min-w-0 flex-1 items-center justify-end gap-2 text-sm font-medium"
							role="alert"
						>
							<TriangleAlert class="size-4 shrink-0" />
							<span class="truncate">
								{$t('editor.save_failed', { detail: save_error })}
							</span>
						</p>
					{/if}
					<!-- The editor hides the navbar, which is where the theme switch used
					     to live and only live -- so the one screen people sit in longest
					     was the one with no way to change it. -->
					<ThemeToggle class={save_blocked || save_error ? 'ml-3' : 'ml-auto'} />
					<Button type="submit" disabled={save_blocked}>
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
