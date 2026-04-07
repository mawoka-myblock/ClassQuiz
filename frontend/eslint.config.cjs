// SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)
//
// SPDX-License-Identifier: MPL-2.0

const { defineConfig, globalIgnores } = require('eslint/config');

const tsParser = require('@typescript-eslint/parser');
const typescriptEslint = require('@typescript-eslint/eslint-plugin');
const globals = require('globals');
const js = require('@eslint/js');
const svelte = require('eslint-plugin-svelte');

module.exports = defineConfig([
	js.configs.recommended,
	svelte.configs.recommended,
	globalIgnores(['**/*.cjs', 'src/app.html']),
	{
		languageOptions: {
			sourceType: 'module',
			ecmaVersion: 2020,

			globals: {
				...globals.browser,
				...globals.node
			}
		}
	},
	{
		files: ['**/*.{ts,js}'],
		languageOptions: {
			parser: tsParser
		},

		plugins: {
			'@typescript-eslint': typescriptEslint
		},

		rules: {
			'no-unused-vars': [
				'error',
				{
					argsIgnorePattern: '^_.*'
				}
			],

			'@typescript-eslint/no-unused-vars': [
				'error',
				{
					argsIgnorePattern: '^_.*'
				}
			]
		}
	},
	{
		files: ['**/*.svelte'],
		languageOptions: {
			parserOptions: {
				parser: tsParser,
				extraFileExtensions: ['.svelte']
			}
		}
	},
	{
		files: ['**/*.svelte', '**/*.ts', '**/*.js'],

		rules: {
			'a11y-click-events-have-key-events': 'off',
			'no-unused-vars': [
				'error',
				{
					argsIgnorePattern: '^_.*'
				}
			],
			'@typescript-eslint/no-unused-vars': [
				'error',
				{
					argsIgnorePattern: '^_.*'
				}
			],
			'svelte/no-at-html-tags': 'warn',
			'svelte/require-each-key': 'warn'
		},

		plugins: {
			'@typescript-eslint': typescriptEslint
		}
	}
]);
