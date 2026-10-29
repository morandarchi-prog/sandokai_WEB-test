'use strict';
const year = document.getElementById('annee');
if (year) year.textContent = String(new Date().getFullYear());
const menu = document.querySelector('.menu');
if (menu) {
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.open) {
      menu.open = false;
      menu.querySelector('summary').focus();
    }
  });
  document.addEventListener('click', event => {
    if (!menu.contains(event.target)) menu.open = false;
  });
  menu.querySelectorAll('nav a').forEach(link => {
    link.addEventListener('click', () => { menu.open = false; });
  });
}
