<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { onDestroy } from 'svelte';
	import { getLocalization } from '$lib/i18n';
	import { Button } from '$lib/components/ui/button';
	import Volume2 from '@lucide/svelte/icons/volume-2';
	import VolumeX from '@lucide/svelte/icons/volume-x';
	import Play from '@lucide/svelte/icons/play';
	import Track from '$lib/assets/music/1-128.mp3';

	const { t } = getLocalization();

	interface Props {
		/** The lobby is the only screen that plays; the parent unmounts this to stop it. */
		playing?: boolean;
	}

	let { playing = true }: Props = $props();

	const STORE_KEY = 'frogquiz_music';
	const DEFAULT_VOLUME = 40;

	// A room gets the music by default, because that is the point of a lobby -- but the
	// choice is remembered, so the host who turned it off once never fights it again.
	const stored = (() => {
		try {
			const raw = localStorage.getItem(STORE_KEY);
			return raw ? JSON.parse(raw) : null;
		} catch {
			return null;
		}
	})();

	let wanted = $state(stored?.on ?? true);
	let volume = $state(typeof stored?.volume === 'number' ? stored.volume : DEFAULT_VOLUME);
	// Browsers refuse to start audio without a gesture, and the host reached this screen
	// through one -- but a reload has none, so the control says "press to play" rather
	// than lying about being on.
	let blocked = $state(false);

	let audio: HTMLAudioElement | undefined;

	const remember = () => {
		try {
			localStorage.setItem(STORE_KEY, JSON.stringify({ on: wanted, volume }));
		} catch {
			/* private window, blocked storage: the choice just does not outlive the tab */
		}
	};

	const start = async () => {
		if (!audio) {
			audio = new Audio(Track);
			audio.loop = true;
		}
		audio.volume = volume / 100;
		try {
			await audio.play();
			blocked = false;
		} catch {
			blocked = true;
		}
	};

	$effect(() => {
		if (playing && wanted) {
			start();
		} else if (audio) {
			audio.pause();
		}
	});

	$effect(() => {
		if (audio) audio.volume = volume / 100;
	});

	// Cutting a loop dead is the one thing that sounds like a bug rather than an ending.
	onDestroy(() => {
		if (!audio) return;
		const a = audio;
		audio = undefined;
		const step = a.volume / 10;
		const fade = setInterval(() => {
			a.volume = Math.max(0, a.volume - step);
			if (a.volume <= 0.01) {
				clearInterval(fade);
				a.pause();
			}
		}, 40);
	});
</script>

<!-- Bottom left: the lobby's own controls are top left and the host's actions top right,
     and this is the one control in the room nobody should have to hunt for when a
     conversation starts. -->
<div
	class="border-border/70 bg-card/90 fixed bottom-4 left-4 z-30 flex items-center gap-2 rounded-full border py-1.5 pr-3 pl-1.5 shadow-sm backdrop-blur"
>
	<Button
		variant="ghost"
		size="icon"
		class="rounded-full"
		aria-label={wanted && !blocked ? $t('play_page.music_off') : $t('play_page.music_on')}
		title={wanted && !blocked ? $t('play_page.music_off') : $t('play_page.music_on')}
		onclick={() => {
			if (blocked) {
				start();
				wanted = true;
			} else {
				wanted = !wanted;
			}
			remember();
		}}
	>
		{#if blocked}
			<Play />
		{:else if wanted}
			<Volume2 />
		{:else}
			<VolumeX />
		{/if}
	</Button>
	<label class="flex items-center gap-2">
		<span class="sr-only">{$t('play_page.music_volume')}</span>
		<input
			type="range"
			min="0"
			max="100"
			step="5"
			bind:value={volume}
			onchange={remember}
			disabled={!wanted || blocked}
			class="accent-primary w-24 cursor-pointer disabled:cursor-not-allowed disabled:opacity-40"
		/>
	</label>
</div>
