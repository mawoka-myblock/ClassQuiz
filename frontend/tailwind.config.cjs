const config = {
	content: ['./src/**/*.{html,js,svelte,ts}'],

	theme: {
		extend: {
			colors: {
				green: {
					600: '#009444'
				}
			},
			typography: (theme) => ({
				DEFAULT: {
					css: {
						color: theme('colors.yellow.50'),
						textDecoration: 'none',
						a: {
							color: theme('colors.blue.200')
						},
						blockquote: {
							color: theme('colors.yellow.50')
						},
						h1: {
							color: theme('colors.yellow.50')
						},
						h2: {
							color: theme('colors.yellow.50')
						},
						h3: {
							color: theme('colors.yellow.50')
						},
						h4: {
							color: theme('colors.yellow.50')
						},
						th: {
							color: theme('colors.yellow.50')
						},
						strong: {
							color: theme('colors.yellow.50')
						},
						'code::before': {
							content: '""',
							'padding-left': '0.25rem'
						},
						'code::after': {
							content: '""',
							'padding-right': '0.25rem'
						},
						code: {
							'padding-top': '0.25rem',
							'padding-bottom': '0.25rem',
							fontWeight: '400',
							color: theme('colors.gray.100'),
							'border-radius': '0.25rem',
							backgroundColor: theme('colors.slate.800')
						}
					}
				}
			})
		}
	},

	plugins: [require('@tailwindcss/typography')]
};

module.exports = config;
