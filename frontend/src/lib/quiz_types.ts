/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

export interface QuizData {
	title: string;
	description: string;
	quiz_id: string;
	questions: Question[];
	game_id: string;
	game_pin: string;
	started: boolean;
}

export interface Question {
	time: string;
	question: string;
	image?: string;
	answers: Answer[];
}

export interface Answer {
	right: boolean;
	answer: string;
}

export interface EditorData {
	public: boolean;
	title: string;
	description: string;
	questions: Question[];
}

// TODO Keep an eye on this shit
// export interface Answer {
// 	username: string;
// 	answer: string;
// 	right: boolean;
// }
