const validActions = ['say', 'listen', 'play', 'remember', 'redirect', 'collect'];

const startOver = () => {
    collectCount = 0;
    taskLimit = '';
    listener = false;
    fieldMemory = {};
    rememberMemory = {};
    collectMemory = {};
    collectAction = {};
    questionNum = 0;
    questionName = '';

    $('.message-section').html('');
    $('#memory ul').html('').css('display', 'inline-block').removeClass('margin-left');
    $('.user-input-section input').attr('disabled', false).focus();
    $('.user-input-section button').attr('disabled', false);
};

const appendMessage = (msg, className = "") => {
    try {
        if (msg.length !== 0) {
            $('.message-section').append(`<div class="${className}">${msg}</div>`);
            document.querySelector(".message-section").scrollTo(0,document.querySelector(".message-section").scrollHeight);
        }
    }
    catch {
    }
};

const suggestStartOver = errorMsg => {
    appendMessage(errorMsg, 'error-msg');
    setTimeout(appendMessage, 600, '<button onClick="startOver()">Click here to Start Over</button>', 'link-msg');
};

const logMemory = (updateMemory, elementId) => {
    let content = updateMemory();
    $(`#${elementId}`).html(content).css('display', 'block').addClass('margin-left');
};

const updateField = () => {
    let content = '';
    Object.keys(fieldMemory).forEach(key => content += `<li><details><summary>${key}</summary><ul><li>Value: ${fieldMemory[key].value},</li><li>Type: ${fieldMemory[key].type}</li></ul></details></li>`);
    return content;
};

const updateRemember = () => {
    let content = '';
    Object.keys(rememberMemory).forEach(key => content += `<li>${key}: ${rememberMemory[key]}</li>`);
    return content;
};

const updateCollect = () => {
    let content = '';
    Object.keys(collectMemory).forEach(key => {
        let subContent = '';
        Object.keys(collectMemory[key]).forEach(subKey => subContent += `<li><details><summary>${subKey}: {</summary> <ul><li>question: "${collectMemory[key][subKey].question}",</li> <li>type: ${collectMemory[key][subKey].type},</li> <li>value: "${collectMemory[key][subKey].value}"</li></ul></details>}</li>`);
        content += `
            <li>
                <details>
                    <summary>${key}: {</summary>
                    <ul>${subContent}</ul>
                </details>}
            </li>
        `;
    });
    return content;
};

const redirectTask = redirect => {
    if (typeof(redirect) === 'string') {
        $.ajax({
        type: "POST",
        url: "/get_task_actions_simulator",
        data: {'assistantSid': assistant_sid, 'taskName': redirect.slice(7)},
        dataType: "json"
        }).done(response => performSimulation(response));
    }
    else {
        $.ajax({
            type: redirect.method,
            url: redirect.uri,
            crossDomain: true,
            data: {'assistantSid': assistant_sid, 'memory': {'remember': rememberMemory, 'collect': collectMemory, 'field': fieldMemory}},
            dataType: 'json',
            success: response => {
                try {
                    let actions = response.actions;
                    actions.forEach(action => {
                        if (validActions.indexOf(Object.keys(action)[0]) == -1)
                            throw '';
                    });
                    newResponse = {}
                    newResponse['actions'] = JSON.stringify(response);
                    newResponse['status'] = 'success';
                    performSimulation(newResponse);
                }
                catch {
                    appendMessage("URL didn't return a valid action", 'error-msg');
                }
            },
            error: () => appendMessage("Redirect URL Failed", 'error-msg')
        });
    }
};

const performSimulation = response => {
    if (response.status === 'success') {
        try {
            let fieldData = response.field_data;
            if (fieldData !== undefined && Boolean(fieldData.length)) {
                fieldData.forEach(field => fieldMemory[field.name] = {'value': field.value, 'type': field.type});
                logMemory(updateField, 'field');
            }
            actions = JSON.parse(response.actions).actions;
            listener = false;
            actions.forEach(action => {
                switch (Object.keys(action)[0]) {
                    case 'say':
                        appendMessage(Object.values(action)[0]);
                        break;
                    case 'listen':
                        taskLimit = Object.values(action)[0].tasks.toString();
                        listener = true;
                        break;
                    case 'remember':
                        Object.entries(Object.values(action)[0]).forEach(item => rememberMemory[item[0]] = item[1]);
                        logMemory(updateRemember, 'remember');
                        break;
                    case 'redirect':
                        let redirect = Object.values(action)[0];
                        redirectTask(redirect);
                        break;
                    case 'collect':
                        collectAction = Object.values(action)[0];
                        collectCount = collectAction.questions.length;
                        questionNum = collectCount;
                        currentQuestion = collectAction.questions[0].question;
                        questionName = collectAction.questions[0].name;
                        collectMemory[collectAction.name] = {};
                        collectMemory[collectAction.name][questionName] = {"question": currentQuestion, "type": collectAction.questions[0].type, "value": ""};
                        appendMessage(currentQuestion);
                        break;
                }
            });
            if (!listener)
                taskLimit = '';
        }
        catch {
            suggestStartOver("Invalid Redirect Task");
        }
    }
    else {
        let errorMsg = response.error;
        appendMessage(errorMsg, 'error-msg');
        $('.user-input-section input').attr('disabled', true);
        $('.user-input-section button').attr('disabled', true);
        if (errorMsg === "Please build the model before using the simulator") {
            $('.start-over').attr('disabled', true);
            setTimeout(appendMessage, 600, '<button onClick="buildModel()">Click here to Build Model</button>', 'link-msg');
        }
        else
            suggestStartOver("No matching task found");
    }
};

const addMessage = () => {
    let msg = $('.simulator-container input').val().trim();
    if (msg !== '') {
        $('.simulator-container input').val('');
        appendMessage(msg, 'user-msg');
        if (questionNum === 0) {
            $.ajax({
            type: "POST",
            url: "/create_query",
            data: {'assistantSid': assistant_sid, 'queryString': msg, 'taskLimit': taskLimit},
            dataType: "json"
            }).done(response => performSimulation(response));
        }
        else {
            try {
                collectMemory[collectAction.name][questionName].value = msg;
                let currentQuestionObject = collectAction.questions[collectCount - --questionNum];
                let currentQuestion = currentQuestionObject.question;
                questionName = currentQuestionObject.name;
                let questionType = currentQuestionObject.type;
                collectMemory[collectAction.name][questionName] = {"question": currentQuestion, "type": questionType, "value": ""};
                setTimeout(appendMessage, 600, currentQuestion);
            }
            catch {
                collectCount = 0;
                redirectTask(collectAction.on_complete.redirect);
                collectAction = {};
                logMemory(updateCollect, 'collect');
            }
        }
    }
    $('.simulator-container input').focus();
}

$(document).ready(function () {
    startOver();
    $('.simulator-container button').on('click', addMessage);
    $('.simulator-container input').on('keyup', function (e) {
        if (e.which === 13)
            addMessage();
    });
    $('.start-over').on('click', startOver);
});