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
