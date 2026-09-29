<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import * as Dialog from '$lib/components/ui/dialog/index.js';
	import * as Collapsible from '$lib/components/ui/collapsible/index.js';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Switch } from '$lib/components/ui/switch';
	import Spinner from '$lib/Spinner.svelte';
	import { getLocalization } from '$lib/i18n';
	import { getAnonSecret } from '$lib/anon_quiz';

	const { t } = getLocalization();
	let { quiz_id = $bindable() } = $props();
	let loading = $state(false);
	let custom_field = $state('');
	// The custom field is an extra question every player is asked on the join screen,
	// and the host's answer to it is shown to them as the heading above that box. It
	// used to be pre-filled from localStorage on mount, so a value typed once -- in
	// practice somebody's own email -- silently re-applied to every game started in
	// that browser from then on, and every player saw it labelling a mystery input.
	// It is now an explicit opt-in that starts empty for every game, and nothing is
	// persisted: the only thing the stored value was ever used for was that
	// auto-prefill, so keeping the write would leave a value nothing reads. The
	// feature itself, and its whole wire path, is untouched.
	let custom_field_enabled = $state(false);
	let randomized_answers = $state(false);
	let error = $state<string | null>(null);
	// Set when the failure looks like "you are not signed in" rather than a real
	// error, so the message can offer a way back rather than just saying no.
	let offer_login = $state(false);

	// Clearing on the way out keeps the value that gets sent equal to the value that
	// is visible: a host who types something and then changes their mind would
	// otherwise still ship it, since the input is only hidden, not unmounted.
	const on_custom_field_toggle = (enabled: boolean) => {
		custom_field_enabled = enabled;
		if (!enabled) {
			custom_field = '';
		}
	};

	// This string is rendered to every player as the heading above the extra box, so
	// bound it. The same 200 as MAX_CUSTOM_FIELD_LENGTH in
	// frogquiz/socket_server/models.py, which bounds the players' answers -- the
	// server does not bound the prompt itself, hence the client-side cap.
	const MAX_CUSTOM_FIELD_LENGTH = 200;

	// Mode picker (Normal / Old-School) was cut: Old-School was never used, and Normal
	// is now the only option. The API still accepts game_mode=normal, so it can come
	// back without a backend change if that's ever wanted.
	const start_game = async (id: string) => {
		loading = true;
		error = null;
		offer_login = false;
		const anon_secret = getAnonSecret(id);
		const headers: Record<string, string> = anon_secret ? { 'X-Anon-Secret': anon_secret } : {};

		// custom_field is whatever the host typed and used to be interpolated straight
		// into the query string. An `&` in it started a new parameter and truncated the
		// value; a `#` made everything after it a fragment, so the server never saw it.
		const params = new URLSearchParams({
			captcha_enabled: 'False',
			game_mode: 'kahoot',
			custom_field,
			cqcs_enabled: 'False',
			randomize_answers: randomized_answers ? 'True' : 'False'
		});
		const res = await fetch(`/api/v1/quiz/start/${encodeURIComponent(id)}?${params}`, {
			method: 'POST',
			headers
		});

		if (res.status === 200) {
			const data = await res.json();
			window.location.assign(
				`/admin?token=${data.game_id}&pin=${data.game_pin}&connect=1&cqc_code=${data.cqc_code}`
			);
			return;
		}

		loading = false;

		// This used to bounce to /account/login on *any* non-200 whenever there was no
		// anonymous secret -- so a 500, a rate limit, or a quiz deleted in another tab
		// all threw a signed-in host out of the page as though their session had
		// expired. Only an explicit 401/403 means that.
		if (res.status === 401 || res.status === 403) {
			window.location.assign('/account/login?returnTo=/my-quizzes');
			return;
		}

		// Without a secret the caller is treated as anonymous by the API, so a 404 here
		// is ambiguous: the quiz may be gone, or the session may have lapsed and this is
		// somebody's own quiz they can no longer prove they own. Say so and offer the
		// way back rather than guessing and navigating away.
		if (res.status === 404 && !anon_secret) {
			error = $t('start_game.start_failed_signed_out');
			offer_login = true;
			return;
		}

		error = $t('start_game.start_failed');
	};

	const open = $derived(quiz_id !== null);
	const on_open_change = (is_open: boolean) => {
		if (!is_open) {
			quiz_id = null;
		}
		// A failure left over from the last quiz would otherwise still be showing the
		// next time the dialog opens.
		error = null;
		offer_login = false;
		loading = false;
		// Every game starts from the same blank slate, including the next one opened
		// from this same dashboard without a reload.
		custom_field_enabled = false;
		custom_field = '';
	};
</script>

<Dialog.Root {open} onOpenChange={on_open_change}>
	<Dialog.Content class="gap-5">
		<Dialog.Header>
			<Dialog.Title>{$t('start_game.start_game')}</Dialog.Title>
		</Dialog.Header>

		<!-- The switch is the only thing that opens this, so the collapsible is driven
		     rather than self-controlled; onOpenChange keeps the two in step if bits-ui
		     ever closes it itself (escape, a forced remount). -->
		<Collapsible.Root open={custom_field_enabled} onOpenChange={on_custom_field_toggle}>
			<div class="flex items-center gap-3">
				<Switch
					id="custom-field-enabled"
					checked={custom_field_enabled}
					onCheckedChange={on_custom_field_toggle}
				/>
				<Label for="custom-field-enabled">{$t('result_page.custom_field')}</Label>
			</div>
			<Collapsible.Content>
				<div class="grid min-w-0 gap-2 pt-3">
					<Label for="custom-field" class="sr-only">
						{$t('result_page.custom_field')}
					</Label>
					<Input
						id="custom-field"
						bind:value={custom_field}
						maxlength={MAX_CUSTOM_FIELD_LENGTH}
						placeholder="Phone Number or Email"
					/>
				</div>
			</Collapsible.Content>
		</Collapsible.Root>

		<div class="flex items-center gap-3">
			<Switch id="randomize-answers" bind:checked={randomized_answers} />
			<Label for="randomize-answers">{$t('start_game.randomize_answers')}</Label>
		</div>

		{#if error}
			<div class="text-destructive text-sm" role="alert">
				<p>{error}</p>
				{#if offer_login}
					<Button
						href="/account/login?returnTo=/my-quizzes"
						variant="link"
						class="text-destructive h-auto p-0"
					>
						{$t('words.login')}
					</Button>
				{/if}
			</div>
		{/if}

		<Dialog.Footer>
			<Button
				onclick={() => {
					start_game(quiz_id);
				}}
				disabled={loading}
			>
				{#if loading}
					<Spinner my_20={false} />
				{:else}
					{$t('start_game.start_game')}
				{/if}
			</Button>
		</Dialog.Footer>
	</Dialog.Content>
</Dialog.Root>
