<script context="module" lang="ts">
	export async function load({ session }) {
		if (!session.authenticated) {
			return {
				status: 302,
				redirect: '/account/login?returnTo=/account/settings'
			};
		}
		return {
			props: {
				email: session.email
			}
		};
	}
</script>

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import { DateTime } from 'luxon';
	import { UAParser } from 'ua-parser-js';
	import Spinner from '$lib/Spinner.svelte';

	const { t } = getLocalization();

	let showMap = false;

	interface UserAccount {
		id: string;
		email: string;
		username: string;
		verified: boolean;
		created_at: string;
	}

	interface ChangePasswordData {
		oldPassword: string;
		newPassword: string;
		newPasswordConfirm: string;
	}

	let changePasswordData: ChangePasswordData = {
		oldPassword: '',
		newPassword: '',
		newPasswordConfirm: ''
	};

	let locationData;
	let this_session;

	let passwordChangeDataValid = false;
	const checkPasswords = (data: ChangePasswordData): void => {
		passwordChangeDataValid =
			data.newPassword === data.newPasswordConfirm &&
			data.newPassword.length >= 8 &&
			data.oldPassword !== data.newPassword &&
			data.oldPassword !== '';
	};
	$: checkPasswords(changePasswordData);
	const changePassword = async () => {
		if (!passwordChangeDataValid) {
			return;
		}
		const res = await fetch('/api/v1/users/password/update', {
			method: 'PUT',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				old_password: changePasswordData.oldPassword,
				new_password: changePasswordData.newPassword
			})
		});
		if (res.status === 200) {
			alert('Password changed');
			window.location.replace('/account/login');
		} else {
			alert('Password change failed');
		}
	};

	const getUser = async (): Promise<UserAccount> => {
		const response = await fetch('/api/v1/users/me', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		});
		if (response.status === 200) {
			return await response.json();
		} else {
			window.location.replace('/account/login');
		}
	};
	const formatDate = (date: string): string => {
		const dt = DateTime.fromISO(date);
		return dt.toLocaleString(DateTime.DATETIME_MED);
	};

	const getSessions = async () => {
		const res = await fetch('/api/v1/users/sessions/list');
		if (res.status === 200) {
			const res2 = await fetch('/api/v1/users/session');
			if (res2.status === 200) {
				this_session = await res2.json();
			}
			return await res.json();
		} else {
			window.location.replace('/account/login?returnTo=/account/settings');
		}
		return await res.json();
	};

	const getFormattedUserAgent = (userAgent: string): string => {
		const parser = new UAParser(userAgent);
		const result = parser.getResult();
		return `${result.browser.name} ${result.browser.version} (${result.os.name})`;
	};

	const checkLocation = async (session_ip: string) => {
		const res = await fetch(`/api/v1/utils/ip-lookup/${session_ip}`);
		if (res.status === 200) {
			locationData = await res.json();
			console.log(locationData.lat, locationData.lon);
			showMap = true;
		}
	};

	const deleteSession = async (session_id: string) => {
		const res = await fetch(`/api/v1/users/sessions/${session_id}`, {
			method: 'DELETE'
		});
		if (res.status === 200) {
			window.location.reload();
		}
	};
</script>

{#await getUser()}
	<Spinner />
{:then user}
	<div class="w-full">
		<div class="sm:flex space-x-7 md:items-start items-center">
			<div class="mb-4">
				<img
					class="rounded-md md:w-80"
					src="https://cdn.statically.io/avatar/shape=rounded/{user.username}"
					alt="Profile image of {user.username}"
				/>
			</div>
			<div>
				<h1 class="text-slate-100 text-4xl font-bold my-2">{user.username}</h1>
				<p class="text-slate-100 text-lg mb-6 md:max-w-lg">
					{$t('words.email')}: {user.email}
				</p>
				<!-- TODO: Add translation -->
				<form class="flex flex-col md:flex-row" on:submit|preventDefault={changePassword}>
					<label
						>Old Password:<input
							type="password"
							class="m-2 text-black"
							bind:value={changePasswordData.oldPassword}
						/></label
					>
					<label
						>New Password:<input
							type="password"
							class="m-2 text-black"
							bind:value={changePasswordData.newPassword}
						/></label
					>
					<label
						>New Password again:<input
							type="password"
							class="m-2 text-black"
							bind:value={changePasswordData.newPasswordConfirm}
						/></label
					>
					<button
						class="border-2 px-2 py-1 rounded-md border-black text-slate-100 hover:bg-amber-700 hover:text-indigo-100 transition duration-75 disabled:cursor-not-allowed disabled:opacity-50"
						disabled={!passwordChangeDataValid}
						type="submit"
					>
						Change Password!
					</button>
				</form>
			</div>
		</div>
	</div>
{/await}
{#await getSessions()}
	<Spinner />
{:then sessions}
	<table class="min-w-full">
		<thead class="bg-gray-50 dark:bg-gray-700">
			<tr>
				<th
					scope="col"
					class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
				>
					{$t('overview_page.created_at')}
				</th>
				<th
					scope="col"
					class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
				>
					Last seen
				</th>
				<th
					scope="col"
					class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
				>
					Browser
				</th>
				<th
					scope="col"
					class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
				>
					Check location
				</th>
				<th
					scope="col"
					class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
				>
					Delete this session
				</th>
				<th
					scope="col"
					class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
				>
					This session?
				</th>
			</tr>
		</thead>
		<tbody>
			{#each sessions as session}
				<tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
					<td
						class="py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400"
					>
						{formatDate(session.created_at)}
					</td>
					<td
						class="py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400"
					>
						{formatDate(session.last_seen)}
					</td>
					<td
						class="py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400"
					>
						{getFormattedUserAgent(session.user_agent)}
					</td>
					<td
						class="py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400"
					>
						<button
							on:click={() => {
								checkLocation(session.ip_address);
							}}>View</button
						>
					</td>
					<td
						class="py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400"
					>
						<button
							on:click={() => {
								deleteSession(session.id);
							}}>Delete</button
						>
					</td>
					<td
						class="py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400"
					>
						{#if session.id === this_session.id}
							✅
						{:else}
							❌
						{/if}
					</td>
				</tr>
			{/each}
		</tbody>
	</table>
{/await}

<div class="w-5/6 h-5/6 z-20 absolute top-10 pt-16 left-28" class:hidden={!showMap}>
	{#if showMap}
		{#await import('$lib/Map.svelte')}
			<Spinner />
		{:then c}
			<button
				on:click={() => {
					showMap = false;
				}}
				class="bg-black text-white rounded-t-lg px-1">Close</button
			>
			<div class="w-full h-full">
				<svelte:component
					this={c.default}
					lat={locationData.lat}
					lng={locationData.lon}
					markerText={'Somewhere here was this session registered.'}
				/>
			</div>
		{/await}
	{/if}
</div>
