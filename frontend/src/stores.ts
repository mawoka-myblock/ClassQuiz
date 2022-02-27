import { writable } from 'svelte/store';
import { io } from 'socket.io-client';


const messageStore = writable('');


// Connection opened

