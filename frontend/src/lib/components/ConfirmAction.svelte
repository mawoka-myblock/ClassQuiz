<!--
SPDX-FileCopyrightText: 2026 frogQuiz contributors

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	// A button that asks before it acts. For the ways out of a live game -- cancel,
	// end, leave -- each of which can't be undone and is easy to hit by accident on a
	// projector remote or a phone.
	import type { Snippet } from 'svelte';
	import { Button, buttonVariants, type ButtonVariant } from '$lib/components/ui/button/index.js';
	import * as AlertDialog from '$lib/components/ui/alert-dialog/index.js';

	interface Props {
		title: string;
		body: string;
		confirmLabel: string;
		cancelLabel: string;
		onconfirm: () => void;
		variant?: ButtonVariant;
		class?: string;
		/** The trigger's content: an icon and a label. */
		children: Snippet;
	}

	let {
		title,
		body,
		confirmLabel,
		cancelLabel,
		onconfirm,
		variant = 'ghost',
		class: className = '',
		children
	}: Props = $props();

	let open = $state(false);
</script>

<AlertDialog.Root bind:open>
	<AlertDialog.Trigger class={buttonVariants({ variant, size: 'sm', class: className })}>
		{@render children()}
	</AlertDialog.Trigger>
	<AlertDialog.Content class="max-w-md">
		<AlertDialog.Header>
			<AlertDialog.Title>{title}</AlertDialog.Title>
			<AlertDialog.Description>{body}</AlertDialog.Description>
		</AlertDialog.Header>
		<AlertDialog.Footer>
			<AlertDialog.Cancel>{cancelLabel}</AlertDialog.Cancel>
			<Button
				variant="destructive"
				onclick={() => {
					open = false;
					onconfirm();
				}}
			>
				{confirmLabel}
			</Button>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>
