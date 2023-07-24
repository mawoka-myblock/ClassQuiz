<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->
<script lang="ts">
	import { Elements, PaymentElement } from 'svelte-stripe';
	import { onMount } from 'svelte';
	import BrownButton from '$lib/components/buttons/brown.svelte';
	import { page } from '$app/stores';
	import Spinner from '$lib/Spinner.svelte';

	const clientSecret = $page.url.searchParams.get('clientSecret');
	const subscription_type = $page.url.searchParams.get('type');

	let elements;
	let processing = false;
	let error = null;

	let primary_color = '#d6edc9';

	let stripe;
	onMount(() => {
		try {
			stripe = Stripe(
				'pk_test_51JpvTnDhqZjJlPDmxZSbz9JyQnoVsHDRm8SAUp97wpzfniJDIpAlbdMz7rDPWMtt1CnhczbTKFapAUfAz3qyZcUs00dkYajTTi'
			);
		} catch (e) {
			window.location.reload();
		}
		if (
			localStorage.theme === 'dark' ||
			(!('theme' in localStorage) &&
				window.matchMedia('(prefers-color-scheme: dark)').matches)
		) {
			primary_color = '#4e6e58';
		}
	});
	const submit = async () => {
		if (processing) return;
		processing = true;
		const res = await stripe.confirmPayment({
			elements,
			confirmParams: {
				return_url: `${window.location.origin}/account/billing/success`
			}
		});
		if (res.error) {
			error = res.error;
			processing = false;
		}
	};
	const annual_string = "You're about to subscribe to the annual plan for 20 €/$ a year.";
	const monthly_string = "You're about to subscribe to the monthly plan for 2 €/$ a month.";
</script>

<!--
  - This Source Code Form is subject to the terms of the Mozilla Public
  - License, v. 2.0. If a copy of the MPL was not distributed with this
  - file, You can obtain one at https://mozilla.org/MPL/2.0/.
  -->

<svelte:head>
	<script src="https://js.stripe.com/v3/"></script>
</svelte:head>
{#if error}
	<p class="error">{error.message} Please try again.</p>
{/if}
{#if stripe}
	<div class="flex justify-center h-full">
		<div class="w-1/3 m-auto">
			<div class="rounded-lg p-3 bg-gray-600">
				<h1 class="text-white text-center text-3xl mb-2">Pay for your plan.</h1>
				<p class="text-center text-white">
					{#if subscription_type === 'ANNUAL'}
						{annual_string}
					{:else if subscription_type === 'MONTHLY'}
						{monthly_string}
					{:else}
						DO NOT CONTINUE, SOMETHING WENT WRONG.
					{/if}
				</p>
				<Elements
					{stripe}
					{clientSecret}
					theme="night"
					labels="floating"
					bind:elements
					variables={{ colorPrimary: primary_color }}
				>
					<form on:submit|preventDefault={submit}>
						<PaymentElement />
						<div class="mt-2">
							<BrownButton disabled={processing} type="submit">
								{#if processing}
									Loading...
								{:else}
									Pay
								{/if}
							</BrownButton>
						</div>
					</form>
				</Elements>
			</div>
		</div>
	</div>
{/if}
