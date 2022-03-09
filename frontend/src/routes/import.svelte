<script context='module' lang='ts'>
	export async function load({ session }) {
		if (!session.authenticated) {
			return {
				status: 302,
				redirect: '/account/login'
			};
		}
		return {
			props: {
				email: session.email
			}
		};
	}
</script>

<script lang='ts'>
	let url_input = '';

	let url_valid = false;
	let kahoot_regex = /^https:\/\/create\.kahoot\.it\/details\/([a-zA-Z-\d]{36})\/?$/;
	let is_loading = false;

	$: url_valid = kahoot_regex.test(url_input);

	const submit = async () => {
		if (!url_valid) {
			return;
		}
		is_loading = true;
		const regex_res = kahoot_regex.exec(url_input);
		console.log(regex_res);
		console.log(url_valid, url_input)
		const res = await fetch(`/api/v1/quiz/import/${regex_res[1]}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			}
		});

		if (res.status === 200) {
			window.location.href = '/overview';
		} else {
			alert('Error importing quiz');
		}
		is_loading = false;
	};
</script>

{#if is_loading}
	<svg class='h-8 w-8 animate-spin mx-auto my-20' viewBox='3 3 18 18'>
		<path
			class='fill-black'
			d='M12 5C8.13401 5 5 8.13401 5 12C5 15.866 8.13401 19 12 19C15.866 19 19 15.866 19 12C19 8.13401 15.866 5 12 5ZM3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12Z'
		/>
		<path
			class='fill-blue-100'
			d='M16.9497 7.05015C14.2161 4.31648 9.78392 4.31648 7.05025 7.05015C6.65973 7.44067 6.02656 7.44067 5.63604 7.05015C5.24551 6.65962 5.24551 6.02646 5.63604 5.63593C9.15076 2.12121 14.8492 2.12121 18.364 5.63593C18.7545 6.02646 18.7545 6.65962 18.364 7.05015C17.9734 7.44067 17.3403 7.44067 16.9497 7.05015Z'
		/>
	</svg>
{:else}

	<form on:submit|preventDefault={submit}>
		<input type='text' class="text-black w-2/5" bind:value={url_input} />
		<button type='submit' disabled={!url_valid}>Submit</button>
	</form>
{/if}