// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import type { QuizData } from '$lib/quiz_types';

export const get_question_title = (q_number: number, quiz_data: QuizData): string => {
	if (q_number - 1 === quiz_data.questions.length) {
		return;
	}
	try {
		return quiz_data.questions[q_number].question;
	} catch (e) {
		return '';
	}
};

export const getWinnersSorted = (
	quiz_data: QuizData,
	final_results: Array<null> | Array<Array<PlayerAnswer>>
) => {
	const winners = {};
	const q_count = quiz_data.questions.length;

	function sortObjectbyValue(obj) {
		const asc = false;
		const ret = {};
		Object.keys(obj)
			.sort((a, b) => obj[asc ? a : b] - obj[asc ? b : a])
			.forEach((s) => (ret[s] = obj[s]));
		return ret;
	}

	try {
		for (let i = 0; i < q_count; i++) {
			const q_res = final_results[i];
			if (q_res === null) {
				continue;
			}
			for (const res of q_res) {
				if (res['right']) {
					if (winners[res['username']] === undefined) {
						winners[res['username']] = 0;
					}
					winners[res['username']] += 1;
				}
			}
		}

		return sortObjectbyValue(winners);
	} catch {
		return undefined;
	}
};

export interface Player {
	username: string;
}

export interface PlayerAnswer {
	username: string;
	answer: string;
	right: string;
}
