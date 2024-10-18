<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->


<!--
This should be okay, right?
-->
<script lang="ts">
	import { onMount } from 'svelte';
	import { tinykeys } from '$lib/tinykeys';
	import { fade } from 'svelte/transition';
	import MiniSearch from 'minisearch';

	let open = false;
	let input = '';
	let bg_text = '';
	let title_ms: MiniSearch;
	let command_ms: MiniSearch;
	let selected: null | number = null;

	// eslint-disable-next-line no-unused-vars
	type ActionFunction = (args: string[]) => void;
	const actions: {
		id: number;
		title: string;
		description?: string;
		command?: string;
		args?: string[];
		action: ActionFunction;
	}[] = [
		{
			id: 0,
			title: 'Close CommandPalette',
			description: 'Closes CommandPalette',
			command: 'close',
			action: () => close_cp(undefined)
		},
		{
			id: 1,
			title: 'Create Quiz',
			description: 'Opens editor to create a new quiz',
			command: 'newquiz',
			args: ['title'],
			action: (args) => window.location.assign(`/create?title=${args.join(' ')}`)
		},
		{
			id: 2,
			title: 'Import a Quiz',
			description: 'Opens the import page',
			command: 'import',
			args: ['url'],
			action: (args) => window.location.assign(`/import?url=${args?.[0] ?? ''}`)
		},
		{
			id: 3,
			title: 'Create Quiztivity',
			description: 'Opens the editor for quiztivities',
			command: 'newquiztivity',
			args: ['title'],
			action: (args) => window.location.assign(`/quiztivity/create?title=${args.join(' ')}`)
		},
		{
			id: 4,
			title: 'View Results',
			description: 'Opens the Results viewer',
			command: 'results',
			action: () => window.location.assign('/results')
		},
		{
			id: 5,
			title: 'Explore Quizzes',
			description: 'Opens the Explore-page',
			command: 'explore',
			action: () => window.location.assign('/explore')
		},
		{
			id: 6,
			title: 'Dashboard',
			description: 'Go to Dashboard',
			command: 'dash',
			action: () => window.location.assign('/dashboard')
		},
		{
			id: 7,
			title: 'Docs',
			description: 'Go to documentation',
			command: 'docs',
			action: () => window.location.assign('/docs')
		},
		{
			id: 8,
			title: 'Settings',
			description: 'Opens the Settings page',
			command: 'settings',
			action: () => window.location.assign('/account/settings')
		}
	];
	let visible_items = actions;

	const toggle_open = (e: KeyboardEvent | undefined) => {
		e.preventDefault();
		open = !open;
		console.log('TOGGLE!');
	};

	const close_cp = (e: KeyboardEvent | undefined) => {
		if (e) {
			e.preventDefault();
		}
		open = false;
	};

	const close_on_outside = (e: Event) => {
		if (e.target == e.currentTarget) {
			open = false;
		}
	};

	const execute_action = () => {
		let args = [];
		const entry = visible_items[selected];
		if (input.startsWith('/')) {
			const tokens = input.split(' ');
			args = tokens.slice(1);
		}
		console.log(args);
		entry.action(args);
	};

	const search = (term: string) => {
		if (!command_ms || !title_ms) {
			return;
		}
		if (term === '' || term === '/') {
			selected = 0;
			visible_items = actions;
			bg_text = '';
			return;
		}
		let suggestions;
		let res;
		if (term.startsWith('/')) {
			term = term.substring(1);
			suggestions = command_ms.autoSuggest(term, { boost: { command: 2 }, prefix: true });
			res = command_ms.search(term, { boost: { command: 2 }, prefix: true });
			bg_text = suggestions[0]?.suggestion;
			bg_text ??= '';
			bg_text = `/${bg_text}`;
		} else {
			suggestions = title_ms.autoSuggest(term, { boost: { command: 2 }, prefix: true });
			res = title_ms.search(term, { boost: { command: 2 }, prefix: true });
			bg_text = suggestions[0]?.suggestion;
			bg_text ??= '';
		}

		visible_items = [];

		console.log(res);
		for (const quiz_data of res) {
			visible_items.push(actions[quiz_data.id]);
		}
		visible_items = visible_items;
		if (visible_items.length === 1) {
			selected = 0;
		}
		if (visible_items.length === 0) {
			selected = null;
		}
	};

	const autocomplete_on_tab = (e: KeyboardEvent) => {
		e.preventDefault();
		input = bg_text;
	};

	const on_arrow_down = (e: KeyboardEvent) => {
		e.preventDefault();
		if (visible_items.length < 1) {
			return;
		}
		if (selected + 1 === visible_items.length) {
			return;
		}
		selected += 1;
	};
	const on_arrow_up = (e: KeyboardEvent) => {
		e.preventDefault();
		if (visible_items.length < 1) {
			return;
		}
		if (selected === 0) {
			return;
		}
		selected -= 1;
	};

	const on_enter = (e: KeyboardEvent) => {
		if (selected === null) {
			return;
		}
		execute_action();
		input = '';
	};

	$: search(input);
	// $: input = lower_input(input)
	$: input = input.toLowerCase();
	onMount(async () => {
		tinykeys(window, {
			'$mod+k': toggle_open,
			Escape: close_cp,
			Tab: autocomplete_on_tab,
			ArrowDown: on_arrow_down,
			ArrowUp: on_arrow_up,
			Enter: on_enter
		});
		title_ms = new MiniSearch<any>({
			fields: ['title'],
			storeFields: ['id']
		});
		title_ms.addAll(actions);
		command_ms = new MiniSearch<any>({
			fields: ['command'],
			storeFields: ['id']
		});
		command_ms.addAll(actions);
	});
</script>

{#if open}
	<div
		class="fixed top-0 left-0 w-screen h-screen flex bg-black bg-opacity-50 z-50"
		on:click={close_on_outside}
        on:keyup={close_on_outside}
		transition:fade={{ duration: 60 }}
	>
		<div class="m-auto w-1/3 h-2/3 rounded bg-black flex flex-col">
			<div class="grid grid-cols-1 grid-rows-1 border-b border-b-white">
				<p
					class="col-start-1 row-start-1 w-full p-4 outline-none bg-gray-700 rounded-t text-gray-400"
				>
					{bg_text}
				</p>
				<input
					type="text"
					class="col-start-1 row-start-1 bg-transparent w-full p-4 outline-none bg-gray-700 rounded"
					bind:value={input}
				/>
			</div>
			<div class="flex flex-col p-2 gap-2 overflow-scroll">
				{#each visible_items as vi, i}
					<div
						transition:fade|local={{ duration: 60 }}
						class="p-2 transition rounded"
						class:bg-[#B07156]={selected === i}
						class:bg-gray-700={selected !== i}
						on:mouseenter={() => (selected = i)}
						on:mousedown={execute_action}
					>
						<div class="flex">
							<h3 class="text-lg my-auto">{vi.title}</h3>
							<p
								class="font-mono my-auto ml-auto h-fit bg-black bg-opacity-50 rounded p-0.5"
							>
								/{vi.command}
								{#if vi.args}
									{#each vi.args as arg}
										&lbrace;<span class="text-indigo-400">{arg}</span
										>&rbrace;{/each}
								{/if}
							</p>
						</div>
						<p class="text-sm">{vi.description}</p>
					</div>
				{/each}
			</div>
		</div>
	</div>
{/if}
