// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import { I18nService } from './i18n-service';
import { I18NextTranslationService } from './translation-service';
import type { TType } from './translation-service';
import type { Readable, Writable } from 'svelte/store';
import { getContext, setContext } from 'svelte';

export type I18nContext = {
	t: Readable<TType>;
	currentLanguage: Writable<string>;
};
const CONTEXT_KEY = 't';
export const setLocalization = (context: I18nContext) => {
	return setContext<I18nContext>(CONTEXT_KEY, context);
};

// To make retrieving the t function easier.
export const getLocalization = () => {
	return getContext<I18nContext>(CONTEXT_KEY);
};

export const initLocalizationContext = () => {
	// Initialize our services
	const i18n = new I18nService();
	const tranlator = new I18NextTranslationService(i18n);

	// skipcq: JS-0357
	setLocalization({
		t: tranlator.translate,
		currentLanguage: tranlator.locale
	});

	return {
		i18n
	};
};
