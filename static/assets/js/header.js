const header = document.getElementById('header')

/*========== BACKGROUND COLOR ==========*/
const scrollHeader = () => {
  this.scrollY >= 50 ? header.classList.remove('bg-header') : header.classList.add('bg-header')
}

window.addEventListener('scroll', scrollHeader)