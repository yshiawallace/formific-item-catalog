const navIcon = document.querySelector('.header__mobile .nav__icon');
const alertBtn = document.querySelector('.alert-box__close');


function toggleMobileMenu() {
	const menu = document.querySelector('.header__mobile .nav');
	const nav = document.querySelector('.header__mobile .nav__icon');
	navIcon.classList.toggle('open');
	menu.classList.toggle('open');
}

function closeAlert() {
	const alertMsg = document.querySelector('.alert-box__msg');
	if (alertMsg.classList.contains('show')) {
		alertMsg.classList.remove('show');
		alertMsg.classList.add('hide');	
	}
}

navIcon.addEventListener('click', toggleMobileMenu);
alertBtn.addEventListener('click', closeAlert);



