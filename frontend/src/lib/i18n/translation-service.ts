// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import type { I18nService } from './i18n-service';
import { derived, writable } from 'svelte/store';
import type { Readable, Writable } from 'svelte/store';

// eslint-disable-next-line no-unused-vars
export type TType = (text: string, replacements?: Record<string, unknown>) => string;

export interface TranslationService {
	locale: Writable<string>;
	translate: Readable<TType>;
}

export class I18NextTranslationService implements TranslationService {
	public locale: Writable<string>;
	public translate: Readable<TType>;

	constructor(i18n: I18nService) {
		i18n.initialize();
		this.locale = this.createLocale(i18n);
		this.translate = this.createTranslate(i18n);
	}

	// Locale initialization.
	// 1. Create a writable store
	// 2. Create a new set function that changes the i18n locale.
	// 3. Create a new update function that changes the i18n locale.
	// 4. Return modified writable.
	// skipcq: JS-0105
	private createLocale(i18n: I18nService) {
		const { subscribe, set, update } = writable<string>(i18n.i18n.language);

		const setLocale = (newLocale: string) => {
			i18n.changeLanguage(newLocale);
			set(newLocale);
		};

		// eslint-disable-next-line no-unused-vars
		const updateLocale = (updater: (value: string) => string) => {
			update((currentValue) => {
				const nextLocale = updater(currentValue);
				i18n.changeLanguage(nextLocale);
				return nextLocale;
			});
		};

		return {
			subscribe,
			update: updateLocale,
			set: setLocale
		};
	}

	// Create a translate function.
	// It is derived from the "locale" writable.
	// This means it will be updated every time the locale changes.
	private createTranslate(i18n: I18nService) {
		return derived([this.locale], () => {
			return (key: string, replacements?: Record<string, unknown>) =>
				i18n.t(key, replacements);
		});
	}
}
