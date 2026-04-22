export class GameState {
    public game_id: string;
    public players: any[];
    public selected_question: number;
    public timer_res: string;
    public question_results: any;
    public answer_count: number;
    public shown_question_now: number;
    public final_results: any;

    constructor(game_id: string, players: any[]) {
        this.game_id = game_id;
        this.players = players;
        this.selected_question = -1;
        this.timer_res = '0';
        this.question_results = null;
        this.answer_count = 0;
        this.shown_question_now = -1;
        this.final_results = null;
    }
}