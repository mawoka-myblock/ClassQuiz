import { writable } from 'svelte/store';

export const navbarVisible = writable(true);
export const signedIn = writable(false);
export const pathname = writable('/');
