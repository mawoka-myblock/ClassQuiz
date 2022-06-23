import { DateTime } from 'luxon';
import * as Sentry from '@sentry/browser';

const gen_salt = (l: number): string => {
	const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
	const charLength = chars.length;
	let result = '';
	for (let i = 0; i < l; i++) {
		result += chars.charAt(Math.floor(Math.random() * charLength));
	}
	return result;
};

export const mint = async (
	resource: string,
	bits = 19,
	// now = null,
	ext = '',
	saltchars = 8,
	stamp_seconds = false
): Promise<string> => {
	const ver = '1';
	let ts;
	if (stamp_seconds) {
		ts = DateTime.now().toFormat('yyMMddHHmmss');
	} else {
		ts = DateTime.now().toFormat('yyMMdd');
	}
	const hex_digits = Math.ceil(bits / 4);
	const zeros = '0'.repeat(hex_digits);
	const salt = gen_salt(saltchars);
	const challenge = `${ver}:${bits}:${ts}:${resource}:${ext}:${salt}`;
	let counter = 0;
	let result: string;
	const t0 = performance.now();
	// eslint-disable-next-line no-constant-condition
	while (true) {
		const data = new TextEncoder().encode(`${challenge}:${counter.toString(16)}`);
		const hashBuffer = await crypto.subtle.digest('SHA-1', data);
		const hashArray = Array.from(new Uint8Array(hashBuffer));
		const digest = hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
		if (digest.slice(0, hex_digits) == zeros) {
			result = counter.toString(16);
			break;
		}
		counter += 1;
	}
	const t1 = performance.now();
	const transaction = Sentry.startTransaction({ name: 'calculatedHasCash' });
	const span = transaction.startChild({
		op: 'hashcash',
		data: {
			milliseconds_taken: t0 - t1,
			bits: bits
		}
	});
	span.finish();
	transaction.finish();
	return `${challenge}:${result}`;
};
