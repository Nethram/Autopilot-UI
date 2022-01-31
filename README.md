# Autopilot UI

Autopilot is [Twilio](https://www.twilio.com/)'s new conversational AI platform for building bots, IVRs, voice assistants, and more.
Learn more about [Twilio Autopilot](https://www.twilio.com/blog/introducing-twilio-autopilot-a-conversational-ai-platform-to-build-bots-that-work).

UI design for Autopilot that is integrated with your Twilio account. You can create a bot using the Flow Builder or Text Builder. Bots that you have created natively within Twilio Autopilot will also be visible in our UI, and can be further edited.


## Installation

Create a Twilio account if you already didn't have one.

Download or clone repository. Install the required Python packages using [pip](https://pip.pypa.io/en/stable/).

```bash
pip install -r requirements.txt
```

Install mysqlclient by entering the following command in the terminal.

```bash
pip install mysqlclient
```


## Configuring to Twilio Account

Copy the Account SID & Auth Token from Twilio Dashboard and paste it in  autopilot/chatbot_maker/config.py

```python
ACCOUNT_SID = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
AUTH_TOKEN  = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
```

Also set up login credentials for your Autopilot UI System in the same file.

```python
LOGIN_USER = 'username'
LOGIN_PASSWORD = 'password'
```

Update settings.py with your database credentials.

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'autopilot_db',
        'USER': 'root',
        'PASSWORD': 'DBPassword',
        'HOST': 'localhost',
        'PORT': '3306'
    }
}
```


## Description

### Tasks:
Tasks are the building blocks for your assistant's text, where you apply the actions to establish capabilities and develop the template. Each task has 3 parts.
- #### Fields
  Used to help identify task inputs from samples.
- #### Samples
  These are sentences that prompt the system to detect inputs and direct them to the appropriate task. 
- #### Actions
  These are a set of instructions that the bot performs when the task is triggered.

### Field Type:
These are like data types in programming. There are a few options in Twilio that have been set as defaults, but you can also design your own field types. These Field Types define the type of field in the tasks and connect them to the overall flow.

### Flow:
This is the place where you build your Assistant using the predefined blocks.

- #### Talk:
  Used to make the bot transmit a message in text or a speech in a voice call.
- #### Remember:
  During a conversation, the Remember block is used to "remember" certain things. This block's connection will redirect you to the following task.
- #### Redirect:
  The GET/POST methods are used to transmit the collected data from a conversation to the specified URL. The URL is expected to return a valid action response. 
- #### Question:
  A group of these blocks form a **Collect** action. These blocks make it easier to have a question-answer session with the end user. Connection from the last question block in a group of questions will take you to the next task.

Create connections between these blocks to determine the flow of the conversation. Connections from **Talk** will listen to the task at the other end of the connection, thereby limiting the list of next possible task.
Connection from **Remember** & **Question** will redirect to the next task in the flow after performing it's action.

Double Click on the task blocks to train them with samples and add fields.

### Simulator:
After you've completed developing your assistant, build model and use the simulator to test out the assistant you just built.


## How to run

Start the local server.

Enter the autopilot directory and run the following code in the terminal to setup the database.

```bash
python manage.py makemigrations
python manage.py migrate
```

Enter the following command in the terminal to run the program.

```bash
python manage.py runserver
```

If you are successful the result will be similar to as shown below.

```bash
Performing system checks...

System check identified no issues (0 silenced).
January 24, 2022 - 15:48:00
Django version 3.2.6, using settings 'autopilot.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

Visit http://127.0.0.1:8000/ to see the web app running.


## About
+ [Django](https://www.djangoproject.com/) is the Python back-end framework used.
+ [Twilio REST APIs](https://www.twilio.com/docs/usage/api) are used to integrate with Twilio.
+ [jQuery](https://jquery.com) & [Drawflow](https://github.com/jerosoler/Drawflow) libraries are used in the front-end (JavaScript).
