<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	// My Quizzes: one page whether or not you are signed in (MVP.md decision D1). It
	// replaced two -- /dashboard for the account's quizzes and a bare browser list here.
	//
	// Quizzes made without an account are only findable through the secret in this
	// browser's localStorage. Without a list, the only record of one is the tab it was
	// created in: close it and the quiz is unreachable until the 30-day sweep removes it.
	// Signed in, those same quizzes are listed under the account's, with Claim.
	import { onMount } from 'svelte';
	import { getLocalization } from '$lib/i18n';
	import { navbarVisible } from '$lib/stores.svelte';
	import { anonDaysLeft, anonQuizIds, clearAnonSecret, getAnonSecret } from '$lib/anon_quiz';
	import Footer from '$lib/footer.svelte';
	import CommandpaletteNotice from '$lib/components/popover/commandpalettenotice.svelte';
	import DownloadQuiz from '$lib/components/DownloadQuiz.svelte';
	import ConfirmAction from '$lib/components/ConfirmAction.svelte';
	import StartGamePopup from '$lib/dashboard/start_game.svelte';
	import MediaComponent from '$lib/editor/MediaComponent.svelte';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Badge } from '$lib/components/ui/badge';
	import { isQuestionComplete } from '$lib/editor/question_complete';
	import Fuse from 'fuse.js';
	import type { QuizData } from '$lib/quiz_types';
	import type { PageData } from './$types';
	import Clock from '@lucide/svelte/icons/clock';
	import Download from '@lucide/svelte/icons/download';
	import LoaderCircle from '@lucide/svelte/icons/loader-circle';
	import Pencil from '@lucide/svelte/icons/pencil';
	import Play from '@lucide/svelte/icons/play';
	import Plus from '@lucide/svelte/icons/plus';
	import Search from '@lucide/svelte/icons/search';
	import Trash2 from '@lucide/svelte/icons/trash-2';
	import TriangleAlert from '@lucide/svelte/icons/triangle-alert';
	import UserPlus from '@lucide/svelte/icons/user-plus';
	import X from '@lucide/svelte/icons/x';

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();
	const { t } = getLocalization();
	navbarVisible.visible = true;

	const signed_in = $derived(Boolean(data.email));

	// Anything the list needs; account rows come from /quiz/list, browser rows from
	// /quiz/get/public, and both carry these.
	type Row = QuizData & { id: string; public?: boolean; expire_at?: string | null };

	let account_quizzes: Row[] = $state(data.quizzes ?? []);
	let browser_quizzes: Row[] | null = $state(null);

	// Per-row failures, shown on the row they belong to rather than as a page alert.
	let row_errors: Record<string, string> = $state({});
	let claiming: string | null = $state(null);

	let start_game: string | null = $state(null);
	let download_id: string | null = $state(null);

	const question_count = (quiz: Row): number =>
		Array.isArray(quiz.questions) ? quiz.questions.length : 0;

	// Same rule as the view page and the server (frogquiz/helpers/completeness.py):
	// a draft is a quiz with an unfinished question, or no questions at all. Rows
	// without a `questions` array at all (nothing to judge) are not flagged.
	const quiz_is_draft = (quiz: Row): boolean =>
		Array.isArray(quiz.questions) &&
		(quiz.questions.length === 0 || quiz.questions.some((q) => !isQuestionComplete(q)));

	onMount(async () => {
		const results = await Promise.all(
			anonQuizIds().map(async (id): Promise<Row | null> => {
				try {
					const res = await fetch(`/api/v1/quiz/get/public/${id}`);
					if (res.status === 404) {
						// Expired and swept, or deleted elsewhere. Drop the dead secret
						// so the list doesn't keep retrying it forever.
						clearAnonSecret(id);
						return null;
					}
					if (!res.ok) return null;
					const quiz = await res.json();
					if (quiz.user_id) {
						// Claimed from another tab: the account owns it now and the
						// secret proves nothing.
						clearAnonSecret(id);
						return null;
					}
					return quiz;
				} catch {
					// Offline or the API is down: keep the secret, just show less.
					return null;
				}
			})
		);
		browser_quizzes = results.filter((q): q is Row => q !== null);
	});

	// The search box only earns its space once the list is long enough to scan badly.
	const SEARCH_THRESHOLD = 6;
	let search_term = $state('');
	const fuse = $derived(
		new Fuse(account_quizzes, {
			keys: ['title', 'description', 'questions.title'],
			findAllMatches: true
		})
	);
	const shown_account_quizzes = $derived(
		search_term === '' ? account_quizzes : fuse.search(search_term).map((r) => r.item)
	);

	const remove = (id: string) => {
		account_quizzes = account_quizzes.filter((q) => q.id !== id);
		if (browser_quizzes) browser_quizzes = browser_quizzes.filter((q) => q.id !== id);
	};

	const delete_quiz = async (id: string) => {
		const anon_secret = getAnonSecret(id);
		delete row_errors[id];
		try {
			const res = await fetch(`/api/v1/quiz/delete/${id}`, {
				method: 'DELETE',
				headers: anon_secret ? { 'X-Anon-Secret': anon_secret } : {}
			});
			if (!res.ok) throw new Error(String(res.status));
		} catch {
			row_errors[id] = $t('my_quizzes.delete_failed');
			return;
		}
		clearAnonSecret(id);
		remove(id);
	};

	const claim_quiz = async (quiz: Row) => {
		const anon_secret = getAnonSecret(quiz.id);
		if (!anon_secret) return;
		claiming = quiz.id;
		delete row_errors[quiz.id];
		try {
			const res = await fetch(`/api/v1/quiz/claim/${quiz.id}`, {
				method: 'POST',
				headers: { 'X-Anon-Secret': anon_secret }
			});
			if (!res.ok) throw new Error(String(res.status));
		} catch {
			claiming = null;
			row_errors[quiz.id] = $t('my_quizzes.claim_failed');
			return;
		}
		claiming = null;
		clearAnonSecret(quiz.id);
		// The account list is loaded by the server, which knows about the claim and
		// the fields /get/public leaves out; reloading is simpler than patching them in.
		window.location.reload();
	};
