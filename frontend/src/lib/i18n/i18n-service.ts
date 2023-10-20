// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

import i18next from 'i18next';
import en from './locales/en.json';
import de from './locales/de.json';
import fr from './locales/fr.json';
import tr from './locales/tr.json';
import id from './locales/id.json';
import ca from './locales/ca.json';
import it from './locales/it.json';
import es from './locales/es.json';
import nb_no from './locales/nb_NO.json';
import zh_Hant from './locales/zh_Hant.json';
import pl from './locales/pl.json';
import pt from './locales/pt.json';
import uk from './locales/uk.json';
import nl from './locales/nl.json';
import hu from './locales/hu.json';
import vi from './locales/vi.json';
// import uz from './locales/uz.json'
// import zh_Hans from './locales/zh_Hans.json';
import LanguageDetector from 'i18next-browser-languagedetector';

import type { i18n } from 'i18next';

export class I18nService {
	// expose i18next
	i18n: i18n;

	constructor() {
		this.i18n = i18next;
		this.initialize();
		// this.changeLanguage("de")
		//this.changeLanguage(INITIAL_LANGUAGE);
	}

	// Our translation function
	t(key: string, replacements?: Record<string, unknown>): string {
		return this.i18n.t(key, replacements);
	}

	// Initializing i18n
	initialize(): void {
		this.i18n.use(LanguageDetector).init({
			// lng: INITIAL_LANGUAGE,
			compatibilityJSON: 'v3',
			fallbackLng: 'en',
			debug: false,
			defaultNS: 'translation',
			interpolation: {
				escapeValue: false
			},
			returnEmptyString: false,
			simplifyPluralSuffix: true,
			// detection: {
			// 	order: ['browser', 'querystring', 'navigator', 'localStorage', 'htmlTag'],
			// 	lookupQuerystring: 'lng'
			// }
			detection: {
				order: ['querystring', 'cookie', 'localStorage', 'navigator'],
				lookupQuerystring: 'lng',
				lookupLocalStorage: 'language'
			}
		});
		this.i18n.addResourceBundle('en', 'translation', en);
		this.i18n.addResourceBundle('de', 'translation', de);
		this.i18n.addResourceBundle('fr', 'translation', fr);
		this.i18n.addResourceBundle('tr', 'translation', tr);
		this.i18n.addResourceBundle('id', 'translation', id);
		this.i18n.addResourceBundle('it', 'translation', it);
		this.i18n.addResourceBundle('ca', 'translation', ca);
		this.i18n.addResourceBundle('es', 'translation', es);
		this.i18n.addResourceBundle('nb_NO', 'translation', nb_no);
		this.i18n.addResourceBundle('zh_Hant', 'translation', zh_Hant);
		this.i18n.addResourceBundle('zh_Hant', 'translation', zh_Hant);
		this.i18n.addResourceBundle('pl', 'translation', pl);
		this.i18n.addResourceBundle('pt', 'translation', pt);
		this.i18n.addResourceBundle('uk', 'translation', uk);
		this.i18n.addResourceBundle('nl', 'translation', nl);
		this.i18n.addResourceBundle('hu', 'translation', hu);
		this.i18n.addResourceBundle('vi', 'translation', vi);
		// this.i18n.addResourceBundle('uz', 'translation', uz);
	}

	changeLanguage(language: string): void {
		this.i18n.changeLanguage(language);
	}
}
