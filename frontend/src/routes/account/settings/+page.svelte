<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import { DateTime } from 'luxon';
	import { UAParser } from 'ua-parser-js';
	import Spinner from '$lib/Spinner.svelte';
	import { onMount } from 'svelte';
	import BrownButton from '$lib/components/buttons/brown.svelte';

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
			window.location.assign('/account/login');
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
			window.location.assign('/account/login');
		}
	};

	onMount(() => {
		api_keys = get_api_keys();
	});

	const get_api_keys = async (): Promise<Array<string>> => {
		const res = await fetch('/api/v1/users/api_keys');
		const api_keys_temp = await res.json();
		console.log(api_keys_temp);
		return api_keys_temp;
	};

	let api_keys;

	const add_api_key = async () => {
		await fetch('/api/v1/users/api_keys', { method: 'POST' });
		api_keys = get_api_keys();
	};
	const formatDate = (date: string): string => {
		const dt = DateTime.fromISO(date);
		return dt.toLocaleString(DateTime.DATETIME_MED);
	};

	const delete_api_key = async (key: string) => {
		if (confirm('Do you really want to delete this API-Key?')) {
			await fetch(`/api/v1/users/api_keys?api_key=${key}`, { method: 'DELETE' });
			api_keys = get_api_keys();
		}
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
			window.location.assign('/account/login?returnTo=/account/settings');
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
		const json = await res.json();
		console.log(json.status, json.status === 'fail');
		if (json.status === 'fail') {
			alert('This feature is kinda broken...');
			return;
		} else {
			locationData = await res.json();
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

<svelte:head>
	<title>ClassQuiz - Settings</title>
</svelte:head>

{#await getUser()}
	<Spinner />
{:then user}
	<div class="w-full grid grid-cols-6">
		<div>
			<img
				class="rounded-md md:w-80"
				src="/api/v1/users/avatar"
				alt="Profile image of {user.username}"
			/>
			<div class="m-2 flex justify-center">
				<BrownButton href="/account/settings/avatar"
					>{$t('settings_page.change_avatar')}</BrownButton
				>
			</div>
		</div>
		<div class="grid grid-rows-2 col-start-2 col-end-7">
			<div class="grid grid-cols-2">
				<div>
					<h1 class="text-4xl font-bold my-2">{user.username}</h1>
					<p class="text-lg mb-6 md:max-w-lg">
						{$t('words.email')}: {user.email}
					</p>
				</div>
				<div class="p-4 flex justify-center">
					<div class="m-auto">
						<BrownButton href="/account/settings/security"
							>{$t('settings_page.security_settings')}
						</BrownButton>
						<BrownButton href="/account/controllers">ClassQuizController</BrownButton>
						<BrownButton href="/user/{user.id}">Public profile page</BrownButton>
					</div>
				</div>
			</div>
			<div>
				<form class="flex flex-col md:flex-row" on:submit|preventDefault={changePassword}>
					<label
						>{$t('settings_page.old_password')}:<input
							type="password"
							class="m-2 text-black rounded p-1 dark:bg-gray-700 dark:text-white"
							bind:value={changePasswordData.oldPassword}
						/></label
					>
					<label
						>{$t('settings_page.new_password')}:<input
							type="password"
							class="m-2 text-black rounded p-1 dark:bg-gray-700 dark:text-white"
							bind:value={changePasswordData.newPassword}
						/></label
					>
					<label
						>{$t('settings_page.repeat_password')}:<input
							type="password"
							class="m-2 text-black rounded p-1 dark:bg-gray-700 dark:text-white"
							bind:value={changePasswordData.newPasswordConfirm}
						/></label
					>
					<div class="my-auto">
						<BrownButton disabled={!passwordChangeDataValid} type="submit">
							{$t('settings_page.change_password_submit')}
						</BrownButton>
					</div>
				</form>
				<div>
					<div class="w-fit">
						<BrownButton on:click={add_api_key}
							>{$t('settings_page.add_api_key')}</BrownButton
						>
					</div>
					{#await api_keys}
						<Spinner />
					{:then keys}
						{#each keys as key}
							<div>
								{key.key}
								<div class="inline-block">
									<BrownButton
										on:click={() => {
											delete_api_key(key.key);
										}}
										>{$t('words.delete')}
									</BrownButton>
								</div>
							</div>
						{/each}
					{/await}
				</div>
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
					{$t('settings_page.last_seen')}
				</th>
				<th
					scope="col"
					class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
				>
					{$t('words.browser')}
				</th>
				<th
					scope="col"
					class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
				>
					{$t('settings_page.check_location')}
				</th>
				<th
					scope="col"
					class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
				>
					{$t('settings_page.delete_this_session')}
				</th>
				<th
					scope="col"
					class="py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400"
				>
					{$t('settings_page.this_session?')}
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
							}}>{$t('words.view')}</button
						>
					</td>
					<td
						class="py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400"
					>
						<button
							on:click={() => {
								deleteSession(session.id);
							}}>{$t('words.delete')}</button
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
				class="bg-black text-white rounded-t-lg px-1">{$t('words.close')}</button
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
