import socket
import threading
import json
import os
import mimetypes
import sys
from http import cookies




HOST ='127.0.0.1'
PORT = 8000

#dictionary to store tweets
tweets = []

# Dictionary to store users
#last editor will be in the sessions[0]
sessions ={}

#function that is run by worker thread to handle and proces requests made by the client/user
def handle_request(client_socket):

    data = client_socket.recv(1024).decode('utf-8')

    if not data:
        return
    print(f"data is{data}")

    request_lines = data.split('\n')
    method, path, _ = request_lines[0].split()

    print(f" method is  {method} and the path is {path}")

    if   method == 'GET' and path =='/':
        #renders and displays the homepage
        filepath = 'index.html'
        with open(filepath, 'rb') as file:
            response_data = file.read()
            content_type = mimetypes.guess_type(filepath)

            client_socket.send(b"HTTP/1.1 200 OK\r\n")
            client_socket.send(f"Content-Type: {content_type}\r\n".encode())
            client_socket.send("Server: Multi_Thread_Web_Server\r\n\r\n".encode())
            client_socket.send(response_data)
            client_socket.close()

            return

    elif method == 'GET' and path == '/api/tweet':
        #returns all the tweets to client so that client can display all tweets
        response_data = json.dumps(tweets)
        status = '200 OK'

    elif method == 'POST' and path == '/api/tweet':
        #receives the data from the client and adds it to the list of tweets
        tweet_data = json.loads(request_lines[-1])
        tweet_data['last_editor'] = sessions.get(0, 'Anonymous')
        tweets.append(tweet_data)
        response_data = "Tweet posted successfully."
        status = '200 OK'

    elif method == 'PUT' and path.startswith('/api/tweet'):
        #edits a particular tweet by reeiving the tweet id and also edits the name of the user to the user that last edits the tweet
        _, tweet_id = path.rsplit('/', 1)
        tweet_id = int(tweet_id)
        print(f"tweet_id is {tweet_id}")
        new_tweet_data = json.loads(request_lines[-1])
        print(f" last editor : {new_tweet_data['last_editor']} new tweet :{new_tweet_data}")
        # new_tweet_data['last_editor'] = sessions.get(0, 'Anonymous')
        sessions[0] = new_tweet_data['last_editor']
        tweets[tweet_id] = new_tweet_data
        response_data = "Tweet updated successfully."
        status = '200 OK'

    elif method == 'POST' and path == '/api/login':
        #receives the name the user logs in with and sets the cookie and sends a status code of 200
        user_data = json.loads(request_lines[-1])
        sessions[0] = user_data['name']
        response_data = "Login Successful"

        sessionCookie = cookies.SimpleCookie()
        sessionCookie["my_cookie"] = user_data['name']



        #setting the path and duration of cookie
        sessionCookie["my_cookie"]["Path"] = "/"
        sessionCookie["my_cookie"]["Max-Age"] = 3600


        sessionCookieOutput = sessionCookie.output()


        client_socket.send(b"HTTP/1.1  200 OK\r\n")
        client_socket.send(f"Content-Length: {len(response_data)}\r\n".encode())
        client_socket.send(f"Set-Cookie: {sessionCookieOutput}\r\n\r\n".encode())
        #setting a cookie on the web browser using http
        client_socket.send("Server: Multi_Thread_Web_Server\r\n\r\n".encode())
        client_socket.send(response_data.encode())

        client_socket.close()

        return



    else:
        #method and path are unrecognized sends an error response
        response_data = "404 Not Found"
        status = '404 Not Found'

    response = f"HTTP/1.1 {status}\nContent-Length: {len(response_data)}\n\n{response_data}"

    print(f" response is : {response}")
    print(f" sessions are {sessions}")
    client_socket.send(response.encode('utf-8'))
    client_socket.close()

#function that starts the multi threaded server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"Server listening on port {PORT}...")

    while True:
        try:
            client_socket, addr = server_socket.accept()
            client_handler = threading.Thread(target=handle_request, args=(client_socket,))
            client_handler.start()
        except KeyboardInterrupt as ki:
            print("Sorry, server close by keyboard interrupt  by host ")
            sys.exit()
        except Exception as e:
            print(f"There is an error and  error is {e}")
            print("OHHHHH NOOOOO!!!!!!!")

if __name__ == "__main__":
    start_server()
