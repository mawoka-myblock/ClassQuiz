/// <reference types="@sveltejs/kit" />

// See https://kit.svelte.dev/docs/types#the-app-namespace
// for information about these interfaces
declare namespace App {
	// interface Locals {}
	// interface Platform {}
	interface Session {
		authenticated: boolean;
		token: string | null;
		email: string | null;
	}

	// interface Stuff {}
}

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

// TODO WTF
export interface Answer {
	username: string;
	answer: string;
	right: boolean;
}
