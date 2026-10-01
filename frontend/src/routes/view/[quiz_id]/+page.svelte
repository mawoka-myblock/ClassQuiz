<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import DownloadQuiz from '$lib/components/DownloadQuiz.svelte';
	import { answerColor } from '$lib/play/answer_colors';
	import AnswerShape from '$lib/play/kahoot_mode_assets/AnswerShape.svelte';
	import { getLocalization } from '$lib/i18n';
	import { QuizQuestionType } from '$lib/quiz_types.js';
	import StartGamePopup from '$lib/dashboard/start_game.svelte';
	import { onMount } from 'svelte';
	import Spinner from '$lib/Spinner.svelte';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import { page } from '$app/state';
	import ModComponent from './ModComponent.svelte';
	import { get_foreground_color } from '$lib/helpers.ts';
	import { anonDaysLeft, getAnonSecret, clearAnonSecret } from '$lib/anon_quiz';
	import { sanitizeTitleHtml, htmlToPlainText } from '$lib/sanitize';
	import { isQuestionComplete } from '$lib/editor/question_complete';
	import { Button, buttonVariants } from '$lib/components/ui/button/index.js';
	import { Badge } from '$lib/components/ui/badge/index.js';
	import * as Card from '$lib/components/ui/card/index.js';
	import * as Collapsible from '$lib/components/ui/collapsible/index.js';
	import * as AlertDialog from '$lib/components/ui/alert-dialog/index.js';
	import Check from '@lucide/svelte/icons/check';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import CircleDot from '@lucide/svelte/icons/circle-dot';
	import Clock from '@lucide/svelte/icons/clock';
	import ListChecks from '@lucide/svelte/icons/list-checks';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import Download from '@lucide/svelte/icons/download';
	import ExternalLink from '@lucide/svelte/icons/external-link';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Play from '@lucide/svelte/icons/play';
	import Repeat from '@lucide/svelte/icons/repeat';
	import Trash2 from '@lucide/svelte/icons/trash-2';

	let start_game: string | null = $state(null);
	let download_id: string | null = $state(null);
	const urlparams = page.url.searchParams;
	const mod_view = Boolean(urlparams.get('mod'));
	// `autoExpand`, which the moderation page still sends, is gone: questions are
	// always shown open now, so there is nothing left for it to expand.
	const auto_return = Boolean(urlparams.get('autoReturn'));

	const { t } = getLocalization();
	let { data } = $props();
	let { quiz, logged_in }: { quiz: QuizData; logged_in: boolean } = $state(data);

	// Ownership of an anonymously-created quiz can only be checked client-side
	// (the secret lives in this browser's localStorage, not on the server).
	let owns_anonymously = $state(false);
	// Account ownership is checked the same way, rather than in the loader, so the
	// page's server render stays identical for every visitor.
	let owns_on_account = $state(false);
	const is_owner = $derived(owns_anonymously || owns_on_account);

	onMount(async () => {
		owns_anonymously = quiz.user_id === null && getAnonSecret(quiz.id) !== null;
		if (logged_in && quiz.user_id) {
			try {
				const res = await fetch('/api/v1/users/me');
				if (res.ok) {
					const me = await res.json();
					owns_on_account = me.id === quiz.user_id.id;
				}
			} catch {
				// Edit and Delete just stay hidden; nothing else on the page needs this.
			}
		}
	});

	// Only the owner sees the answer key. Anyone else viewing a public quiz may well
	// play it later, and this page used to spoil it. Presentation only, not a secret:
	// /quiz/get/public still returns `right` on every answer, since the game needs it.
	const show_answers = $derived(is_owner);

	// An ORDER question stores its answers in the correct order, so listing them as
	// stored is the answer key. Visitors get them alphabetised instead.
	const visitor_order = (answers: { answer: string }[]) =>
		[...answers].sort((a, b) => a.answer.localeCompare(b.answer));

	// What the server actually allows (routers/quiz.py, start_quiz): its own creator, or
	// anyone signed in if the quiz is public. Offering Play on somebody else's unlisted
	// quiz gave a signed-in visitor a button that answered "quiz not found".
	const can_start = $derived(owns_anonymously || (logged_in && (quiz.public || owns_on_account)));

	// A draft is a quiz with at least one unfinished question -- the same rule the
	// server uses (frogquiz/helpers/completeness.py) to refuse POST /quiz/start.
	// There is no draft column; this is computed the same way on every render.
	const is_draft = $derived(
		quiz.questions.length === 0 || quiz.questions.some((q) => !isQuestionComplete(q))
	);

	// An anonymous quiz is swept 30 days after creation. The holder of the secret
	// is the only person who can act on that, so they are the one who has to be
	// told -- signing in is what makes it permanent.
	const expires_at = $derived(quiz.expire_at ? new Date(quiz.expire_at) : null);
	const days_until_expiry = $derived(anonDaysLeft(quiz.expire_at));

	let delete_open = $state(false);
	let deleting = $state(false);
	let delete_error = $state(false);

	const delete_quiz = async () => {
		const anon_secret = getAnonSecret(quiz.id);
		deleting = true;
		delete_error = false;
		let res: Response;
		try {
			res = await fetch(`/api/v1/quiz/delete/${quiz.id}`, {
				method: 'DELETE',
				headers: anon_secret ? { 'X-Anon-Secret': anon_secret } : {}
			});
		} catch {
			deleting = false;
			delete_error = true;
			return;
		}
		deleting = false;
		if (res.ok) {
			clearAnonSecret(quiz.id);
			window.location.href = '/my-quizzes';
		} else {
			// Stays open on purpose: a dialog that closed on failure would read as success.
			delete_error = true;
		}
	};

	let claiming = $state(false);
	let claim_error = $state(false);

	const claim_quiz = async () => {
		const anon_secret = getAnonSecret(quiz.id);
		if (!anon_secret) return;
		claiming = true;
		claim_error = false;
		let res: Response;
		try {
			res = await fetch(`/api/v1/quiz/claim/${quiz.id}`, {
				method: 'POST',
				headers: { 'X-Anon-Secret': anon_secret }
			});
		} catch {
			claiming = false;
			claim_error = true;
			return;
		}
		claiming = false;
		if (res.ok) {
			clearAnonSecret(quiz.id);
			window.location.href = '/my-quizzes';
		} else {
			claim_error = true;
		}
	};

	// ABCD and CHECK render as the real game tiles, with the shape that carries answer
	// identity for anyone who can't separate the hues. A missing type is an old ABCD.
	const is_tile_question = (question: Question): boolean =>
		question.type === undefined ||
		question.type === QuizQuestionType.ABCD ||
		question.type === QuizQuestionType.CHECK;

	interface Question {
		type?: QuizQuestionType;
		time: string;
		question: string;
		image?: string;
		// RANGE questions carry an object here rather than a list.
		answers: any;
	}

	interface QuizData {
		id: string;
		public: boolean;
		title: string;
		description: string;
		cover_image?: string;
		expire_at?: string | null;
		created_at: string;
		updated_at: string;
		user_id: { id: string; username: string } | null;
		imported_from_kahoot?: boolean;
		questions: Question[];
		kahoot_id?: string;
		mod_rating?: number;
	}
