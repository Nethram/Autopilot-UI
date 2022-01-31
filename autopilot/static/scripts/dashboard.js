$(document).ready(function () {
  changeTab($('body').attr('data-tab'));
  $('.dashboard-btn').on('click', switchTab);

  if ($('#dev_stage').html().trim() == 'In Development')
    $('#radio_dev').attr('checked', true);
  else
    $('#radio_prd').attr('checked', true);
});

function switchTab(){
  let tabId = $(this).attr('id');
  $('body').attr('data-tab', tabId);
  changeTab(tabId);
}

function changeTab(tabId){
  $('.active-tab').removeClass('active-tab');
  $('.active-dashboard').removeClass('active-dashboard');
  $('#dashboard_' +  tabId).addClass('active-tab');
  $('#' + tabId).addClass('active-dashboard');
  $('.simulator-container input').focus();
}