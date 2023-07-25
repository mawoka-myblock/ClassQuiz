<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->
<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import Spinner from '$lib/Spinner.svelte';

	let stripe;
	onMount(() => {
		stripe = Stripe(
			'pk_test_51JpvTnDhqZjJlPDmxZSbz9JyQnoVsHDRm8SAUp97wpzfniJDIpAlbdMz7rDPWMtt1CnhczbTKFapAUfAz3qyZcUs00dkYajTTi'
		);
	});

	const params = {
		payment_intent: $page.url.searchParams.get('payment_intent'),
		payment_intent_client_secret: $page.url.searchParams.get('payment_intent_client_secret'),
		redirect_status: $page.url.searchParams.get('redirect_status')
	};

	const get_payment_status = async (): Promise<string> => {
		const res = await stripe.retrievePaymentIntent(params.payment_intent_client_secret);
		return res.paymentIntent.status;
	};
</script>

<svelte:head>
	<script src="https://js.stripe.com/v3/"></script>
</svelte:head>

{#if stripe}
	<div class="flex w-full h-full">
		{#await get_payment_status()}
			<div class="m-auto">
				<Spinner />
			</div>
		{:then status}
			{#if status === 'succeeded'}
				<div class="m-auto flex flex-col w-full">
					<h1 class="text-6xl mx-auto">Success!</h1>
					<div class="mx-auto w-1/6">
						<!-- heroicons/legacy 24 outline/CheckCircle -->
						<svg
							aria-hidden="true"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
								stroke-linecap="round"
								stroke-linejoin="round"
							/>
						</svg>
					</div>
				</div>
			{:else if status === 'processing'}
				<div class="m-auto flex flex-col w-full">
					<h1 class="text-6xl mx-auto">You payment is processing</h1>
					<div class="mx-auto w-1/6">
						<!-- heroicons/legacy 24 outline/Clock -->
						<svg
							aria-hidden="true"
							fill="none"
							stroke="currentColor"
							stroke-width="2"
							viewBox="0 0 24 24"
							xmlns="http://www.w3.org/2000/svg"
						>
							<path
								d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
								stroke-linecap="round"
								stroke-linejoin="round"
							/>
						</svg>
					</div>
				</div>
			{:else if status === 'requires_payment_method'}
				<p>Payment failed, try another method</p>
			{:else}
				<p>Something went wrong.</p>
			{/if}
		{/await}
	</div>
{/if}
