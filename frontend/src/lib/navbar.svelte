<script>
	import '@fontsource/marck-script/index.css';

	let openMenu = true;
	let closeMenu = false;
	let menuItems = false;
	const toggleMenu = () => {
		openMenu = !openMenu;
		closeMenu = !closeMenu;
		menuItems = !menuItems;
	};
</script>

<nav
	class='w-screen px-4 lg:px-10 py-2 flex flex-col lg:flex-row lg:items-center fixed backdrop-blur-sm bg-white/60 shadow-md z-50 top-0'
>
	<!-- Our logo and button -->
	<section class='w-full lg:w-max flex justify-between'>
		<!-- Logo -->
		<a href='/' class='font-black tracking-tight text-xl text-black marck-script link-hover'
		>ClassQuiz</a
		>

		<!-- Our open/close buttons -->
		<!-- Open menu -->
		<button class='lg:hidden' id='open-menu' on:click={toggleMenu} class:hidden={!openMenu}>
			<svg
				xmlns='http://www.w3.org/2000/svg'
				width='24'
				height='24'
				viewBox='0 0 24 24'
				fill='none'
				stroke='currentColor'
				stroke-width='2'
				stroke-linecap='round'
				stroke-linejoin='round'
				display='block'
				id='TextAlignJustified'
			>
				<path d='M3 6h18M3 12h18M3 18h18' />
			</svg>
		</button>

		<!-- Close menu -->
		<button class='hidden' id='close-menu' class:hidden={!closeMenu} on:click={toggleMenu}>
			<svg
				xmlns='http://www.w3.org/2000/svg'
				width='14'
				height='14'
				viewBox='0 0 24 24'
				fill='none'
				stroke='currentColor'
				stroke-width='3'
				stroke-linecap='round'
				stroke-linejoin='round'
				display='block'
				id='Cross'
			>
				<path d='M20 20L4 4m16 0L4 20' />
			</svg>
		</button>
	</section>

	<!-- Our list of items -->
	<ul
		id='menu-items'
		class='lg:flex w-full flex-col lg:flex-row lg:pl-6'
		class:hidden={!menuItems}
	>
		<li class='py-2'>
			<a
				class='text-lg font-medium lg:px-4 text-gray-600 hover:text-green-600 link-hover'
				href='#install'>Play</a
			>
		</li>
		<li class='py-2'>
			<a
				class='text-lg font-medium lg:px-4 text-gray-600 hover:text-green-600 link-hover'
				href='/account/register'>Register</a
			>
		</li>
		<li class='py-2'>
			<a
				class='text-lg font-medium lg:px-4 text-gray-600 hover:text-green-600 link-hover'
				href='/account/login'>Login</a
			>
		<li class='py-2'>
			<a
				class='text-lg font-medium lg:px-4 text-gray-600 hover:text-green-600 link-hover'
				href='https://github.com/mawoka-myblock/classquiz'>GitHub</a
			>
		</li>

	</ul>
</nav>

