# tgbot-remote-helper
Telegram bot for helping to connect to pc remotely

# How to run
Go to project directory:  
``cd <path-to-project-directory>``  
Build a Docker image:  
``docker build -t tgbot-remote-helper .``  
Run a Docker container:  
``docker run --name tgbot-remote-helper -t -d --privileged --restart always -p 10788:10788/udp -p 10789:10789/udp -v "<path-to-project-directory>:/app" tgbot-remote-helper -u main.py``
