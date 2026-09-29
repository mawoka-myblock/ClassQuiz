<!--
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { moveItem, selectionAfterMove } from '$lib/editor/reorder';
	import type { EditorData } from '../quiz_types';
	import { getLocalization } from '$lib/i18n';
	import { isQuestionComplete } from '$lib/editor/question_complete';
	import { editorValidation } from '$lib/editor/validation.svelte';
	import { htmlToPlainText } from '$lib/sanitize';
	import AddNewQuestionPopup from '$lib/editor/AddNewQuestionPopup.svelte';
	import { Button } from '$lib/components/ui/button';
	import Settings2 from '@lucide/svelte/icons/settings-2';
	import Plus from '@lucide/svelte/icons/plus';

	interface Props {
		data: EditorData;
		selected_question: number;
	}

	let { data = $bindable(), selected_question = $bindable(-1) }: Props = $props();

	const { t } = getLocalization();

	let add_open = $state(false);
	let scroller: HTMLElement | undefined = $state();

	// Long-press to pick a question up, then drag to reposition it. This is the idiom a
	// filmstrip already has on a phone (Keynote, Slides, Canva), and it is the only one
	// where the control is the thing being reordered rather than a button somewhere else
	// pointing at it. The press delay is what separates "I am moving this" from "I am
	// scrolling the strip", which is why a plain drag handle does not work in a
	// horizontal scroller.
	//
	// Dragging is never the only way: WCAG 2.5.7 asks for a single-pointer alternative,
	// and the Move buttons in the question toolbar are it. Keyboard users get those too.
	const PRESS_MS = 350;
	const SLOP_PX = 8;

	let dragging = $state<number | null>(null);
	let press_timer: ReturnType<typeof setTimeout> | null = null;
	let start = { x: 0, y: 0 };
	let pressed_index: number | null = null;

	const cancel_press = () => {
		if (press_timer) clearTimeout(press_timer);
		press_timer = null;
		pressed_index = null;
	};

	const on_pointer_down = (e: PointerEvent, index: number) => {
		if (e.pointerType === 'mouse' && e.button !== 0) return;
		pressed_index = index;
		start = { x: e.clientX, y: e.clientY };
		press_timer = setTimeout(() => {
			dragging = index;
			selected_question = index;
			// Take the pointer so the gesture keeps arriving here even once the chip has
			// moved out from under the finger.
			(e.target as HTMLElement)?.closest('button')?.setPointerCapture?.(e.pointerId);
			navigator.vibrate?.(10);
		}, PRESS_MS);
	};

	const on_pointer_move = (e: PointerEvent) => {
		if (dragging === null) {
			// Moved before the press landed, so this was a scroll after all.
			if (
				pressed_index !== null &&
				Math.hypot(e.clientX - start.x, e.clientY - start.y) > SLOP_PX
			) {
				cancel_press();
			}
			return;
		}
		e.preventDefault();
		const over = document
			.elementFromPoint(e.clientX, e.clientY)
			?.closest<HTMLElement>('[data-index]');
		const to = over ? Number(over.dataset.index) : NaN;
		if (Number.isNaN(to) || to === dragging) return;
		// Same helper as the sidebar's drag, so the two reordering paths cannot drift.
		selected_question = selectionAfterMove(selected_question, dragging, to);
		data.questions = moveItem(data.questions, dragging, to);
		dragging = to;
	};

	const on_pointer_up = () => {
		cancel_press();
		dragging = null;
	};

	// Keep the chosen chip in view when the selection moves, including when it moves
	// because a question was reordered out from under the thumb.
	$effect(() => {
		selected_question;
		if (dragging !== null) return; // it is already under the finger
		scroller
			?.querySelector('[data-selected="true"]')
			?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
	});
</script>

<!-- The narrow-screen form of the question rail. It is a sibling of the canvas in the
     editor shell, not an overlay: the quiz's shape and its order have to stay visible
     while you edit, which is exactly what a drawer takes away. Same job as the
     vertical aside at lg and up, laid out along the other axis. -->
