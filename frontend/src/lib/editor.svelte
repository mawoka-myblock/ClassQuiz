<script lang="ts">
	import { getLocalization } from '$lib/i18n';
	import * as yup from 'yup';
	import { dataSchema } from '$lib/yupSchemas';
	import type { EditorData, Question, Answer } from './quiz_types';
	import Sidebar from '$lib/editor/sidebar.svelte';
	import SettingsCard from '$lib/editor/settings-card.svelte';

	const { t } = getLocalization();

	let schemaInvalid = false;
	let yupErrorMessage = '';

	export let data: EditorData;
	export let submit_button_text = 'Create';
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
</script>

<div class="grid grid-cols-6 h-screen w-screen">
	<div>
		<Sidebar bind:data bind:selected_question />
	</div>
	<div class="col-span-5">
		{#if selected_question === -1}
			<SettingsCard bind:data />
		{/if}
	</div>
</div>
