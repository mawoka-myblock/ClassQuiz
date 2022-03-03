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
	import type { QuizData } from '../app';
	import { DateTime } from 'luxon';


	const getData = async (): Promise<Array<QuizData>> => {
		const res = await fetch('/api/v1/quiz/list');
		const data = await res.json();
		return data;
	};

	const formatDate = (date: string): string => {
		const dt = DateTime.fromISO(date);
		return dt.toLocaleString(DateTime.DATETIME_MED);
	};

	const startGame = async (id: string): Promise<void> => {
		console.log('start game', id);
		const res = await fetch(`/api/v1/quiz/start/${id}`, {
			method: 'POST'
			// headers: {
			// 	'Content-Type': 'application/json'
			// }
		});
		if (res.status !== 200) {
			throw new Error('Failed to start game');
		}
		const data = await res.json();
		window.location.replace(`/admin?token=${data.game_id}&pin=${data.game_pin}&connect=1`);
	};


</script>

{#await getData()}
	<p>Loading...</p>

{:then quizzes}

	<div class='flex flex-col w-fit'>
		<div class='overflow-x-auto sm:-mx-8 lg:-mx-8'>
			<div class='inline-block py-2 min-w-full sm:px-6 lg:px-8'>
				<div class='overflow-hidden shadow-md sm:rounded-lg'>
					<table class='min-w-full'>
						<thead class='bg-gray-50 dark:bg-gray-700'>
						<tr>
							<th
								scope='col'
								class='py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400'
							>
								Title
							</th>
							<th
								scope='col'
								class='py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400'
							>
								Created at
							</th>
							<th
								scope='col'
								class='py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400'
							>
								Question count
							</th>
							<th
								scope='col'
								class='py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400'
							>
								Play
							</th>
							<th
								scope='col'
								class='py-3 px-6 text-xs font-medium tracking-wider text-left text-gray-700 uppercase dark:text-gray-400'
							>
								Edit
							</th>
						</tr>
						</thead>
						<tbody>
						<!-- Product 1 -->
						{#each quizzes as quiz}

							<tr class='bg-white border-b dark:bg-gray-800 dark:border-gray-700'>
								<td
									class='py-4 px-6 text-sm font-medium text-gray-900 whitespace-nowrap dark:text-white'
								>
									{quiz.title}
								</td>
								<td
									class='py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400'
								>
									{formatDate(quiz.created_at)}
								</td>
								<td
									class='py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400'
								>
									{quiz.questions.length}
								</td>
								<td
									class='py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400'
								>
									<button on:click={() => {startGame(quiz.id)}} class='border border-green-600'>
										Start
									</button>
								</td>
								<td
									class='py-4 px-6 text-sm text-gray-500 whitespace-nowrap dark:text-gray-400'
								>
									<a href='/edit/{quiz.id}'>Edit</a>
								</td>
							</tr>
						{/each}
						</tbody>
					</table>
				</div>
			</div>
		</div>
	</div>
{:catch err}
	<p>{err}</p>
{/await}
