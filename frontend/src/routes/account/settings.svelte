<script context="module" lang="ts">
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

<script lang="ts">
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

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
</script>

{#await getUser()}
	<svg class="h-8 w-8 animate-spin mx-auto my-20" viewBox="3 3 18 18">
		<path
			class="fill-black"
			d="M12 5C8.13401 5 5 8.13401 5 12C5 15.866 8.13401 19 12 19C15.866 19 19 15.866 19 12C19 8.13401 15.866 5 12 5ZM3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12Z"
		/>
		<path
			class="fill-blue-100"
			d="M16.9497 7.05015C14.2161 4.31648 9.78392 4.31648 7.05025 7.05015C6.65973 7.44067 6.02656 7.44067 5.63604 7.05015C5.24551 6.65962 5.24551 6.02646 5.63604 5.63593C9.15076 2.12121 14.8492 2.12121 18.364 5.63593C18.7545 6.02646 18.7545 6.65962 18.364 7.05015C17.9734 7.44067 17.3403 7.44067 16.9497 7.05015Z"
		/>
	</svg>
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
