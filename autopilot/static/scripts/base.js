$(document).ready(function () {
  try {
    document.getElementById('prompt_input').addEventListener('keyup', e => {
      if (e.keyCode == 13)
        $('#prompt_input').next().find('button.my-btn-blue').click();
    });
  }
  catch {
  }
});

const openOverlay = () => {
  $('#prompt_input').focus();
  $('.overlay').css('transform', 'scale(1)');
  $('.fab').css('backgroundColor', '#EEE').css('color', '#345');
}

const closeOverlay = () => {
  $('.overlay').css('transform', 'scale(0)');
  $('.fab').css('backgroundColor', '#345').css('color', '#EEE');
}

const selectBot = bot => location.href = 'assistant/' + bot + '/home';

function createBot() {
  let unique_name = document.getElementById("prompt_input").value.trim();
  if (checkSpclChars(unique_name)) {
    closeOverlay();
    if (unique_name !== null && unique_name !== "")
      location.href='/assistants/create/' + unique_name + '/';
  }
}

const checkSpclChars = string => {
  for (char of string) {
    charCode = char.charCodeAt();
    if (charCode != 45 && (charCode < 48 || charCode > 57) && (charCode < 65 || charCode > 90) && charCode != 95  && (charCode < 97 || charCode > 122)) {
      alert('Use alphanumeric characters & underscores & dashes only');
    return false;
    }
  }
  return true;
}