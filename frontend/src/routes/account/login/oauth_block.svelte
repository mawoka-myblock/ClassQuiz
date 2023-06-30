<!--
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
-->

<script lang="ts">
	import { github_auth_enabled, google_auth_enabled, custom_oauth_name } from '$lib/config';
</script>

{#if google_auth_enabled}
	<div class="flex items-center justify-center pt-4">
		<a
			href="/api/v1/users/oauth/google/login"
			class="inline-flex w-fit p-1 rounded-lg border-gray-500 border border-2 hover:bg-[#4285F4] transition"
			>Google Login

			<svg
				class="h-6 w-6 ml-4 dark:fill-gray-300"
				role="img"
				viewBox="0 0 24 24"
				xmlns="http://www.w3.org/2000/svg"
				><title> Google</title>
				<path
					d="M12.48 10.92v3.28h7.84c-.24 1.84-.853 3.187-1.787 4.133-1.147 1.147-2.933 2.4-6.053 2.4-4.827 0-8.6-3.893-8.6-8.72s3.773-8.72 8.6-8.72c2.6 0 4.507 1.027 5.907 2.347l2.307-2.307C18.747 1.44 16.133 0 12.48 0 5.867 0 .307 5.387.307 12s5.56 12 12.173 12c3.573 0 6.267-1.173 8.373-3.36 2.16-2.16 2.84-5.213 2.84-7.667 0-.76-.053-1.467-.173-2.053H12.48z"
				/>
			</svg>
		</a>
	</div>
{/if}
{#if github_auth_enabled}
	<div class="flex items-center w-full justify-center pt-4">
		<a
			href="/api/v1/users/oauth/github/login"
			class="inline-flex w-fit p-1 rounded-lg border-gray-500 border border-2 hover:bg-[#181717] transition hover:text-white group"
			>GitHub Login
			<svg
				class="h-6 w-6 ml-4 dark:fill-gray-300 group-hover:fill-white transition"
				role="img"
				viewBox="0 0 24 24"
				xmlns="http://www.w3.org/2000/svg"
				><title> GitHub</title>
				<path
					d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"
				/>
			</svg>
		</a>
	</div>
{/if}
{#if custom_oauth_name}
	<div class="flex items-center w-full justify-center pt-4">
		<a
			href="/api/v1/users/oauth/custom/login"
			class="inline-flex w-fit p-1 rounded-lg border-gray-500 border border-2 hover:bg-[#F78C40] transition hover:text-white group"
			>OpenID Login
			<svg
				class="h-6 w-6 ml-4 dark:fill-gray-300 group-hover:fill-white transition"
				role="img"
				viewBox="0 0 24 24"
				xmlns="http://www.w3.org/2000/svg"
				><title>OpenID</title>
				<path
					d="M14.54.889l-3.63 1.773v18.17c-4.15-.52-7.27-2.78-7.27-5.5 0-2.58 2.8-4.75 6.63-5.41v-2.31C4.42 8.322 0 11.502 0 15.332c0 3.96 4.74 7.24 10.91 7.78l3.63-1.71V.888m.64 6.724v2.31c1.43.25 2.71.7 3.76 1.31l-1.97 1.11 7.03 1.53-.5-5.21-1.87 1.06c-1.74-1.06-3.96-1.81-6.45-2.11z"
				/>
			</svg>
		</a>
	</div>
{/if}
