export async function load({ url }) {
	const error = url.searchParams.get('error');
	return {
		error
	};
}
