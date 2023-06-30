/*
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
*/

module.exports = {
	options: {
		debug: true,
		// read strings from functions: IllegalMoveError('KEY') or t('KEY')
		func: {
			list: ['IllegalMoveError', 't'],
			extensions: ['.js', '.svelte']
		},

		trans: false,

		// Create and update files `en.json`, `fr.json`, `es.json`
		lngs: ['en'],

		ns: [
			// The namespace I use
			'translation'
		],

		defaultLng: 'en',
		defaultNs: 'translation',

		// Put a blank string as initial translation
		// (useful for Weblate be marked as 'not yet translated', see later)
		defaultValue: () => '',

		// Location of translation files
		resource: {
			loadPath: 'src/lib/i18n/locales/{{lng}}.json',
			savePath: 'src/lib/i18n/locales/{{lng}}.json',
			jsonIndent: 4
		},

		nsSeparator: ':',
		keySeparator: '.'
	}
};
