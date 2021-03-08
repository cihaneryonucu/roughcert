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
There are two viable options: run the server locally, use the included Dockerfile to run the server as a service. 

## Run as docker
To run the server as a docker, first build the provided Dockerfile:

`docker build -t securechat-server .`

Run the securechat server docker image, binding port 10040 on the host:

You will need to provide the secureChatApp.config with the IP of the host running the server service. 

`docker run -dp 10040:10040 securechat-server`

## Run the server locally



