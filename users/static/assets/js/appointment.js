// ==================== STEP DOCTORS ====================
let chosen;

$(".doctors__card").click(function(){
  $(".doctors__card").removeClass("chosen");
  $(this).toggleClass("chosen");
  console.log('hi')
})

// ==================== STEP DOCTORS ====================
$(".send__btn").click(function(){
  $(".time__select").removeClass("hidden");
  console.log('time__select')
})

// ==================== POPUP ====================
$('body').on('click', '[data-btn-header-example]', function(){
	var type = $(this).attr('data-btn-header-example');

	$().msgpopup({
		text: 'Appointment '+type,
		type: type
	});
});