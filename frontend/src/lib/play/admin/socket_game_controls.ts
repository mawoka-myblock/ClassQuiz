
import type { Socket } from 'socket.io-client';

/**
 * Class that encapsulates all the socket calls related to game controls for the admin page.
 * Still in development, but it will be used to avoid having socket calls directly in the svelte files, and to have a single place to manage all the game controls related socket calls.
 */
export class SocketGameControls {
    socket: Socket;

    constructor(socket: Socket) {
        this.socket = socket;
    }

	set_question_number(q_number: number) {
		this.socket.emit('set_question_number', q_number.toString());
	};

	get_question_results(game_id: string, question_number: number) {
		this.socket.emit('get_question_results', {
			game_id,
			question_number
		});
	};

	show_solutions() {
		this.socket.emit('show_solutions', {});
	};

	get_final_results() {
		this.socket.emit('get_final_results', {});
	};

    start_game() {
        this.socket.emit('start_game', '');
    }

    kick_player(username: string, players: any[]) {
        this.socket.emit('kick_player', { username: username });

        for (let i = 0; i < players.length; i++) {
            console.log(players[i].username, username);
            if (players[i].username === username) {
                players.splice(i, 1);
                break;
            }
        }
        return players;
    }
}