const signUpButton = document.getElementById('signUp');
const signInButton = document.getElementById('signIn');
const container = document.getElementById('container');
const submitSignUp = document.getElementById('submitSignUp');
const submitSignIn = document.getElementById('submitSignIn');
const formSignIn = document.getElementById('formSignIn');
const formSignUp = document.getElementById('formSignUp');

signUpButton.addEventListener('click', () => {
  container.classList.add("right__panel__active");
});

signInButton.addEventListener('click', () => {
  container.classList.remove("right__panel__active");
});

submitSignIn.addEventListener('click', () => {
  console.log('this');
  formSignIn.submit();
});

submitSignUp.addEventListener('click', () => {
  console.log('this');
  formSignUp.submit();
})