</script>

<svelte:head>
	<title>frogQuiz - {$t('my_quizzes.title')}</title>
</svelte:head>

{#if signed_in}
	<CommandpaletteNotice />
{/if}

{#snippet row(quiz: Row, source: 'account' | 'browser')}
	{@const days = source === 'browser' ? anonDaysLeft(quiz.expire_at) : null}
	{@const count = question_count(quiz)}
	{@const draft = quiz_is_draft(quiz)}
	<li
		class="border-border bg-card flex flex-col gap-4 rounded-xl border p-4 sm:flex-row sm:items-center"
	>
		{#if quiz.cover_image}
			<div
				class="bg-muted relative hidden h-16 w-24 shrink-0 overflow-hidden rounded-md sm:block"
			>
				<MediaComponent
					src={quiz.cover_image}
					css_classes="absolute inset-0 h-full w-full object-cover"
				/>
			</div>
		{/if}

		<div class="min-w-0 flex-1">
			<!-- The view page is where a quiz's full set of actions lives; the title goes there. -->
			<a
				href="/view/{quiz.id}"
				class="block truncate font-medium underline-offset-4 hover:underline"
				>{quiz.title}</a
			>
			{#if quiz.description}
				<p class="text-muted-foreground line-clamp-2 text-sm">{quiz.description}</p>
			{/if}
			<div class="text-muted-foreground mt-2 flex flex-wrap items-center gap-2 text-xs">
				{#if source === 'account'}
					<Badge variant="secondary">
						{quiz.public ? $t('words.public') : $t('words.private')}
					</Badge>
				{/if}
				{#if draft}
					<Badge variant="outline">{$t('draft.badge')}</Badge>
				{/if}
				<span>
					{count}
					{count === 1 ? $t('words.question') : $t('words.question_plural')}
				</span>
				{#if days !== null}
					<span class="inline-flex items-center gap-1">
						<Clock class="size-3.5" aria-hidden="true" />
						{$t('device_quizzes.expires', { count: days })}
					</span>
				{/if}
			</div>
			{#if draft}
				<p id="draft-hint-{quiz.id}" class="text-muted-foreground mt-2 text-sm">
					{$t('draft.hint_owner')}
				</p>
			{/if}
			{#if row_errors[quiz.id]}
				<p class="text-destructive mt-2 text-sm" role="alert">{row_errors[quiz.id]}</p>
			{/if}
		</div>

		<div class="flex shrink-0 flex-wrap items-center gap-1.5">
			<Button
				disabled={draft}
				title={draft ? $t('draft.hint_owner') : undefined}
				aria-describedby={draft ? `draft-hint-${quiz.id}` : undefined}
				onclick={() => (start_game = quiz.id)}
			>
				<Play />
				{$t('words.play')}
			</Button>
			{#if source === 'browser' && signed_in}
				<Button
					variant="outline"
					disabled={claiming !== null}
					onclick={() => claim_quiz(quiz)}
				>
					{#if claiming === quiz.id}
						<LoaderCircle class="animate-spin" />
					{:else}
						<UserPlus />
					{/if}
					{$t('my_quizzes.claim')}
				</Button>
			{/if}
			<Button
				href="/edit?quiz_id={quiz.id}"
				variant="ghost"
				size="icon"
				title={$t('words.edit')}
				aria-label={$t('words.edit')}
			>
				<Pencil />
			</Button>
			{#if source === 'account'}
				<!-- Analytics hidden with Results for the MVP (D4). -->
				<Button
					variant="ghost"
					size="icon"
					title={$t('words.download')}
					aria-label={$t('words.download')}
					onclick={() => (download_id = quiz.id)}
				>
					<Download />
				</Button>
			{/if}
			<ConfirmAction
				title={$t('view_quiz_page.delete_confirm_title')}
				body={$t('view_quiz_page.delete_confirm')}
				confirmLabel={$t('words.delete')}
				cancelLabel={$t('words.cancel')}
				onconfirm={() => delete_quiz(quiz.id)}
				class="text-muted-foreground hover:text-destructive size-9 px-0"
			>
				<Trash2 aria-hidden="true" />
				<span class="sr-only">{$t('words.delete')}</span>
			</ConfirmAction>
		</div>
	</li>
{/snippet}

<div class="flex min-h-dvh flex-col">
	<div class="mx-auto w-full max-w-5xl grow px-5 pt-8 pb-20">
		<header class="flex flex-wrap items-end justify-between gap-4">
			<div class="min-w-0">
				<h1 class="text-3xl font-semibold tracking-tight">{$t('my_quizzes.title')}</h1>
				<p class="text-muted-foreground mt-1 text-sm">
					{signed_in
						? $t('my_quizzes.subtitle_signed_in')
						: $t('my_quizzes.subtitle_signed_out')}
				</p>
			</div>
			<Button href="/create" size="lg">
				<Plus />
				{$t('dashboard.create_quiz')}
			</Button>
		</header>

		{#if signed_in}
			<!-- The toolbar (Import, Results, Files library) is hidden for the MVP: D4, D6 and
			     D15 in MVP.md. Each route 404s through DISABLED_ROUTES; restore a button here
			     with its route. -->

			{#if account_quizzes.length === 0}
				<div
					class="border-border mt-10 flex flex-col items-center gap-4 rounded-xl border border-dashed px-6 py-16 text-center"
				>
					<p class="text-muted-foreground max-w-sm text-balance">
						{$t('my_quizzes.empty_signed_in')}
					</p>
					<Button href="/create">
						<Plus />
						{$t('dashboard.create_quiz')}
					</Button>
				</div>
			{:else}
				{#if account_quizzes.length > SEARCH_THRESHOLD}
					<div class="relative mt-8 max-w-sm">
						<Search
							class="text-muted-foreground pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2"
						/>
						<Input
							bind:value={search_term}
							class="pr-9 pl-9"
							aria-label={$t('dashboard.search_for_own_quizzes')}
							placeholder={$t('dashboard.search_for_own_quizzes')}
						/>
						{#if search_term !== ''}
							<button
								type="button"
								aria-label={$t('my_quizzes.clear_search')}
								class="text-muted-foreground hover:text-foreground focus-visible:ring-ring absolute top-1/2 right-2 -translate-y-1/2 rounded-sm p-1 focus-visible:ring-2 focus-visible:outline-none"
								onclick={() => (search_term = '')}
							>
								<X class="size-4" />
							</button>
						{/if}
					</div>
				{/if}

				<ul class="mt-8 flex flex-col gap-3">
					{#each shown_account_quizzes as quiz (quiz.id)}
						{@render row(quiz, 'account')}
					{/each}
				</ul>
			{/if}

			{#if browser_quizzes && browser_quizzes.length > 0}
				<section class="mt-12" aria-labelledby="browser-heading">
					<h2 id="browser-heading" class="text-lg font-semibold tracking-tight">
						{$t('my_quizzes.on_this_browser')}
					</h2>
					<p class="text-muted-foreground mt-1 text-sm">
						{$t('my_quizzes.on_this_browser_hint')}
					</p>
					<ul class="mt-4 flex flex-col gap-3">
						{#each browser_quizzes as quiz (quiz.id)}
							{@render row(quiz, 'browser')}
						{/each}
					</ul>
				</section>
			{/if}
		{:else}
			<div
				class="border-primary/40 bg-primary/10 mt-6 flex flex-col gap-3 rounded-xl border p-4 sm:flex-row sm:items-center"
			>
				<TriangleAlert class="text-primary size-5 shrink-0" aria-hidden="true" />
				<p class="min-w-0 flex-1 text-sm">{$t('my_quizzes.signed_out_notice')}</p>
				<Button href="/account/register" variant="outline" size="sm" class="shrink-0">
					<UserPlus />
					{$t('my_quizzes.create_account')}
				</Button>
			</div>

			{#if browser_quizzes === null}
				<div class="text-muted-foreground mt-16 flex justify-center">
					<LoaderCircle class="size-8 animate-spin" aria-label="Loading" />
				</div>
			{:else if browser_quizzes.length === 0}
				<div
					class="border-border mt-10 flex flex-col items-center gap-4 rounded-xl border border-dashed px-6 py-16 text-center"
				>
					<p class="text-muted-foreground max-w-sm text-balance">
						{$t('my_quizzes.empty_signed_out')}
					</p>
					<Button href="/create">
						<Plus />
						{$t('dashboard.create_quiz')}
					</Button>
				</div>
			{:else}
				<ul class="mt-8 flex flex-col gap-3">
					{#each browser_quizzes as quiz (quiz.id)}
						{@render row(quiz, 'browser')}
					{/each}
				</ul>
			{/if}
		{/if}
	</div>
	<Footer />
</div>

<!-- No {#if} wrapper: the popup is a Dialog and owns its own visibility from `quiz_id`. -->
<StartGamePopup bind:quiz_id={start_game} />
<DownloadQuiz bind:quiz_id={download_id} />
