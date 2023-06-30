/*
SPDX-FileCopyrightText: 2023 Marlon W (Mawoka)

SPDX-License-Identifier: MPL-2.0
*/

const tailwindcss = require('tailwindcss');
const autoprefixer = require('autoprefixer');
const cssnano = require('cssnano');
const postcss_import = require('postcss-import');

const config = {
	plugins: [
		//Some plugins, like tailwindcss/nesting, need to run before Tailwind,
		tailwindcss(),
		postcss_import(),
		//But others, like autoprefixer, need to run after,
		autoprefixer,
		cssnano({ preset: 'default' })
	]
};

module.exports = config;