<nav
	class="border-border bg-muted/30 flex shrink-0 items-center gap-2 border-b px-2 py-2 lg:hidden"
	aria-label={$t('editor.show_questions')}
>
	<!-- overflow-x:auto computes overflow-y to auto as well, so anything drawn outside
	     a child's border box is clipped. That is what cut the top and bottom off the
	     selected chip's ring. The rings are inset now, so there is nothing outside the
	     box to clip, and the scroller keeps a little padding so the focus ring has
	     somewhere to land too. -->
	<div
		bind:this={scroller}
		class="flex min-w-0 flex-1 items-stretch gap-2 overflow-x-auto p-1 scroll-smooth"
		class:touch-none={dragging !== null}
		onpointermove={on_pointer_move}
		onpointerup={on_pointer_up}
		onpointercancel={on_pointer_up}
	>
		<button
			type="button"
			data-selected={selected_question === -1}
			class="border-border bg-card flex min-h-11 shrink-0 items-center gap-1.5 rounded-lg border px-3 text-xs font-medium transition
				{selected_question === -1 ? 'ring-primary bg-primary/5 ring-2 ring-inset' : ''}"
			onclick={() => (selected_question = -1)}
		>
			<Settings2 class="size-3.5 shrink-0" />
			{$t('editor.quiz_setup')}
		</button>

		{#each data.questions as question, index (index)}
			{@const selected = index === selected_question}
			<button
				type="button"
				data-selected={selected}
				data-index={index}
				class="border-border bg-card flex min-h-11 w-36 shrink-0 flex-col items-start justify-center gap-0.5 rounded-lg border px-3 py-2 text-left transition select-none
					{selected ? 'ring-primary bg-primary/5 ring-2 ring-inset' : ''}
					{dragging === index ? 'ring-primary z-10 scale-105 shadow-lg ring-2' : ''}
					{dragging !== null && dragging !== index ? 'opacity-60' : ''}"
				aria-grabbed={dragging === index}
				onclick={() => (selected_question = index)}
				onpointerdown={(e) => on_pointer_down(e, index)}
				oncontextmenu={(e) => dragging !== null && e.preventDefault()}
			>
				<span class="flex w-full items-center gap-1.5">
					<span class="text-muted-foreground text-xs tabular-nums">{index + 1}</span>
					{#if editorValidation.shown && !isQuestionComplete(question)}
						<span
							class="bg-destructive size-1.5 shrink-0 rounded-full"
							title={$t('editor.question_incomplete')}
						></span>
						<span class="sr-only">{$t('editor.question_incomplete')}</span>
					{/if}
				</span>
				<span class="w-full truncate text-xs">
					{#if question.question === ''}
						<span class="text-muted-foreground italic">{$t('editor.no_title')}</span>
					{:else}
						<!-- Plain text, not {@html}: the title is rich text from the same editor as
						     the quiz title, and its <p> wrapper is a block element that would break
						     this one-line chip out of its truncate. Nothing is lost at text-xs. -->
						{htmlToPlainText(question.question)}
					{/if}
				</span>
			</button>
		{/each}
	</div>

	<Button
		type="button"
		variant="outline"
		size="icon"
		class="shrink-0"
		aria-label={$t('editor.add_new_question')}
		onclick={() => (add_open = true)}
	>
		<Plus />
	</Button>
</nav>

<!-- No instructional line under the strip. The lift, the shadow and the other chips
     fading back are the feedback, and the Move buttons in the question toolbar are the
     discoverable path for anyone who does not try the gesture. Telling people to "drag
     to move, release to place" is the app explaining itself to someone already doing
     it. Screen readers still get it: the held chip carries aria-grabbed. -->

<!-- No {#if} wrapper: Dialog.Root owns its own visibility. -->
<AddNewQuestionPopup bind:questions={data.questions} bind:open={add_open} bind:selected_question />
