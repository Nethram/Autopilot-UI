$(document).ready(function () {
  $('#say_text').val($('#say_text').val().trim());
  $(`#redirect_${$('.redirect-radio-grp').attr('id')}`).attr('checked', true);
});


function listenTask() {
  let task = $('#listen_tasks').val().trim();
  let content = `<div class="listen-task-container" id="${task}">
                  <h4 class="listen-task">${task}</h4>
                  <button class="sqr-btn my-btn my-btn-red" onclick="removeTask('${task}')">&minus;</button>
                </div>`;
  $('#listen_task_list').append(content);
}

function rememberValue() {
  let key = $('#remember_name').val().trim();
  $('#remember_name').val('');
  if (key.length > 0 && checkSpclChars(key)) {
    let content = `<div id="${key}" class="remember-container">
                    <span id="${key}_key">${key}</span>
                    <input type="text" id="${key}_value" class="input input-tag" placeholder="Enter Value to remember">
                    <button class="sqr-btn my-btn my-btn-red" onclick="removeRemember('${key}')">&minus;</button>
                  </div>`;
    $('#remember_list').append(content);
  }
}

function addQuestion() {
  let questionName = $('#new_question').val().trim();
  $('#new_question').val('');
  if (questionName.length > 0 && checkSpclChars(questionName)) {
    let content = `<div class="question-container" id="${questionName}">
                    <span id="${questionName}_name">${questionName}</span>
                    <input type="text" class="input input-tag" id="${questionName}_question" placeholder="Enter your question">
                    <div>
                      Select type of Answer
                      <select id="${questionName}_type" class="type_select"></select>
                    </div>
                    <button class="sqr-btn my-btn my-btn-red" onclick="removeQuestion('${questionName}')">&minus;</button>
                  </div>`;
    $('.questions-list-container').append(content);
    addOptions();
  }
  else {
    alert("Enter a question name first");
    $('#new_question').focus();
  }
}

function addOptions() {
  for (fieldType of fieldTypes) {
    option = `<option value="${fieldType}">${fieldType}</option>`;
    $('.type_select').append(option);
  }
  $('.type_select').removeClass('type_select');
}

const removeTask = taskId => $('#' + taskId).remove();
const removeRemember = rememberId => $('#' + rememberId).remove();
const removeQuestion = questionId => $('#' + questionId).remove();


function createAction() {
  let actionJSON = {"actions": []}

  if ($('#say-action-status').is(':checked')) {
    let sayTxt = $('#say_text').val().trim();
    if (sayTxt !== null && sayTxt !== '')
      actionJSON.actions.push({'say': sayTxt});
    else{
      $('#say_text').focus();
      return alert('If you want your Chatbot to say something, please enter a text, otherwise turn off the Say action');
    }
  }
  
  if ($('#play-action-status').is(':checked')) {
    let loopCount = Number($('#play_loop').val());
    let playURL = $('#play_url').val().trim();
    if (playURL !== null && playURL !== '') {
      if ((loopCount !== null || loopCount !== '') && loopCount > 0)
        actionJSON.actions.push({'play': {'loop': loopCount, 'url': playURL}});
      else{
        if (confirm("Loop Count has not been specified! Continue with Loop Count value as 1"))
          actionJSON.actions.push({'play': {'loop': 1, 'url': playURL}});
        else{
          $('#play_loop').focus();
          return alert('Please specify loop count');
        }
      }
    }
    else{
      $('#play_url').focus();
      return alert('If you want your Chatbot to play an audio, please enter a URL to play, otherwise turn off the Play action');
    }
  }
  
  if ($('#listen-action-status').is(':checked')) {
    let taskNameList = [];
    for (taskName of document.getElementsByClassName('listen-task'))
      taskNameList.push(taskName.innerText)
    if (taskNameList.length === 0)
      return alert('If you want your Chatbot to listen to task, please select atleast 1 task, otherwise turn off the Listen action');
    actionJSON.actions.push({'listen': {'tasks': taskNameList}});
  }
  
  if ($('#remember-action-status').is(':checked')) {
    rememberObject = {};
    for (remember of document.getElementsByClassName('remember-container')) {
      rememberObject[$(`#${remember.id}_key`).text()] = $(`#${remember.id}_value`).val().trim();
    }
    if (jQuery.isEmptyObject(rememberObject))
      return alert('If you want your Chatbot to remember something, please enter atleast 1 item, otherwise turn off the Remember action');
    actionJSON.actions.push({'remember': rememberObject});
  }
  
  if ($('#redirect-action-status').is(':checked')) {
    let redirectMethod = $("input[name='redirect_method']:checked").val();
    let redirectURL = $('#redirect_url').val().trim();
    if (redirectURL !== null && redirectURL !== '') {
      if (redirectMethod == undefined || redirectMethod === '' || redirectMethod === null)
        return alert('Please Select a method for redirect URL');
      actionJSON.actions.push({'redirect': {'method': redirectMethod, 'uri': redirectURL}});
      }
    else
      return alert('If you want your Chatbot to redirect to a URL, please specify the URL, otherwise turn off the Redirect action');
  }
  
  if ($('#collect-action-status').is(':checked')) {
    let collectName = $('#collect_name').val().trim();
    checkSpclChars(collectName);
    if (collectName === '' || collectName === null)
      return alert('Please enter a name for the Collector');
    let collectRedirect = $('#collect_redirect_task').val();
    let questions = [];
    for (question of document.getElementsByClassName('question-container')) {
      let questionObject = {};
      let qn = $(`#${question.id}_question`).val().trim();
      if (qn.length === 0)
        return alert("Question can't be blank!")
      questionObject['question'] = qn;
      questionObject['name'] = $(`#${question.id}_name`).text();
      questionObject['type'] = $(`#${question.id}_type`).val();
      questions.push(questionObject);
    }
    if (questions.length === 0)
      return alert('If you want your Chatbot to collect something, please enter atleast 1 question, otherwise turn off the Collect action');
    actionJSON.actions.push({
      'collect': {
        'name': collectName,
        'questions': questions,
        'on_complete': {
        'redirect': `task://${collectRedirect}`
        }
      }
    });
  }


  if ($('#collect-action-status').is(':checked') && $('#redirect-action-status').is(':checked'))
    return alert('You can either use Redirect or Collect action at a time');

  console.log(actionJSON);
  return actionJSON;
}