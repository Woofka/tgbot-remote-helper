# tgbot-remote-helper
Telegram bot for helping to connect to pc remotely

# How to run
Go to project directory:  
``cd <PATH-TO-PROJECT-DIRECTORY>``  
Build a Docker image:  
``docker build -t tgbot-remote-helper .``  
Run a Docker container:  
``docker run --name tgbot-remote-helper -t -d --restart always --network="host" -e "TZ=<YOUR-TIMEZONE>" -v "<PATH-TO-PROJECT-DIRECTORY>:/app" tgbot-remote-helper -u main.py``  
