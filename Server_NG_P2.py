#TPRG-2131-01
#Nadim Gutto -- 100665657
#Project 2: Server Program
#This was solely my own work which I completed. I used past codes,
#in-class materials and online research to finish this program.
'''
This program creates a server/client-based system that will simply pass collated data
from one program to another and presents the data in a GUI based format.'''

#This program can run on either the pi or pc.

'''This program is to run first.'''

#Import libraries
import socket
import json
import PySimpleGUI as sg

#Function to parse JSON data from the client
def parse_data(json_data):
    """Convert JSON string to Python dictionary."""
    try:
        return json.loads(json_data)  #Decode the JSON string into a dictionary
    except json.JSONDecodeError:      #Handle cases where the JSON data is invalid
        return {}  #Return an empty dictionary in case of an error

#Main function to handle server operations
def main():
    #Define the GUI layout
    sg.theme("SystemDefault1")  #Set the GUI theme
    layout = [
        [sg.Text("Latest Data:")],
        [sg.Text("", size=(500, 1), key="-DATA-")],  #Area to display received data
        [sg.Text("Connection Status: "), sg.Text("Waiting...", key="-STATUS-")],  #Display connection status
        [sg.Text("🔴", key="-LED-", font=("Helvetica", 24))],  #LED to show data reception
        [sg.Button("Exit", key="-EXIT-")]  #Exit button to close the server
    ]
    window = sg.Window("Server Monitor", layout,size=(700, 150), finalize=True)

    #Define network configuration (host and port)
    host = '127.0.0.1'  #Local host
    port = 5000         #Port for communication

    s = socket.socket()  #Create a socket object
    s.bind((host, port))  #Bind the socket to the host and port
    s.listen(5)  #Listen for up to 5 incoming connections
    window["-STATUS-"].update("Listening...")  #Update status to show the server is listening

    conn, addr = s.accept()  #Accept a connection from the client
    window["-STATUS-"].update(f"Connected to {addr}")  #Update status with client address
    led_state = False  #Initial LED state (off)

    try:
        #Loop to handle incoming data
        while True:
            event, _ = window.read(timeout=100)  #Read GUI events
            if event == "-EXIT-" or event == sg.WIN_CLOSED:  #Exit the loop if Exit button or window is closed
                break

            #Check if data is received from the client
            data = conn.recv(1024)  #Receive data from the client
            if data:
                #Parse the received data
                parsed_data = parse_data(data.decode("utf-8"))
                display_text = " | ".join([f"{k}: {v}" for k, v in parsed_data.items()])
                window["-DATA-"].update(display_text)  #Update the GUI with the received data

                #Toggle LED state to indicate data reception
                led_state = not led_state  # Change LED state
                window["-LED-"].update("🟢" if led_state else "🔴")  #Update LED symbol

    except Exception as e:
        sg.popup(f"An error occurred: {e}", title="Error")  #Show error if something goes wrong
    finally:
        conn.close()    #Close the client connection
        s.close()       #Close the server socket
        window.close()  #Close the GUI window

#Run the main function and handle keyboard interruptions
if __name__ == "__main__":
    try:
        main()  #Call the main function
    except KeyboardInterrupt:
        print("Server interrupted. Exiting...")  #Graceful exit (Ctrl+C)