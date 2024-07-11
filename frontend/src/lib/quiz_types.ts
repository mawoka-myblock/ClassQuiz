// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

export enum ElementTypes {
	Text = 'TEXT', // eslint-disable-line no-unused-vars
	Headline = 'HEADLINE', // eslint-disable-line no-unused-vars
	Image = 'IMAGE', // eslint-disable-line no-unused-vars
	Rectangle = 'RECTANGLE', // eslint-disable-line no-unused-vars
	Circle = 'CIRCLE' // eslint-disable-line no-unused-vars
}

export interface QuizData {
	title: string;
	description: string;
	quiz_id: string;
	questions: Question[];
	game_id: string;
	game_pin: string;
	started: boolean;
	cover_image?: string;
	background_color?: string;
	background_image?: string;
	likes: number;
	dislikes: number;
	plays: number;
	views: number;
}

export enum QuizQuestionType {
	ABCD = 'ABCD', // eslint-disable-line no-unused-vars
	RANGE = 'RANGE', // eslint-disable-line no-unused-vars
	VOTING = 'VOTING', // eslint-disable-line no-unused-vars
	SLIDE = 'SLIDE', // eslint-disable-line no-unused-vars
	TEXT = 'TEXT', // eslint-disable-line no-unused-vars
	ORDER = 'ORDER', // eslint-disable-line no-unused-vars
	CHECK = 'CHECK' // eslint-disable-line no-unused-vars
}

export interface RangeQuizAnswer {
	min: number;
	max: number;
	min_correct: number;
	max_correct: number;
}

export interface TextQuizAnswer {
	answer: string;
	case_sensitive: boolean;
}

export interface OrderQuizAnswer {
	answer: string;
	color?: string;
	id?: number;
}

export interface Question {
	time: string;
	question: string;
	type?: QuizQuestionType;
	image?: string;
	answers: Answers;
	hide_results?: boolean;
}

export type Answers =
	| Answer[]
	| RangeQuizAnswer
	| VotingAnswer[]
	| string
	| TextQuizAnswer[]
	| OrderQuizAnswer[];

export interface Answer {
	right: boolean;
	answer: string;
	color?: string;
}

export interface VotingAnswer {
	answer: string;
	image?: string;
	color?: string;
}

export interface EditorData {
	public: boolean;
	title: string;
	description: string;
	questions: Question[];
	cover_image?: string;
	background_color?: string;
	background_image?: string;
}

export interface PrivateImageData {
	id: string;
	uploaded_at: string;
	mime_type: string;
	hash?: string;
	size?: number;
	deleted_at?: string;
	alt_text?: string;
	filename?: string;
	thumbhash?: string;
	server?: string;
	imported: boolean;
	quizzes: { id: string }[];
	quiztivities: { id: string }[];
}
