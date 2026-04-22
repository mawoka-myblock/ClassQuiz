import type { Player, PlayerAnswer } from '$lib/admin.ts';
import { QuizData } from '$lib/quiz_types';

export interface IGameState {
    game_id: string;
    players: Player[];
    player_scores: Record<string, number>;
    selected_question: number;
    timer_res: string;
    question_results: any;
    answer_count: number;
    shown_question_now: number;
    final_results: Array<null> | Array<Array<PlayerAnswer>>;
    game_started: boolean;
    quiz_data: QuizData;
    control_visible: boolean;

    constructor(game_id: string);
}