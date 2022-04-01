<script lang="ts">
	import { getLocalization } from '$lib/i18n';

	const { t } = getLocalization();

	interface Data {
		public: boolean;
		title: string;
		description: string;
		questions: Question[];
	}

	interface Question {
		question: string;
		time: string;
		image?: string;
		answers: Answer[];
	}

	interface Answer {
		right: boolean;
		answer: string;
	}

	export let data: Data;
	export let submit_button_text = 'Create';
	let imgur_links_valid = false;

	const empty_question: Question = {
		question: '',
		time: '20',
		image: '',
		answers: [
			{
				right: false,
				answer: ''
			}
		]
	};

	const checkIfAllQuestionImagesComplyWithRegex = (questions: Array<Question>) => {
		let NoteverythingValid = false;
		// const regex = /^https:\/\/i\.imgur\.com\/.{7}.(jpg|png|gif)$/;
		// const local_regex = /^http(|s):\/\/\w*(|:)\d*\/api\/v1\/storage\/download\/.{36}--.{36}$/g;
		const main_regex =
			/^(http(|s):\/\/\w*(|:)\d*\/api\/v1\/storage\/download\/.{36}--.{36}|https:\/\/i\.imgur\.com\/.{7}.(jpg|png|gif))$/;
		for (let i = 0; i < questions.length; i++) {
			const question = questions[i];

			if (question.image && !main_regex.test(question.image)) {
				NoteverythingValid = true;
			}
		}
		return NoteverythingValid;
	};

	$: imgur_links_valid = checkIfAllQuestionImagesComplyWithRegex(data.questions);

	const empty_answer: Answer = {
		right: false,
		answer: ''
	};
</script>

<label class="pl-2 w-2/6 flex gap-2 flex-row">
	<input type="checkbox" class="w-fit" bind:checked={data.public} />
	<span class="w-fit">{$t('words.public')}?</span>
</label>
<label class="pl-2 flex flex-row gap-2 w-3/5">
	<span class="w-fit">{$t('words.title')}:</span>
	<input
		type="text"
		placeholder={$t('words.title')}
		bind:value={data.title}
		class="text-black bg-inherit border-dotted border-b-2 border-black w-full"
	/>
</label>
<label class="pl-2 flex flex-row gap-2 w-3/5">
	{$t('words.description')}:
	<textarea
		placeholder={$t('words.description')}
		bind:value={data.description}
		class="text-black w-full"
	/>
</label>
{#each data.questions as question, index_question}
	<div class="ml-8 grid grid-cols-1 gap-2 m-2 border border-black border-2">
		<h1 class="text-3xl m-1">{$t('words.question')} {index_question + 1}</h1>

		<label class="m-1 flex flex-row gap-2 w-3/5">
			{$t('words.question')}:
			<input
				type="text"
				placeholder={$t('words.question')}
				bind:value={question.question}
				class="text-black w-full bg-inherit border-dotted border-b-2 border-black"
			/>
		</label>
		<label class="m-1 flex flex-row gap-2 w-3/5">
			{$t('words.image')}:
			<input
				type="text"
				placeholder="https://i.imgur.com/kSPCidY.png"
				bind:value={question.image}
				class="text-black w-full bg-inherit border-dotted border-b-2 border-black"
			/>
		</label>
		<label class="m-1 flex flex-row gap-2 w-3/5 flex-nowrap whitespace-nowrap">
			{$t('editor.time_in_seconds')}:
			<input
				type="text"
				placeholder="20"
				bind:value={question.time}
				class="text-black w-full bg-inherit border-dotted border-b-2 border-black"
			/>
		</label>
		{#each question.answers as answer, index_answer}
			<div class="ml-8 grid grid-cols-1 gap-2 m-2 border border-black border-2 m-1">
				<h1 class="text-3xl m-1">{$t('words.answer')} {index_answer + 1}</h1>
				<p class="m-1">
					{$t('words.answer')}: {index_answer + 1}
					{$t('words.question')}: {index_question + 1}
				</p>
				<label class="m-1 flex flex-row gap-2 w-3/5 flex-nowrap whitespace-nowrap">
					{$t('words.answer')}:
					<input
						type="text"
						placeholder={$t('words.answer')}
						bind:value={data.questions[index_question].answers[index_answer].answer}
						class="text-black w-full bg-inherit border-dotted border-b-2 border-black"
					/>
				</label>
				<label class="m-1 flex flex-row gap-2 w-2/6 flex-nowrap whitespace-nowrap">
					<input type="checkbox" bind:checked={answer.right} class="text-black w-fit" />
					<span class="w-fit">{$t('editor.right_or_true?')}</span>
				</label>

				<button
					class="text-left border-yellow-500 border-2 w-fit m-1"
					type="button"
					on:click={() => {
						data.questions[index_question].answers.splice(index_answer, 1);
						data.questions[index_question].answers =
							data.questions[index_question].answers;
					}}
				>
					{$t('editor.delete_answer')}
				</button>
			</div>
		{/each}
		<button
			class="text-left border-green-500 border-2 w-fit m-1"
			type="button"
			on:click={() => {
				data.questions[index_question].answers = [
					...data.questions[index_question].answers,
					{ ...empty_answer }
				];
			}}
		>
			{$t('editor.add_new_answer')}
		</button>
		<button
			class="text-left border-red-500 border-2 w-fit m-1"
			type="button"
			on:click={() => {
				data.questions.splice(index_question, 1);
				data.questions = data.questions;
			}}
		>
			{$t('editor.delete_question')}
		</button>
	</div>
{/each}
<button
	class="text-left"
	type="button"
	on:click={() => {
		data.questions = [...data.questions, { ...empty_question }];
	}}
>
	{$t('editor.add_new_question')}
</button>
{#if imgur_links_valid}
	<p class="text-blue-600 text-xl text-center w-fit mx-auto">
		Not all links are imgur-links! <!-- TODO: Add translation -->
	</p>
{/if}
<button
	type="submit"
	class="text-xl disabled:cursor-not-allowed disabled:border disabled:border-red-500 w-fit mx-auto"
	disabled={imgur_links_valid}>{submit_button_text}</button
>
