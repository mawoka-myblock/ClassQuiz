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

	import tippy from 'sveltejs-tippy';

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
		console.log(url_valid, url_input);
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

<!--{#if is_loading}
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
{:else}-->

<!--	<form on:submit|preventDefault={submit}>
		<input type='text' class="text-black w-2/5" bind:value={url_input} />
		<button type='submit' disabled={!url_valid}>Submit</button>
	</form>-->
<div class='flex items-center justify-center h-full px-4'>
	<div>
		<span class='p-4' />

		<div
			class='lg:w-[64rem] lg:max-w-[64rem] w-screen max-w-screen mx-auto overflow-hidden bg-white rounded-lg shadow-md dark:bg-gray-800'

		>
			<div class='px-6 py-4'>
				<h2 class='text-3xl font-bold text-center text-gray-700 dark:text-white'>
					ClassQuiz
				</h2>

				<h3 class='mt-1 text-xl font-medium text-center text-gray-600 dark:text-gray-200'>
					Welcome Back
				</h3>

				<p class='mt-1 text-center text-gray-500 dark:text-gray-400'>
					Login or create account
				</p>

				<form on:submit|preventDefault={submit}>
					<div class='w-full mt-4'>
						<div class='dark:bg-gray-800 bg-white p-4 rounded-lg'>
							<div class='relative bg-inherit w-full'>
								<input
									id='url'
									bind:value={url_input}
									name='email'
									type='url'
									class='w-full peer bg-transparent h-10 rounded-lg text-gray-700 dark:text-white placeholder-transparent ring-2 px-2 ring-gray-500 focus:ring-sky-600 focus:outline-none focus:border-rose-600'
									placeholder='https://create.kahoot.it/details/something'
									class:ring-red-700={!url_valid}
									class:ring-green-600={url_valid}
								/>
								<label
									for='url'
									class='absolute cursor-text left-0 -top-3 text-sm text-gray-700 dark:text-white bg-inherit mx-1 px-1 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-500 peer-placeholder-shown:top-2 peer-focus:-top-3 peer-focus:text-sky-600 peer-focus:text-sm transition-all'
								>
									URL
								</label>
							</div>
						</div>

						<div class='flex items-center justify-between mt-4'>
							<span></span>

							<button
								class='px-4 py-2 leading-5 text-white transition-colors duration-200 transform bg-gray-700 rounded hover:bg-gray-600 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50'
								disabled={!url_valid}
								type='submit'
							>
								{#if is_loading}
									<svg
										class='h-4 w-4 animate-spin mx-auto my-20'
										viewBox='3 3 18 18'
									>
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
									Submit
								{/if}
							</button>
						</div>
					</div>
				</form>
			</div>
			<div
				class='flex items-center justify-center py-4 text-center bg-gray-50 dark:bg-gray-700'
			>
				<span class='text-sm text-gray-600 dark:text-gray-200'
				>Need help?
				</span>

				<a
					href='/docs/import-from-kahoot'
					class='mx-2 text-sm font-bold text-blue-500 dark:text-blue-400 hover:underline'
				>Visit the docs</a
				>
			</div>
		</div>
	</div>
</div>
<!--{/if}-->