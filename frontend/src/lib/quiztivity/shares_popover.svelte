<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { getLocalization } from '$lib/i18n';
	import Spinner from '$lib/Spinner.svelte';
	import { DateTime } from 'luxon';
	import { browser } from '$app/environment';
	import SmallPopover from '$lib/components/popover/smalltop.svelte';
	import { PopoverTypes } from '$lib/components/popover/smalltop';
	import { onMount } from 'svelte';
	import { fade, fly } from 'svelte/transition';

	const { t } = getLocalization();
	export let open = false;
	export let id;
	let popover_open = false;
	const load_shares = async (): Promise<{
		id: string;
		name?: string;
		expire_in?: number;
		quiztivity: { id: string };
		user: { id: string };
	}> => {
		const res = await fetch(`/api/v1/quiztivity/${id}/shares`);
		return await res.json();
	};
	const copyToClipboard = (str) => {
		try {
			navigator.clipboard.writeText(str);
		} catch {
			console.log('Async Clipboard not supported');
			const el = document.createElement('textarea');
			el.value = str;
			el.setAttribute('readonly', '');
			el.style.position = 'absolute';
			el.style.left = '-9999px';
			document.body.appendChild(el);
			const selected =
				document.getSelection().rangeCount > 0
					? document.getSelection().getRangeAt(0)
					: false;
			el.select();
			document.execCommand('copy');
			document.body.removeChild(el);
			if (selected) {
				document.getSelection().removeAllRanges();
				document.getSelection().addRange(<Range>selected);
			}
		} finally {
			popover_open = true;
			setTimeout(() => {
				popover_open = false;
			}, 2000);
		}
	};

	const on_parent_click = (e: Event) => {
		if (e.target !== e.currentTarget) {
			return;
		}
		open = false;
	};
	const close_start_game_if_esc_is_pressed = (key: KeyboardEvent) => {
		if (key.code === 'Escape') {
			open = false;
		}
	};
	onMount(() => {
		document.body.addEventListener('keydown', close_start_game_if_esc_is_pressed);
	});
	let never_expires_checked = true;
	let selected_date = undefined;
	const create_share = async () => {
		if (!selected_date && !never_expires_checked) {
			return;
		}
		console.log(selected_date);
		await fetch('/api/v1/quiztivity/shares/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				name: undefined,
				quiztivity: id,
				expire_in: never_expires_checked
					? undefined
					: Math.floor(Math.abs(new Date() - new Date(selected_date)) / 1000 / 60)
			})
		});
		loaded_shares = load_shares();
	};
	let loaded_shares = load_shares();

	const delete_share = async (id: string) => {
		if (!confirm('Do you really want to delete this Share?')) {
			return;
		}
		await fetch(`/api/v1/quiztivity/shares/${id}`, { method: 'DELETE' });
		loaded_shares = load_shares();
	};

	const share_available = (): boolean => {
		try {
			return browser
				? !navigator.canShare({
						title: 'title',
						url: `${window.location.origin}/quiztivity`
				  })
				: false;
		} catch {
			return false;
		}
	};
	let add_shares_open = false;
</script>

<SmallPopover bind:open={popover_open} type={PopoverTypes.Copy} />
<div
	class="fixed w-full h-full top-0 flex bg-black bg-opacity-50 z-50"
	on:click={on_parent_click}
	transition:fade|local={{ duration: 100 }}
>
	<div
		class="m-auto bg-white dark:bg-gray-600 rounded shadow-2xl flex p-4 flex-col w-2/3 h-5/6 gap-2 overflow-scroll"
	>
		<div class="flex justify-center flex-col">
			<BrownButton
				on:click={() => {
					add_shares_open = !add_shares_open;
				}}>{$t('quiztivity.editor.shares.add_new_share')}</BrownButton
			>
			{#if add_shares_open}
				<form
					class="flex justify-center p-2 border-b-2 border-l-2 border-r-2 border-[#B07156] flex-col gap-2"
					transition:fly|local={{ duration: 100, y: -10 }}
					on:submit|preventDefault={create_share}
				>
					<div class="grid grid-cols-2">
						<input
							type="datetime-local"
							class="dark:text-black transition-all mx-auto"
							disabled={never_expires_checked}
							bind:value={selected_date}
						/>
						<div class="mx-auto">
							<label for="cb">{$t('quiztivity.editor.shares.never_expires')}</label>
							<input type="checkbox" id="cb" bind:checked={never_expires_checked} />
						</div>
					</div>
					<BrownButton type="submit" disabled={!selected_date && !never_expires_checked}
						>{$t('words.submit')}</BrownButton
					>
				</form>
			{/if}
		</div>
		{#await loaded_shares}
			<Spinner />
		{:then shares}
			{#each shares as share}
				<div class="grid grid-cols-4 w-full gap-2" in:fade={{ duration: 50 }}>
					<!--                    <p>{share.name ?? "..."}</p>-->
					<div class="w-full mx-auto">
						<BrownButton
							flex={true}
							disabled={share_available()}
							on:click={() => {
								navigator.share({
									title: 'Quiztivity on ClassQuiz',
									text: 'Play this Quiztivity now on ClassQuiz!',
									url: `${window.location.origin}/quiztivity/share/${share.id}?ref=share`
								});
							}}
						>
							<!-- heroicons/share -->
							<svg
								aria-hidden="true"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								viewBox="0 0 24 24"
								xmlns="http://www.w3.org/2000/svg"
								class="w-5 h-5"
							>
								<path
									d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</BrownButton>
					</div>
					<div class="w-full mx-auto">
						<BrownButton
							flex={true}
							on:click={() => {
								copyToClipboard(
									`${window.location.origin}/quiztivity/share/${share.id}?ref=copy`
								);
							}}
						>
							<!-- heroicons/ClipboardCopy -->
							<svg
								aria-hidden="true"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								class="w-5 h-5"
								viewBox="0 0 24 24"
								xmlns="http://www.w3.org/2000/svg"
							>
								<path
									d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"
									stroke-linecap="round"
									stroke-linejoin="round"
								/>
							</svg>
						</BrownButton>
					</div>
					<p class="m-auto">
						{#if share.expire_in}
							{$t('quiztivity.editor.shares.expires_on', {
								date: DateTime.now()
									.plus({ minutes: share.expire_in })
									.toJSDate()
									.toLocaleString()
							})}
						{:else}
							{$t('quiztivity.editor.shares.never_expires')}
						{/if}
					</p>
					<div class="w-fit my-auto ml-auto">
						<BrownButton
							on:click={() => {
								delete_share(share.id);
							}}>{$t('words.delete')}</BrownButton
						>
					</div>
				</div>
			{/each}
		{/await}
	</div>
</div>
