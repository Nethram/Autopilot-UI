from os import name
from django.urls import path
from . import views

urlpatterns=[
    path('', views.login, name='login'),
    path('sign_in', views.sign_in, name='sign_in'),
    path('home', views.home, name='home'),
    path('logout', views.logout, name='logout'),
    path('assistants/create/<str:unique_name>/', views.create_assistant, name='create_assistant'), # create new assistant
    path('assistants/delete/<str:unique_name>/', views.delete_assistant, name='delete_assistant'), # delete assistant
    path('assistant/<str:assistant_sid>/<str:tab>', views.get_assistant, name='get_assistant'), # dashboard
    path('assistants/<str:assistant_sid>/tasks/create/<str:unique_name>/', views.create_task, name='create_task'), # Create a task
    path('assistant/<str:assistant_sid>/task/delete/<str:task_sid>/', views.delete_task, name='delete_task'), # delete a task
    path('assistant/<str:assistant_sid>/task/<str:task_sid>/', views.task_home, name='task_home'), # task home
    path('assistant/<str:assistant_sid>/task/<str:task_sid>/fields/', views.task_fields, name='task_fields'), # view task fields
    path('assistant/<str:assistant_sid>/task/<str:task_sid>/fields/create/<str:unique_name>/<str:field_type>/', views.create_field, name='create_field'), # create a fields
    path('assistant/<str:assistant_sid>/task/<str:task_sid>/fields/delete/<str:field_sid>/', views.delete_field, name='delete_field'), # delete a fields
    path('assistant/<str:assistant_sid>/task/<str:task_sid>/samples/', views.task_samples, name='task_samples'), # view task samples
    path('assistant/<str:assistant_sid>/task/<str:task_sid>/samples/create/<str:tagged_text>/', views.create_sample, name='create_sample'), # create a sample
    path('assistant/<str:assistant_sid>/task/<str:task_sid>/samples/delete/<str:sample_sid>/', views.delete_sample, name='delete_sample'), # delete a sample
    path('assistant/<str:assistant_sid>/task/<str:task_sid>/fields/', views.task_fields, name='task_fields'), # view task fields
    path('assistant/<str:assistant_sid>/task/<str:task_sid>/fields/delete/<str:field_sid>/', views.delete_field, name='delete_field'), # delete a fields
    path('assistants/<str:assistant_sid>/field_type/create/<str:unique_name>/', views.create_field_type, name='create_field_type'), # Create a field type
    path('assistants/<str:assistant_sid>/field_type/delete/<str:field_sid>/', views.delete_field_type, name='delete_field_type'), # delete a field type
    path('assistants/<str:assistant_sid>/field_type/<str:field_sid>/create/<str:unique_value>/', views.create_field_value, name='create_field_value'), # Create a field value
    path('assistants/<str:assistant_sid>/field_type/<str:field_sid>/delete/<str:field_val_sid>/', views.delete_field_value, name='delete_field_value'), # delete a field value
    path('assistants/update/<str:assistant_sid>/<str:unique_name>/<str:dev_stage>/', views.update_assistant, name='update_assistant'), # update assistant
    path('assistant/build/<str:assistant_sid>/', views.build_model, name='build_model'), # build model
    path('assistant/<str:assistant_sid>/task/<str:task_sid>/actions/', views.task_actions, name='task_actions'), # view task actions
    path('update_task_actions', views.update_task_actions, name='update_task_actions'), # update task actions
    path('assistant/<str:assistant_sid>/flow/', views.bot_flow, name='bot_flow'), # get flow of chatbot
    path('get_task_nodes', views.get_task_nodes, name='get_task_nodes'), # get task nodes
    path('create_task_flow', views.create_task_flow, name='create_task_flow'), # create task in flow
    path('delete_task_flow', views.delete_task_flow, name='delete_task_flow'), # delete task in flow
    path('update_action_flow', views.update_action_flow, name='update_action_flow'), # update an action in flow
    path('task_rename_flow', views.task_rename_flow, name='task_rename_flow'), # rename a task in flow
    path('get_action_flow', views.get_action_flow, name='get_action_flow'), # get action in flow
    path('update_node_position', views.update_node_position, name='update_node_position'), # update position of node to db
    path('bot_initiation', views.bot_initiation, name='bot_initiation'), # set initiation
    path('clear_bot_initiation', views.clear_bot_initiation, name='clear_bot_initiation'), # clear initiation
    path('publish_flow', views.publish_flow, name='publish_flow'), # publish flow
    path('create_query', views.create_query, name='create_query'), # query in simulator
    path('get_task_actions_simulator', views.get_task_actions_simulator, name='get_task_actions_simulator'), # query in simulator
]