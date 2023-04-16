const doctorContainers = [...document.querySelectorAll('.doctors__container')];
const nxtBtn = [...document.querySelectorAll('.nxt__btn')];
const preBtn = [...document.querySelectorAll('.pre__btn')];

doctorContainers.forEach((item, i) => {
  let containerDimensions = item.getBoundingClientRect();
  let containerWidth = containerDimensions.width;

  nxtBtn[i].addEventListener('click', () => {
      item.scrollLeft += containerWidth;
  })

  preBtn[i].addEventListener('click', () => {
      item.scrollLeft -= containerWidth;
  })
})