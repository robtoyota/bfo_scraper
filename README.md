

# Explanation

Quote from this answer: [Running simple python script continuously on Heroku](https://stackoverflow.com/questions/39139165/running-simple-python-script-continuously-on-heroku)

>Sure, you need to do a few things:
>
>1. Define a `requirements.txt` file in the root of your project that lists your dependencies. This is what Heroku will use to 'detect' you're using a Python app.
>
>2. In the Heroku scheduler addon, just define the command you need to run to launch your python script. It will likely be something like `python myscript.py`.
>
>3. Finally, you need to have some sort of web server that will listen on the proper Heroku PORT -- otherwise, Heroku will think your app isn't working and it will be in the 'crashed' state -- which isn't what you want. To satisfy this Heroku requirement, you can run a really simple Flask web server like this...
>
>Code (`server.py`):
>
    from os import environ
    from flask import Flask
    
    app = Flask(__name__)
    app.run(environ.get('PORT'))
>
>Then, in your `Procfile`, just say: `web: python server.py`.
>
>And that should just about do it =)
