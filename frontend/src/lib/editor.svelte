<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import * as yup from 'yup';
	import { dataSchema } from '$lib/yupSchemas';
	import type { EditorData, Question, Answer } from './quiz_types';
	import Sidebar from '$lib/editor/sidebar.svelte';
	import SettingsCard from '$lib/editor/settings-card.svelte';
	import QuizCard from '$lib/editor/card.svelte';
	import Spinner from './Spinner.svelte';

	const { t } = getLocalization();

	let schemaInvalid = false;
	let yupErrorMessage = '';

	export let data: EditorData;
	export let submit_button_text = 'Create';
	export let quiz_id: string | null;
	let selected_question = -1;
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

	const validateInput = async (data: EditorData) => {
		try {
			await dataSchema.validate(data, { abortEarly: false });
			schemaInvalid = false;
			yupErrorMessage = '';
		} catch (err) {
			schemaInvalid = true;
			yupErrorMessage = err.errors[0];
		}
	};
	$: validateInput(data);

	const checkIfAllQuestionImagesComplyWithRegex = (questions: Array<Question>) => {
		let NoteverythingValid = false;
		// const regex = /^https:\/\/i\.imgur\.com\/.{7}.(jpg|png|gif)$/;
		// const local_regex = /^http(|s):\/\/\w*(|:)\d*\/api\/v1\/storage\/download\/.{36}--.{36}$/g;
		const main_regex =
			/^(http(|s):\/\/.*(|:)\d*\/api\/v1\/storage\/download\/.{36}--.{36}|https:\/\/i\.imgur\.com\/.{7}.(jpg|png|gif))$/;
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
	let edit_id;

	const getEditID = async () => {
		let res;
		if (quiz_id === null) {
			res = await fetch(`/api/v1/editor/start?edit=false`, {
				method: 'POST'
			});
		} else {
			res = await fetch(`/api/v1/editor/start?edit=true&quiz_id=${quiz_id}`, {
				method: 'POST'
			});
		}
		if (res.status === 200) {
			const json = await res.json();
			edit_id = json.token;
			console.log(edit_id, json);
		} else {
			alert('Error!');
		}
	};
</script>

{#await getEditID()}
	<Spinner />
{:then _}
	<div class="grid grid-cols-6 h-screen w-screen">
		<div>
			<Sidebar bind:data bind:selected_question />
		</div>
		<div class="col-span-5 flex flex-col">
			<div class="h-10 w-full bg-white mb-10 flex align-middle justify-center rounded-br-lg">
				{#if schemaInvalid}
					<p class="text-center w-full text-red-600 h-full mt-0.5 font-semibold">
						{yupErrorMessage}
					</p>
				{:else}
					<p class="text-center w-full text-black h-full align-bottom mt-0.5">
						{data.title}
					</p>
				{/if}
				<button
					class="pr-2 align-middle bg-purple-400 pl-2 ml-auto whitespace-nowrap disabled:opacity-60 rounded-br-lg"
					disabled={schemaInvalid}
				>
					<span>Save</span>
					<svg
						class="w-6 h-6 inline-block"
						fill="none"
						stroke="currentColor"
						viewBox="0 0 24 24"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							stroke-linecap="round"
							stroke-linejoin="round"
							stroke-width="2"
							d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"
						/>
					</svg>
				</button>
			</div>
			<div class="w-full h-full">
				{#if selected_question === -1}
					<SettingsCard bind:data />
				{:else}
					<QuizCard bind:data bind:selected_question bind:edit_id />
				{/if}
			</div>
		</div>
	</div>
{/await}
