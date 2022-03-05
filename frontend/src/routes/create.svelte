<script context='module' lang='ts'>
	export async function load({ session, url }) {
		if (!session.authenticated) {
			return {
				status: 302,
				redirect: '/account/login'
			};
		}
		const token = url.searchParams.get('token');
		const pin = url.searchParams.get('pin');
		let auto_connect = url.searchParams.get('connect') !== null;
		if (token === null || pin === null) {
			auto_connect = false;
		}
		return {
			props: {
				game_pin: pin === null ? '' : pin,
				game_token: token === null ? '' : token,
				auto_connect: auto_connect
			}
		};
	}
</script>

<script lang='ts'>
	interface Data {
		public: boolean;
		title: string;
		description: string;
		questions: Question[];
	}

	interface Question {
		question: string;
		time: string;
		answers: Answer[];
	}

	interface Answer {
		right: boolean;
		answer: string;
	}

	let empty_question: Question = {
		question: '',
		time: '20',
		answers: [{
			right: false,
			answer: ''
		}]
	};

	let empty_answer: Answer = {
		right: false,
		answer: ''
	};
	let data: Data;
	const from_localstorage = localStorage.getItem('create_game');
	if (from_localstorage === null) {
		data = {
			description: '',
			public: false,
			title: '',
			questions: [{ question: '', time: '20', answers: [{ right: false, answer: '' }] }]
		};
	} else {
		data = JSON.parse(from_localstorage);
	}


	const submit = async () => {
		const res = await fetch('/api/v1/quiz/create', {
			method: 'POST',
			body: JSON.stringify(data)
		});
		if (res.status === 401) {
			localStorage.setItem('create_game', JSON.stringify(data));
			window.location.href = '/account/login';
		}
	};

</script>

<form on:submit|preventDefault={submit} class='grid grid-cols-1 gap-2'>
	<label>
		<input type='checkbox' bind:checked={data.public}>
		Public?
	</label>
	<label>
		<input type='text' placeholder='Title' bind:value={data.title} class='text-black' />
		Title
	</label>
	<label>
		<textarea placeholder='Description' bind:value={data.description} class='text-black'></textarea>
		Description
	</label>
	{#each data.questions as question, index_question}
		<div class='ml-8 grid grid-cols-1 gap-2 m-2 border border-black border-2'>
			<h1 class='text-3xl'>Question {index_question + 1}</h1>

			<label>
				<input type='text' placeholder='Question' bind:value={question.question} class='text-black' />
				Question
			</label>
			<label>
				<input type='text' placeholder='20' bind:value={question.time} class='text-black' />
				Time in seconds
			</label>
			{#each question.answers as answer, index_answer}
				<div class='ml-8 grid grid-cols-1 gap-2 m-2 border border-black border-2'>
					<h1 class='text-3xl'>Answer {index_answer + 1}</h1>
					<p>Answer: {index_answer} Question: {index_question}</p>
					<label>
						<input type='text' placeholder='Answer'
							   bind:value={data.questions[index_question].answers[index_answer].answer}
							   class='text-black' />
						Answer
					</label>
					<label>
						<input type='checkbox' bind:checked={answer.right} class='text-black' />
						Right?
					</label>
					<button class='text-left'
							on:click={() => {data.questions[index_question].answers = [...data.questions[index_question].answers, empty_answer]}}>
						Add new answer
					</button>
				</div>
			{/each}
			<button class='text-left' on:click={() => {data.questions = [...data.questions, empty_question]}}>Add new
				question
			</button>

		</div>

	{/each}
	<button type='submit'>Create</button>
</form>