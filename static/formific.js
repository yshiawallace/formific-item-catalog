const navIcon = document.querySelector('.header__mobile .nav__icon');

function toggleMobileMenu() {
	const menu = document.querySelector('.header__mobile .nav');
	const nav = document.querySelector('.header__mobile .nav__icon');
	navIcon.classList.toggle('open');
	menu.classList.toggle('open');
}

navIcon.addEventListener('click', toggleMobileMenu);



