<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	// import AudioPlayer from '$lib/play/audio_player.svelte';
	import ControllerCodeDisplay from '$lib/components/controller/code.svelte';
	import { getLocalization } from '$lib/i18n';
	import { fade, fly } from 'svelte/transition';
	import { flip } from 'svelte/animate';
	import { Button } from '$lib/components/ui/button';
	import ConfirmAction from '$lib/components/ConfirmAction.svelte';
	import X from '@lucide/svelte/icons/x';
	import { SocketGameControls } from '$lib/play/admin/socket_game_controls.ts';
	import type { IGameState } from '$lib/play/admin/game_state';

	interface Props {
		game_pin: string;
		game_state: IGameState;
		socket_game_controls: SocketGameControls;
		cqc_code: string;
	}

	let {
		game_pin,
		game_state = $bindable(),
		socket_game_controls,
		cqc_code = $bindable()
	}: Props = $props();

	let fullscreen_open = $state(false);
	const { t } = getLocalization();

	if (cqc_code === 'null') {
		cqc_code = null;
	}
</script>

<!-- The lobby used to have no way out but closing the tab, which left the PIN live and
     the joined players waiting on a game that would never start. -->
<div class="fixed top-3 left-3 z-30">
	<ConfirmAction
		title={$t('admin_page.cancel_confirm_title')}
		body={$t('admin_page.cancel_confirm_body')}
		confirmLabel={$t('admin_page.cancel_game')}
		cancelLabel={$t('admin_page.keep_waiting')}
		onconfirm={() => socket_game_controls.end_game()}
	>
		<X />
		{$t('admin_page.cancel_game')}
	</ConfirmAction>
</div>

<div class="fq-stage">
	<!-- The join details are the whole point of this screen, so they get the
	     centre and the largest type rather than being split across three
	     unaligned columns. -->
	<div class="flex flex-col items-center gap-8 md:flex-row md:items-center md:gap-12">
		<div class="flex flex-col items-center gap-3 md:items-start">
			<p class="text-lg text-muted-foreground md:text-xl">
				{$t('play_page.join_description', {
					url:
						window.location.host === 'frogquiz.xyz'
							? 'frogquiz.xyz/play'
							: `${window.location.host}/play`,
					pin: game_pin
				})}
			</p>
			<p class="text-sm font-medium uppercase tracking-[0.2em] text-muted-foreground">
				{$t('words.pin')}
			</p>
			<p class="fq-pin select-all font-mono font-bold tracking-[0.12em] tabular-nums">
				{game_pin}
			</p>
		</div>

		<button
			type="button"
			onclick={() => (fullscreen_open = true)}
			aria-label={$t('play_page.join_by_entering_code')}
			class="rounded-2xl bg-white p-3 shadow-xl ring-1 ring-black/5 transition-transform hover:scale-[1.03] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring"
		>
			<img
				alt="QR code to join the game"
				src="/api/v1/utils/qr/{game_pin}"
				class="size-40 md:size-56"
			/>
		</button>
	</div>

	{#if cqc_code}
		<div class="flex flex-col items-center gap-2">
			<p class="text-muted-foreground">{$t('play_page.join_by_entering_code')}</p>
			<ControllerCodeDisplay code={cqc_code} />
		</div>
	{/if}

	<Button
		size="lg"
		class="h-14 rounded-xl px-10 text-lg font-semibold shadow-lg transition-transform hover:scale-[1.02] active:scale-[0.98] disabled:scale-100"
		disabled={game_state.players.length < 1}
		onclick={() => socket_game_controls.start_game()}
	>
		{$t('admin_page.start_game')}
	</Button>

	<div class="flex w-full max-w-5xl flex-col items-center gap-4">
		<p class="text-xl text-muted-foreground" aria-live="polite">
			<!-- i18next picks _one / _other from the count; the old _plural suffix was
			     i18next v20's and printed the raw key on the projector. -->
			{$t('play_page.players_waiting', { count: game_state.players.length ?? 0 })}
		</p>

		{#if game_state.players.length > 0}
			<ul class="flex flex-wrap items-center justify-center gap-2.5">
				{#each game_state.players as player (player.username)}
					<li animate:flip={{ duration: 250 }}>
						<button
							type="button"
							title={$t('words.kick')}
							aria-label="{$t('words.kick')}: {player.username}"
							onclick={() =>
								socket_game_controls.kick_player(
									player.username,
									game_state.players
								)}
							class="group rounded-full border border-border bg-card px-4 py-2 text-lg font-medium shadow-sm
								transition-all hover:border-destructive hover:text-destructive
								focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring
								motion-safe:animate-in motion-safe:fade-in motion-safe:zoom-in-95"
							in:fly|global={{ y: 8, duration: 220 }}
						>
							<span class="group-hover:line-through">{player.username}</span>
						</button>
					</li>
				{/each}
			</ul>
		{/if}
	</div>
</div>

{#if fullscreen_open}
	<!-- Was `w-screen h-screen`. 100vw includes the vertical scrollbar, so the overlay
	     overflowed by its width on any page that scrolls, and 100vh is the wrong number
	     on a phone. inset-0 is how a fixed overlay fills the viewport. -->
	<div
		class="fixed inset-0 z-50 flex bg-black/50 p-2"
		transition:fade|global={{ duration: 80 }}
		onclick={() => (fullscreen_open = false)}
		tabindex="0"
		role="button"
		aria-label="Close modal"
		onkeydown={(e) =>
			e.key === 'Enter' || e.key === ' '
				? () => {
						fullscreen_open = false;
					}
				: null}
	>
		<!-- bg-white here and on the thumbnail above is deliberate and must not become a
		     token: a QR code needs a light quiet zone to scan, in either theme. -->
		<img
			alt="QR code to join the game"
			src="/api/v1/utils/qr/{game_pin}"
			class="object-contain rounded-sm m-auto h-full bg-white"
		/>
	</div>
{/if}
