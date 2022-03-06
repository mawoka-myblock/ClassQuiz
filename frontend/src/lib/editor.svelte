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

	export let data: Data;
	export let submit_button_text = "Create";

	const empty_question: Question = {
		question: '',
		time: '20',
		answers: [{
			right: false,
			answer: ''
		}]
	};

	const empty_answer: Answer = {
		right: false,
		answer: ''
	};
</script>


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
						on:click={() => {data.questions[index_question].answers = [...data.questions[index_question].answers, {...empty_answer}]}}>
					Add new answer
				</button>
			</div>
		{/each}
		<button class='text-left' on:click={() => {data.questions = [...data.questions, {...empty_question}]}}>
			Add new
			question
		</button>

	</div>

{/each}
<button type='submit'>{submit_button_text}</button>
