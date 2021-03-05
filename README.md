This project will create a python based secure instant messaging app. 2 party will be able to communicate in a secure, E2E manner using TLS. There is a server that handles discovery of the users. Server acts like a phonebook, specifying the 'address' of the other party. Server is also the CA, handling the PKI.

Features:
-Instant messaging
-Security for messages via TLS. Only communicating parties should be able to see the contents.
-Self destruct messages. Messages are self destruct with the help of the roughtime protocol by Google. Rought time verifies the time so other party cannot 'fool' by changing its own clock or manipulating NTP.


