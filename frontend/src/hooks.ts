import * as cookie from 'cookie';
import fetch from 'node-fetch';
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

/** @type {import('@sveltejs/kit').Handle} */
export async function handle({ event, resolve }) {
	const cookies = cookie.parse(event.request.headers.get('cookie') || '');
	const regex_token = /^Bearer (.*)$/gm.exec(cookies.access_token);
	if (regex_token === null) {
		event.locals.token = null;
	} else {
		event.locals.token = regex_token[1];
	}
	event.locals.rememberme = cookies.rememberme_token;

	return await resolve(event);
}

/** @type {import('@sveltejs/kit').GetSession} */
export async function getSession(event) {
	const redis_res = await redis.get(event.locals.token);
	let user_email: string;
	if (redis_res === null) {
		const res = await fetch(`${process.env.API_URL}/api/v1/users/check`, {
			headers: {
				Cookie: `access_token=Bearer ${event.locals.token}`
			}
		});
		if (res.ok) {
			const json = await res.json();
			//@ts-ignore
			user_email = json.email;
		} else {
			user_email = null;
		}
	} else {
		user_email = redis_res;
	}
	if (user_email === null) {
		return {
			authenticated: false,
			token: event.locals.token,
			email: null
		};
	} else {
		return {
			authenticated: true,
			token: event.locals.token,
			email: user_email
		};
	}
}
