# Secure Chat application


This tool allows to parties to communicate securely between each other. 
Each user registers to a phonebook server that retains the contact information of the other party. Once the user selects the corresponding recipient, a TLS channel is bootstrapped between the two users that can securely communicate with each other. The communication is point to point and does not require the server

The server also acts as CA, providing the user with individual certificates.

Features:
* Contact list server
* Instant messaging
* Security for messages via TLS: only communicating parties should be able to see the contents.
* Self destruct messages: Messages are self destruct with the help of the roughtime protocol by Google. Rought time verifies the time so other party cannot 'fool' by changing its own clock or manipulating NTP.

# Installing
To install the tools, create a conda environment with the provided *.yml file:

`conda env create -f roughcert.yml`

Activate the environment :

`conda activate roughcert`

Install the required pip dependencies:

`pip install --no-cache-dir -r python-requirements.txt`

# Running the server
The server default port is `tcp://*:10040` It is recommended to run the server at this port.
There are three viable options: run the server locally, use the included Dockerfile to run the server as a service or use our server provided at `130.237.202.97` (Please be nice, this is for testing only and uptime is not guaranteed!)

## Run as docker
To run the server as a docker, first build the provided Dockerfile:

`docker build -t securechat-server .`

Run the securechat server docker image, binding port 10040 on the host:

You will need to provide the secureChatApp.config with the IP of the host running the server service. 

`docker run -dp 10040:10040 securechat-server`

## Run the server locally

The server can also run as a normal python application in your local machine. To execute as a local application:

`conda activate roughtime && python server.py`

This will execute the server at `tcp://127.0.0.1:10040`

# Running the chat client

To run the chat client you need to activate the conda environment `roughtime`. Once activate, you can run the client as follows:

`python securechatApp.py --username marco --port XXX --host XXX`

The argument port is the specific TCP port you want to use to listen for incoming messages (any free port is suitable), while host is the IP of your machine. You can chat with any other peer you have a route too. As we only use one TCP port, you could ideally use this over the internet with the necessary port forwarding on your router. In that case, the host would be the public IP of your router. 

The client will first contact the backend server to register the new user and request the list of currently connected users. After the bootstrap phase, the client will allow the user to select a peer to start the conversation. Once a peer is selected, a curses GUI will open where the messages can be entered and visualized. Additional info about the certificate of the remote peer is displayed.



