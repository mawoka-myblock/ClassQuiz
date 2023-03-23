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

<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->

<svelte:head>
	<script src="https://js.stripe.com/v3/"></script>
</svelte:head>

{#if stripe}
	{#await get_payment_status()}
		<Spinner />
	{:then status}
		{#if status === 'succeeded'}
			<p>Success!</p>
		{:else if status === 'processing'}
			<p>Payment is processing.</p>
		{:else if status === 'requires_payment_method'}
			<p>Payment failed, try another method</p>
		{:else}
			<p>Something went wrong.</p>
		{/if}
	{/await}
{/if}
