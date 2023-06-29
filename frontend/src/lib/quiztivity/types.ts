/*
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/.
 */

export enum QuizTivityTypes {
	// eslint-disable-next-line no-unused-vars
	SLIDE = 'SLIDE',
	// eslint-disable-next-line no-unused-vars
	PDF = 'PDF',
	// eslint-disable-next-line no-unused-vars
	MEMORY = 'MEMORY',
	// eslint-disable-next-line no-unused-vars
	MARKDOWN = 'MARKDOWN',
	// eslint-disable-next-line no-unused-vars
	ABCD = 'ABCD'
}

export interface Pdf {
	url: string;
}

export interface MemoryCard {
	image?: string;
	text?: string;
	id: string;
}

export interface Memory {
	cards: MemoryCard[][];
}

export interface Markdown {
	markdown: string;
}

export interface AbcdAnswer {
	answer: string;
	correct: boolean;
}

export interface Abcd {
	question: string;
	answers: AbcdAnswer[];
}

export interface QuizTivityPage {
	title?: string;
	type: QuizTivityTypes;
	data: Pdf | Memory | Markdown;
	id?: string;
}

export interface Data {
	id?: string;
	title: string;
	pages: QuizTivityPage[];
}
