from django.http.response import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from .config import *
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import json
from datetime import datetime
import time
from .models import NodePositions

client = Client(ACCOUNT_SID, AUTH_TOKEN)
SIGNED_IN = False

def signed_in():
    global SIGNED_IN
    return SIGNED_IN

def login(request):
    return render(request, 'login.html')

@csrf_exempt
def sign_in(request):
    global SIGNED_IN
    if request.POST['uname'] == LOGIN_USER and request.POST['pswd'] == LOGIN_PASSWORD:
        SIGNED_IN = True
        return redirect('home')
    return HttpResponse('''<script>alert("Invalid Credential");window.location.href="/";</script>''')

def home(request):
    if signed_in():
        assistants = client.autopilot.assistants.list()
        return render(request, 'home.html', {'assistants':assistants})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')
    
def create_assistant(request, unique_name):
    if signed_in():
        try:
            time_start = datetime.now()
            ts = time.time()
            assistant = client.autopilot.assistants.create(unique_name=unique_name)
            log('Creating Assistant', assistant.sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return redirect('/home')
        except:
            log('Creating Assistant Failed', '', '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return HttpResponse('''<script>alert("An Assistant with the same name exists. Try again with a different name");window.location.href="/home";</script>''')
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def get_assistant(request, assistant_sid, tab):
    if signed_in():
        time_start = datetime.now()
        ts = time.time()
        assistant = client.autopilot.assistants(assistant_sid).fetch()
        tasks = client.autopilot.assistants(assistant_sid).tasks.list()
        field_types = client.autopilot.assistants(assistant_sid).field_types.list()
        tasks_stats = dict()
        field_vals = dict()
        for task in tasks:
            task_statistics = client.autopilot.assistants(assistant_sid).tasks(task.sid).statistics().fetch()
            tasks_stats[task.sid] = [task_statistics.samples_count, task_statistics.fields_count]
        for field_type in field_types:
            field_values = client.autopilot.assistants(assistant_sid).field_types(field_type.sid).field_values.list()
            field_vals[field_type.sid] = list()
            for field_value in field_values:
                field_vals[field_type.sid].append([field_value.sid, field_value.value])
        log('Get Assistant Details', assistant.sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        return render(request, 'dashboard.html', {'tab': tab, 'assistant': assistant, 'tasks': tasks, 'tasks_stats': tasks_stats, 'fields': field_types, 'field_val': field_vals})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def build_model(request, assistant_sid):
    if signed_in():
        try:
            time_start = datetime.now()
            ts = time.time()
            model_build = client.autopilot.assistants(assistant_sid).model_builds.create()
            log('Assistant Model Build', assistant_sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return HttpResponse(f'''<script>window.location.href="/assistant/{assistant_sid}/home";</script>''')
        except:
            log('Model Build Failed', assistant_sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return HttpResponse(f'''<script>alert("Your assistant must have at least one Task and that task must have at least one Sample before you may build a model");window.location.href="/assistant/{assistant_sid}/home";</script>''') 
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')
    
def update_assistant(request, assistant_sid, unique_name, dev_stage):
    if signed_in():
        time_start = datetime.now()
        ts = time.time()
        if dev_stage == 'D':
            dev_stage = 'in-development'
        else:
            dev_stage = 'in-production'
        assistant = client.autopilot.assistants(assistant_sid).update(unique_name=unique_name, development_stage = dev_stage)
        log('Update Assignment', assistant.sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        return redirect(reverse('get_assistant', args=[assistant_sid, 'settings']))
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def delete_assistant(request, unique_name):
    if signed_in():
        try:
            time_start = datetime.now()
            ts = time.time()
            assistant = client.autopilot.assistants(unique_name).fetch()
            tasks = client.autopilot.assistants(assistant.sid).tasks.list()
            for task in tasks:
                try:
                    delete_node_position(task.sid)
                except:
                    pass
            assistant.delete()
            log('Delete Assistant', assistant.sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return redirect('/home')
        except:
            log('Delete Assistant Failed', assistant.sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return HttpResponse('''<script>alert("Couldn't Delete Assistant. Please try again");window.location.href="/home";</script>''')
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def create_task(request, unique_name, assistant_sid):
    if signed_in():
        try:
            time_start = datetime.now()
            ts = time.time()
            task = client.autopilot.assistants(assistant_sid).tasks.create(unique_name=unique_name)
            log('Creating Task', assistant_sid, task.sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return redirect(reverse('get_assistant', args=[assistant_sid, 'tasks']))
        except:
            log('Create Task Failed', assistant_sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return HttpResponse(f'''<script>alert("A Task with the same name exists. Try again with a different name");window.location.href="/assistant/{assistant_sid}/tasks";</script>''')
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def task_home(request, assistant_sid, task_sid):
    if signed_in():
        time_start = datetime.now()
        ts = time.time()
        assistant = client.autopilot.assistants(assistant_sid).fetch()
        task = client.autopilot.assistants(assistant_sid).tasks(task_sid).fetch()
        task_statistics = client.autopilot.assistants(assistant_sid).tasks(task_sid).statistics().fetch()
        log('Get Task Data', assistant.sid, task.sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        return render(request, 'task_home.html', {'assistant': assistant, 'task': task, 'task_stats': task_statistics})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def delete_task(request, assistant_sid, task_sid):
    if signed_in():
        try:
            time_start = datetime.now()
            ts = time.time()
            client.autopilot.assistants(assistant_sid).tasks(task_sid).delete()
            log('Delete Task', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            try:
                delete_node_position(task_sid)
            except:
                pass
            return redirect(reverse('get_assistant', args=[assistant_sid, 'tasks']))
        except:
            log('Task Deletion Failed', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return HttpResponse('''<script>alert("All Fields and Samples associated with the Task must be deleted before deleting the Task");window.location.href="/assistant/''' + assistant_sid + '''/task/''' + task_sid + '''";</script>''')
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def task_fields(request, assistant_sid, task_sid):
    if signed_in():
        time_start = datetime.now()
        ts = time.time()
        assistant = client.autopilot.assistants(assistant_sid).fetch()
        task = client.autopilot.assistants(assistant_sid).tasks(task_sid).fetch()
        fields = client.autopilot.assistants(assistant_sid).tasks(task_sid).fields.list()
        user_field_types = client.autopilot.assistants(assistant_sid).field_types.list()
        log('Fields for Task', assistant.sid, task.sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        field_types = set(TWILIO_FIELD_TYPES)
        for field_type in user_field_types:
            field_types.add(field_type.unique_name)
        field_types = list(field_types)
        field_types.sort()
        return render(request, 'task_fields.html', {'assistant': assistant, 'task': task, 'fields': fields, 'field_types': field_types})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def create_field(request, assistant_sid, task_sid, unique_name, field_type):
    if signed_in():
        try:
            time_start = datetime.now()
            ts = time.time()
            field = client.autopilot.assistants(assistant_sid).tasks(task_sid).fields.create(field_type=field_type, unique_name=unique_name)
            log('Creating Task Field', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return redirect(reverse('task_fields', args=[assistant_sid, task_sid]))
        except:
            log('Task Field Creation Failed', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return HttpResponse(f'''<script>alert("A Field with same name already exist. Try again with a different name");window.location.href="/assistant/{assistant_sid}/task/{task_sid}/fields/";</script>''')
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def delete_field(request, assistant_sid, task_sid, field_sid):
    if signed_in():
        try:
            time_start = datetime.now()
            ts = time.time()
            client.autopilot.assistants(assistant_sid).tasks(task_sid).fields(field_sid).delete()
            log('Delete Task Field', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return redirect(reverse('task_fields', args=[assistant_sid, task_sid]))
        except:
            log('Failed Task Field Deletion', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return HttpResponse('''<script>alert("This Field is in use, delete them first");window.location.href="/assistant/''' + assistant_sid + '''/task/''' + task_sid + '''/samples";</script>''')
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def task_samples(request, assistant_sid, task_sid):
    if signed_in():
        time_start = datetime.now()
        ts = time.time()
        assistant = client.autopilot.assistants(assistant_sid).fetch()
        task = client.autopilot.assistants(assistant_sid).tasks(task_sid).fetch()
        samples = client.autopilot.assistants(assistant_sid).tasks(task_sid).samples.list()
        fields = client.autopilot.assistants(assistant_sid).tasks(task_sid).fields.list()
        log('Get Samples', assistant.sid, task.sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        return render(request, 'task_samples.html', {'assistant': assistant, 'task': task, 'samples': samples, 'fields': fields})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def create_sample(request, assistant_sid, task_sid, tagged_text):
    if signed_in():
        try:
            time_start = datetime.now()
            ts = time.time()
            sample = client.autopilot.assistants(assistant_sid).tasks(task_sid).samples.create(language='en-US', tagged_text=tagged_text)
            log('Creating Sample', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return redirect(reverse('task_samples', args=[assistant_sid, task_sid]))
        except:
            log('Sample Creation Failed', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return redirect(reverse('task_samples', args=[assistant_sid, task_sid]))
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def delete_sample(request, assistant_sid, task_sid, sample_sid):
    if signed_in():
        time_start = datetime.now()
        ts = time.time()
        client.autopilot.assistants(assistant_sid).tasks(task_sid).samples(sample_sid).delete()
        log('Delete Sample', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        return redirect(reverse('task_samples', args=[assistant_sid, task_sid]))
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def task_actions(request, assistant_sid, task_sid):
    if signed_in():
        time_start = datetime.now()
        ts = time.time()
        assistant = client.autopilot.assistants(assistant_sid).fetch()
        task = client.autopilot.assistants(assistant_sid).tasks(task_sid).fetch()
        tasks = client.autopilot.assistants(assistant_sid).tasks.list()
        task_actions = client.autopilot.assistants(assistant_sid).tasks(task_sid).task_actions().fetch()
        user_field_types = client.autopilot.assistants(assistant_sid).field_types.list()
        log('Get Task Actions', assistant.sid, task.sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        actions = task_actions.data['actions']
        action_on = list()
        my_action = dict()
        collect_task = None
        for action in actions:
            a = list(action.keys())[0]
            action_on.append(a)
            my_action[a] = action[a]
        field_types = set(TWILIO_FIELD_TYPES)
        for field_type in user_field_types:
            field_types.add(field_type.unique_name)
        field_types = list(field_types)
        field_types.sort()
        if 'collect' in action_on:
            collect_task = my_action['collect']['on_complete']['redirect'][7:]
        return render(request, 'task_actions.html', {'assistant': assistant, 'tasks': tasks, 'task': task, 'actions': actions, 'action_on': action_on, 'my_action': my_action, 'field_types': field_types, 'collect_task': collect_task})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

@csrf_exempt
def update_task_actions(request):
    if signed_in():
        assistant_sid = request.POST['assistant_sid']
        task_sid = request.POST['task_sid']
        actionsJSON = request.POST['actionsJSON']
        time_start = datetime.now()
        ts = time.time()
        task_actions = client.autopilot.assistants(assistant_sid).tasks(task_sid).task_actions().update(actions=actionsJSON)
        log('Update Task Actions', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        return redirect(reverse('task_home', args=[assistant_sid, task_sid]))
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def create_field_type(request, assistant_sid, unique_name):
    if signed_in():
        try:
            time_start = datetime.now()
            ts = time.time()
            field_type = client.autopilot.assistants(assistant_sid).field_types.create(unique_name=unique_name)
            log('Creating Field Type', assistant_sid, field_type.sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return redirect(reverse('get_assistant', args=[assistant_sid, 'fields']))
        except:
            log('Failed Field Type Creations', assistant_sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return HttpResponse(f'''<script>alert("A Field Type with same name already exist. Try again with a different name");window.location.href="/assistant/{assistant_sid}/fields";</script>''')
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def delete_field_type(request, assistant_sid, field_sid):
    if signed_in():
        try:
            time_start = datetime.now()
            ts = time.time()
            client.autopilot.assistants(assistant_sid).field_types(field_sid).delete()
            log('Delete Field Type', assistant_sid, field_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return redirect(reverse('get_assistant', args=[assistant_sid, 'fields']))
        except:
            log('Failed Field Type Deletion', assistant_sid, field_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return HttpResponse(f'''<script>alert("This Field Type has values, delete them first");window.location.href="/assistant/{assistant_sid}/fields";</script>''')
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def create_field_value(request, assistant_sid, field_sid, unique_value):
    if signed_in():
        try:
            time_start = datetime.now()
            ts = time.time()
            field_value = client.autopilot.assistants(assistant_sid).field_types(field_sid).field_values.create(language='en-US', value=unique_value)
            log('Creating Field Value', assistant_sid, field_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return redirect(reverse('get_assistant', args=[assistant_sid, 'fields']))
        except:
            log('Failed Field Value Creation', assistant_sid, field_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return HttpResponse(f'''<script>alert("This Field Value exist within the same Field Type. Please enter a different value");window.location.href="/assistant/{assistant_sid}/fields";</script>''')
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def delete_field_value(request, field_val_sid, field_sid, assistant_sid):
    if signed_in():
        time_start = datetime.now()
        ts = time.time()
        client.autopilot.assistants(assistant_sid).field_types(field_sid).field_values(field_val_sid).delete()
        log('Delete Field Value', assistant_sid, field_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        return redirect(reverse('get_assistant', args=[assistant_sid, 'fields']))
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def bot_flow(request, assistant_sid):
    if signed_in():
        task_data_list = list()
        time_start = datetime.now()
        ts = time.time()
        assistant = client.autopilot.assistants(assistant_sid).fetch()
        user_field_types = client.autopilot.assistants(assistant_sid).field_types.list()
        defaults = client.autopilot.assistants(assistant_sid).defaults().fetch()
        log('Get Assistant for Flow', assistant_sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        field_types = set(TWILIO_FIELD_TYPES)
        for field_type in user_field_types:
            field_types.add(field_type.unique_name)
        field_types = list(field_types)
        field_types.append('Any')
        field_types.sort()
        return render(request, 'flow.html', {'assistant': assistant, 'field_types': field_types, 'initiation_task': defaults.data['defaults']['assistant_initiation'][7:]})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

@csrf_exempt
def get_task_nodes(request):
    if signed_in():
        assistant_sid = request.POST['assistantSid']
        task_data_list = list()
        time_start = datetime.now()
        ts = time.time()
        tasks = client.autopilot.assistants(assistant_sid).tasks.list()
        for task in tasks:
            task_actions = client.autopilot.assistants(assistant_sid).tasks(task.sid).task_actions().fetch()
            task_type, pos_x, pos_y = get_node_position(task.sid)
            task_data_list.append({'sid': task.sid, 'name': task.unique_name,'actions': task_actions.data['actions'], 'type': task_type[:-5], 'x': pos_x, 'y': pos_y})
        log('Get Tasks for Flow', assistant_sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        return JsonResponse({'task_data_list': task_data_list})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

@csrf_exempt    
def create_task_flow(request):
    if signed_in():
        assistant_sid = request.POST['assistantSid']
        time_start = datetime.now()
        ts = time.time()
        try:
            task = client.autopilot.assistants(assistant_sid).tasks.create(unique_name=request.POST['nodeId'])
            log('Create Task in Flow', assistant_sid, task.sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return JsonResponse({'task_sid': task.sid, 'task_name': task.unique_name, 'status': 'success'})
        except:
            return JsonResponse({'status': 'failed'})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

@csrf_exempt    
def delete_task_flow(request):
    if signed_in():
        assistant_sid = request.POST['assistantSid']
        task_sid = request.POST['taskSid']
        time_start = datetime.now()
        ts = time.time()
        try:
            client.autopilot.assistants(assistant_sid).tasks(task_sid).delete()
            log('Delete Task in Flow', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            delete_node_position(task_sid)
            return JsonResponse({'status': 'done'})
        except:
            log('Failed Task Deletion in Flow', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return JsonResponse({'status': 'failed'})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

@csrf_exempt
def task_rename_flow(request):
    if signed_in():
        assistant_sid = request.POST.get('assistantSid', False)
        task_sid = request.POST.get('taskSid', False)
        name = request.POST['taskName']
        time_start = datetime.now()
        ts = time.time()
        try:
            task = client.autopilot.assistants(assistant_sid).tasks(task_sid).update(unique_name=name)
            log('Rename Task in Flow', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return JsonResponse({'status': 'done'})
        except:
            log('Failed Renaming Task in Flow', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return JsonResponse({'status': 'failed'})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

@csrf_exempt
def update_action_flow(request):
    if signed_in():
        assistant_sid = request.POST['assistantSid']
        task_sid = request.POST.get('taskSid')
        time_start = datetime.now()
        ts = time.time()
        task_actions = client.autopilot.assistants(assistant_sid).tasks(task_sid).task_actions().update(actions=request.POST['action'])
        log('Update Action in Flow', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        return JsonResponse({'status':'done'})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

@csrf_exempt
def bot_initiation(request):
    if signed_in():
        time_start = datetime.now()
        ts = time.time()
        try:
            assistant_sid = request.POST['assistantSid']
            defaults = client.autopilot.assistants(assistant_sid).defaults().update(defaults={'defaults': {'assistant_initiation': 'task://' + request.POST['initiation_task'], 'fallback': ''}})
            log('Update Initiation Task', assistant_sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return JsonResponse({'status': 'done'})
        except:
            log('Initiation Task Updation Failed', assistant_sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return JsonResponse({'status': 'failed'})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

@csrf_exempt
def clear_bot_initiation(request):
    if signed_in():
        time_start = datetime.now()
        ts = time.time()
        try:
            assistant_sid = request.POST['assistantSid']
            defaults = client.autopilot.assistants(assistant_sid).defaults().update(defaults={'defaults': {'assistant_initiation': '', 'fallback': ''}})
            log('Clear Initiation Task', assistant_sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return JsonResponse({'status': 'done'})
        except:
            log('Initiation Task Updation Failed', assistant_sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return JsonResponse({'status': 'failed'})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

@csrf_exempt
def publish_flow(request):
    if signed_in():
        task_actions = json.loads(request.POST.get('taskActions'))
        assistant_sid = request.POST['assistantSid']
        time_start_publish = datetime.now()
        ts_publish = time.time()
        for task_action in task_actions:
            time_start = datetime.now()
            ts = time.time()
            try:
                task_actions = client.autopilot.assistants(assistant_sid).tasks(task_action['sid']).task_actions().update(actions=task_action['action'])
                log('Update Action in Flow Publish', assistant_sid, task_action['sid'], datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            except:
                log('Failed to Publish Actions in Flow', assistant_sid, task_action['sid'], datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        log('Completed Flow Publish', assistant_sid, '', datetime.now().strftime('%d/%m/%Y'), time_start_publish.strftime('%H:%M:%S'), round(time.time() - ts_publish, 3))
        return JsonResponse({'status': 'done'})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

@csrf_exempt
def get_action_flow(request):
    if signed_in():
        assistant_sid = request.POST['assistantSid']
        task_sid = request.POST.get('taskSid')
        time_start = datetime.now()
        ts = time.time()
        task_actions = client.autopilot.assistants(assistant_sid).tasks(task_sid).task_actions().fetch()
        log('Get Action in Flow', assistant_sid, task_sid, datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        return JsonResponse({'actions': json.dumps(task_actions.data)})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

@csrf_exempt
def update_node_position(request):
    if signed_in():
        sid = request.POST['taskSid']
        task_type = request.POST['taskType']
        pos_x, pos_y = request.POST['posX'], request.POST['posY']
        if NodePositions.objects.filter(sid=sid).exists():
            NodePositions.objects.filter(sid=sid).update(type=task_type, x=pos_x, y=pos_y)
        else:
            new_node = NodePositions()
            new_node.sid = sid
            new_node.type = task_type
            new_node.x = pos_x
            new_node.y = pos_y
            new_node.save()
        return JsonResponse({'status': 'updated'})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

@csrf_exempt
def create_query(request):
    if signed_in():
        assistant_sid = request.POST['assistantSid']
        query_string = request.POST['queryString']
        tasks_limit = request.POST.get('taskLimit', False)
        if tasks_limit == 'true':
            tasks_limit = None
        time_start = datetime.now()
        ts = time.time()
        assistant = client.autopilot.assistants(assistant_sid).fetch()
        if assistant.needs_model_build:
            log('Query Creation Failed: Model not Build', assistant.sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return JsonResponse({'error': "Please build the model before using the simulator"})
        query = client.autopilot.assistants(assistant_sid).queries.create(language='en-US', query=query_string, tasks=tasks_limit)
        task_actions = get_task_actions(assistant_sid, query.results['task'])
        if task_actions == None:
            log('Created Query Not Matching to Task Set', assistant.sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
            return JsonResponse({'status': 'failed'})
        log('Create Query', assistant.sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        return JsonResponse({'actions': json.dumps(task_actions), 'status': 'success', 'field_data': query.results['fields']})
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

@csrf_exempt
def get_task_actions_simulator(request):
    if signed_in():
        assistant_sid = request.POST['assistantSid']
        time_start = datetime.now()
        ts = time.time()
        log('Redirected to Task in Simulator', assistant_sid, '', datetime.now().strftime('%d/%m/%Y'), time_start.strftime('%H:%M:%S'), round(time.time() - ts, 3))
        return JsonResponse({'actions': json.dumps(get_task_actions(assistant_sid, request.POST['taskName'])), 'status': 'success'})
        
    return HttpResponse('''<script>alert("Sign In to Continue");window.location.href="/";</script>''')

def get_task_actions(assistant_sid, task_name):
    tasks = client.autopilot.assistants(assistant_sid).tasks.list()
    for task in tasks:
        if task.unique_name == task_name:
            return client.autopilot.assistants(assistant_sid).tasks(task.sid).task_actions().fetch().data

def get_node_position(task_sid):
    try:
        task = NodePositions.objects.get(sid=task_sid)
        return task.type, task.x, task.y
    except:
        return 'speech-item', 0, 0

def delete_node_position(task_sid):
    NodePositions.objects.get(sid=task_sid).delete()

def log(type, assistant_sid, task_sid, date, time_start, time):
    with open('log_file.csv', 'a') as file:
        file.write(f'{type},{assistant_sid},{task_sid},{date},{time_start},{time}\n')

def logout(request):
    global SIGNED_IN
    SIGNED_IN = False
    return redirect('/')