</script>

<svelte:head>
	<title>frogQuiz - View {htmlToPlainText(quiz.title)}</title>
</svelte:head>

<div class="mx-auto w-full max-w-2xl px-4 py-8 sm:py-12">
	<!-- fq-section's rhythm, but stretched: fq-section centres its children, which
	     would shrink every card to its content width. -->
	<div class="flex flex-col gap-(--fq-space-group)">
		{#if mod_view}
			<div class="flex justify-center">
				<ModComponent autoReturn={auto_return} quiz_id={quiz.id} />
			</div>
		{/if}

		{#if owns_anonymously}
			<!-- First thing on the page, because it is the one thing here with a deadline.
			     Collapsed, it still says the fact that matters -- this quiz is going away and
			     when; expanding gives the why and the way to keep it. -->
			<Collapsible.Root
				class="border-primary/40 bg-primary/10 text-foreground rounded-xl border"
			>
				<Collapsible.Trigger
					class="group focus-visible:ring-ring flex w-full min-w-0 items-center gap-3 rounded-xl px-4 py-3 text-left focus-visible:ring-2 focus-visible:outline-none"
				>
					<TriangleAlert class="text-primary size-5 shrink-0" aria-hidden="true" />
					<span
						class="flex min-w-0 flex-1 flex-col sm:flex-row sm:items-baseline sm:gap-2"
					>
						<span class="font-medium">{$t('view_quiz_page.anon_temporary')}</span>
						{#if days_until_expiry !== null}
							<span class="text-muted-foreground text-sm">
								{$t('view_quiz_page.anon_expires_short', {
									count: days_until_expiry
								})}
							</span>
						{/if}
					</span>
					<span class="text-muted-foreground hidden text-sm sm:inline">
						<span class="group-data-[state=open]:hidden"
							>{$t('view_quiz_page.anon_more')}</span
						>
						<span class="hidden group-data-[state=open]:inline"
							>{$t('view_quiz_page.anon_less')}</span
						>
					</span>
					<ChevronDown
						class="text-muted-foreground size-4 shrink-0 transition-transform group-data-[state=open]:rotate-180"
						aria-hidden="true"
					/>
				</Collapsible.Trigger>
				<Collapsible.Content>
					<div class="flex flex-col gap-3 px-4 pb-4 pl-12 text-sm">
						<div class="text-muted-foreground flex flex-col gap-1">
							{#if expires_at}
								<p>
									{$t('view_quiz_page.anon_expires', {
										count: days_until_expiry,
										date: expires_at.toLocaleDateString()
									})}
								</p>
							{/if}
							<p>
								{logged_in
									? $t('view_quiz_page.anon_claim_hint')
									: $t('view_quiz_page.anon_sign_in_hint')}
							</p>
						</div>
						{#if logged_in}
							<Button
								onclick={claim_quiz}
								disabled={claiming}
								class="w-full sm:w-fit"
							>
								{#if claiming}
									<LoaderCircle class="animate-spin" aria-hidden="true" />
								{/if}
								{claiming
									? $t('view_quiz_page.claiming')
									: $t('view_quiz_page.claim_quiz')}
							</Button>
							{#if claim_error}
								<p class="text-destructive" aria-live="polite">
									{$t('view_quiz_page.claim_failed')}
								</p>
							{/if}
						{:else}
							<Button
								href="/account/register?returnTo=/view/{quiz.id}"
								class="w-full sm:w-fit"
							>
								{$t('view_quiz_page.anon_sign_up')}
							</Button>
						{/if}
					</div>
				</Collapsible.Content>
			</Collapsible.Root>
		{/if}

		<Card.Root>
			{#if quiz.cover_image}
				<!-- First child, so the Card rounds its top corners and drops its top padding. -->
				<img
					class="max-h-64 w-full object-cover"
					src="/api/v1/storage/download/{quiz.cover_image}"
					alt=""
				/>
			{/if}
			<Card.Header>
				<h1
					class="text-2xl font-semibold tracking-tight text-balance sm:text-3xl [&_p]:inline"
				>
					{@html sanitizeTitleHtml(quiz.title)}
				</h1>
				{#if quiz.description}
					<p class="text-muted-foreground mt-1 text-base">{quiz.description}</p>
				{/if}
				<div class="text-muted-foreground mt-3 flex flex-wrap items-center gap-2 text-xs">
					<Badge variant="secondary">
						{quiz.public ? $t('words.public') : $t('words.private')}
					</Badge>
					{#if is_draft}
						<Badge variant="outline">{$t('draft.badge')}</Badge>
					{/if}
					<span>
						{quiz.questions.length}
						{$t('words.question', { count: quiz.questions.length })}
					</span>
					{#if quiz.imported_from_kahoot}
						<Badge variant="outline">{$t('view_quiz_page.imported')}</Badge>
					{/if}
					{#if quiz.user_id}
						<!-- Plain text: public profiles are hidden for the MVP (see MVP.md). -->
						<span>{$t('view_quiz_page.made_by')} @{quiz.user_id.username}</span>
					{/if}
				</div>
			</Card.Header>

			<Card.Footer
				class="flex flex-col items-stretch gap-3 sm:flex-row sm:flex-wrap sm:items-center"
			>
				<!-- Start is the one primary action; everything else is outline or ghost. -->
				<Button
					size="lg"
					disabled={!can_start || is_draft}
					onclick={() => (start_game = quiz.id)}
					aria-describedby={is_draft
						? 'draft-hint'
						: can_start
							? undefined
							: 'signed-out-hint'}
				>
					<Play />
					{$t('words.play')}
				</Button>
				{#if is_owner}
					<Button href="/edit?quiz_id={quiz.id}" variant="outline" size="lg">
						<Pencil />
						{$t('words.edit')}
					</Button>
				{/if}
				<Button href="/practice?quiz_id={quiz.id}" variant="outline" size="lg">
					<Repeat />
					{$t('words.practice')}
				</Button>
				<Button
					variant="outline"
					size="lg"
					disabled={!logged_in}
					onclick={() => (download_id = quiz.id)}
					aria-describedby={logged_in ? undefined : 'signed-out-hint'}
				>
					<Download />
					{$t('words.download')}
				</Button>
				{#if quiz.imported_from_kahoot && quiz.kahoot_id}
					<Button
						href="https://create.kahoot.it/details/{quiz.kahoot_id}"
						target="_blank"
						rel="noopener noreferrer"
						variant="ghost"
						size="lg"
					>
						<ExternalLink />
						{$t('view_quiz_page.view_on_kahoot')}
					</Button>
				{/if}
				{#if is_owner}
					<AlertDialog.Root
						bind:open={delete_open}
						onOpenChange={(o) => {
							if (!o) delete_error = false;
						}}
					>
						<AlertDialog.Trigger
							class={buttonVariants({
								variant: 'ghost',
								size: 'lg',
								class: 'text-muted-foreground hover:text-destructive sm:ml-auto'
							})}
						>
							<Trash2 />
							{$t('words.delete')}
						</AlertDialog.Trigger>
						<AlertDialog.Content class="max-w-md">
							<AlertDialog.Header>
								<AlertDialog.Title
									>{$t('view_quiz_page.delete_confirm_title')}</AlertDialog.Title
								>
								<AlertDialog.Description>
									{$t('view_quiz_page.delete_confirm')}
								</AlertDialog.Description>
							</AlertDialog.Header>
							{#if delete_error}
								<p class="text-destructive text-sm" aria-live="polite">
									{$t('view_quiz_page.delete_failed')}
								</p>
							{/if}
							<AlertDialog.Footer>
								<AlertDialog.Cancel disabled={deleting}
									>{$t('words.cancel')}</AlertDialog.Cancel
								>
								<!-- A plain Button, not AlertDialog.Action, so a failure stays visible. -->
								<Button
									variant="destructive"
									disabled={deleting}
									onclick={delete_quiz}
								>
									{#if deleting}
										<LoaderCircle class="animate-spin" aria-hidden="true" />
									{/if}
									{$t('words.delete')}
								</Button>
							</AlertDialog.Footer>
						</AlertDialog.Content>
					</AlertDialog.Root>
				{/if}
			</Card.Footer>
			<!-- Said in text rather than a tooltip: a disabled button can't be hovered or
			     focused on a phone, so a tooltip on it is never seen. -->
			{#if is_draft}
				<p id="draft-hint" class="text-muted-foreground -mt-2 px-6 text-sm">
					{is_owner ? $t('draft.hint_owner') : $t('draft.hint')}
				</p>
			{/if}
			{#if !logged_in}
				<p id="signed-out-hint" class="text-muted-foreground -mt-2 px-6 text-sm">
					{can_start
						? $t('view_quiz_page.download_signed_out_hint')
						: $t('view_quiz_page.start_signed_out_hint')}
				</p>
			{:else if !can_start && !is_draft}
				<p id="signed-out-hint" class="text-muted-foreground -mt-2 px-6 text-sm">
					{$t('view_quiz_page.unlisted_not_yours')}
				</p>
			{/if}
		</Card.Root>

		<section class="flex flex-col gap-8" aria-labelledby="questions-heading">
			<h2 id="questions-heading" class="text-lg font-semibold tracking-tight">
				{$t('view_quiz_page.questions_heading')}
			</h2>

			{#if quiz.questions.length === 0}
				<p
					class="border-border text-muted-foreground rounded-xl border border-dashed px-6 py-10 text-center text-sm"
				>
					{$t('view_quiz_page.no_questions')}
				</p>
			{/if}

			<!-- Each question is the editor's canvas, read-only: the same toolbar facts above
			     it, the same centred title and the same answer tiles, so a quiz looks the same
			     here as it did to the person who built it. Always open -- a list of bars you
			     have to click one by one hid the only content on the page. -->
			{#each quiz.questions as question, index_question}
				<article class="flex flex-col gap-3" aria-labelledby="question-{index_question}">
					<div class="flex flex-wrap items-center gap-2">
						<p class="text-sm font-medium">
							{$t('editor.question_n_of_total', {
								n: index_question + 1,
								total: quiz.questions.length
							})}
						</p>
						<div
							class="text-muted-foreground ml-auto flex flex-wrap items-center gap-2 text-sm"
						>
							<span
								class="border-border flex items-center gap-1.5 rounded-md border px-2.5 py-1"
							>
								<Clock class="size-4" aria-hidden="true" />
								<span class="tabular-nums"
									>{$t('view_quiz_page.seconds', {
										count: Number(question.time)
									})}</span
								>
							</span>
							{#if question.type === QuizQuestionType.CHECK}
								<span
									class="border-border flex items-center gap-1.5 rounded-md border px-2.5 py-1"
								>
									<ListChecks class="size-4" aria-hidden="true" />
									{$t('editor.multiple_answers')}
								</span>
							{:else if is_tile_question(question)}
								<span
									class="border-border flex items-center gap-1.5 rounded-md border px-2.5 py-1"
								>
									<CircleDot class="size-4" aria-hidden="true" />
									{$t('editor.single_answer')}
								</span>
							{/if}
						</div>
					</div>

					<div
						class="border-border bg-card flex flex-col gap-6 rounded-xl border p-4 shadow-sm sm:p-6"
					>
						{#if question.type === QuizQuestionType.SLIDE}
							{#await import('$lib/play/admin/slide.svelte')}
								<Spinner my_20={false} />
							{:then c}
								<div class="max-w-full overflow-hidden">
									<c.default question={quiz.questions[index_question]} />
								</div>
							{/await}
						{:else}
							<h3
								id="question-{index_question}"
								class="text-center text-xl font-semibold text-balance wrap-anywhere [&_p]:inline"
							>
								{@html sanitizeTitleHtml(question.question)}
							</h3>
							{#if question.image}
								<div class="mx-auto h-56 max-w-full">
									<MediaComponent
										css_classes="h-full w-auto max-w-full rounded-md"
										src={question.image}
										muted={true}
									/>
								</div>
							{/if}

							{#if is_tile_question(question)}
								<ul class="grid w-full gap-3 sm:grid-cols-2">
									{#each question.answers as answer, index_answer}
										{@const bg = answer.color ?? answerColor(index_answer)}
										{@const ink = get_foreground_color(bg)}
										<!-- min-w-0: a grid item won't shrink below its content otherwise. -->
										<li
											class="flex min-w-0 items-center gap-3 rounded-xl p-4"
											class:ring-3={show_answers && answer.right}
											class:ring-foreground={show_answers && answer.right}
											style="background-color: {bg}; color: {ink}"
										>
											<AnswerShape
												index={index_answer}
												class="size-6 shrink-0"
											/>
											<span
												class="min-w-0 flex-1 text-lg font-medium wrap-anywhere"
											>
												{answer.answer}
											</span>
											{#if show_answers && answer.right}
												<!-- The editor's mark-correct control, frozen in its "on" state. -->
												<span
													class="shrink-0 rounded-full border-2 p-1"
													style="border-color: {ink}; background-color: {ink}; color: {bg}"
												>
													<Check class="size-4" aria-hidden="true" />
												</span>
												<span class="sr-only">{$t('words.correct')}</span>
											{/if}
										</li>
									{/each}
								</ul>
							{:else if question.type === QuizQuestionType.RANGE}
								<p class="text-muted-foreground text-center">
									{show_answers
										? $t('view_quiz_page.range_answer', {
												min_correct: question.answers.min_correct,
												max_correct: question.answers.max_correct,
												min: question.answers.min,
												max: question.answers.max
											})
										: $t('view_quiz_page.range_answer_hidden', {
												min: question.answers.min,
												max: question.answers.max
											})}
								</p>
							{:else if question.type === QuizQuestionType.ORDER}
								<ol class="flex flex-col gap-3">
									{#each show_answers ? question.answers : visitor_order(question.answers) as answer, index_answer}
										<li
											class="bg-muted flex min-w-0 items-center gap-3 rounded-xl p-4"
										>
											{#if show_answers}
												<span class="text-muted-foreground tabular-nums"
													>{index_answer + 1}</span
												>
											{/if}
											<span class="min-w-0 text-lg font-medium wrap-anywhere"
												>{answer.answer}</span
											>
										</li>
									{/each}
								</ol>
							{:else if question.type === QuizQuestionType.TEXT && !show_answers}
								<!-- A TEXT question's answers are the accepted spellings: the key itself. -->
								<p class="text-muted-foreground text-center">
									{$t('view_quiz_page.text_answer_hidden')}
								</p>
							{:else if question.type === QuizQuestionType.VOTING || question.type === QuizQuestionType.TEXT}
								<ul class="grid w-full gap-3 sm:grid-cols-2">
									{#each question.answers as answer}
										<li
											class="bg-muted min-w-0 rounded-xl p-4 text-lg font-medium wrap-anywhere"
										>
											{answer.answer}
										</li>
									{/each}
								</ul>
							{/if}
						{/if}
					</div>
				</article>
			{/each}
		</section>
	</div>
</div>

<!-- No {#if} wrapper: the popup is a Dialog and owns its own visibility from `quiz_id`,
     as on the dashboard. -->
<StartGamePopup bind:quiz_id={start_game} />
<DownloadQuiz bind:quiz_id={download_id} />
