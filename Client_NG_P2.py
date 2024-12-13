#TPRG-2131-01
#Nadim Gutto -- 100665657
#Project 2: Client Program
#This was solely my own work which I completed. I used past codes,
#in-class materials and online research to finish this program.
'''
This program creates a server/client-based system that will simply pass collated data
from one program to another and presents the data in a GUI based format.'''

#This program is to run on the pi. If not on the pi, error message will pop up. Link below ↓↓
#https://raspberrypi.stackexchange.com/questions/5100/detect-that-a-python-program-is-running-on-the-pi

'''This program is to run after the server is running first.'''

#Import libraries
import socket
import json
import time
import os
import PySimpleGUI as sg

#Function to check if the script is running on a Raspberry Pi
def is_pi():
    """Check if the script is running on a Raspberry Pi."""
    try:
        #Open the /proc/cpuinfo file and check for Raspberry Pi identifiers
        with open("/proc/cpuinfo", "r") as cpuinfo:
            for line in cpuinfo:
                if "Raspberry Pi" in line:
                    return True  #If Raspberry Pi is detected, return True
    except FileNotFoundError:  #Handle cases where the file is missing
        pass
    return False  #Return False if not running on a Raspberry Pi

#Exit if the script is not running on a Raspberry Pi
if not is_pi():
    sg.popup("This script is designed to run on a Raspberry Pi. Exiting...", title="Error")  #Show an error message
    exit(0)  #Exit the program if it's not on a Raspberry Pi

#Function to collect system data using vcgencmd commands
def collect_data(iteration):
    """Gather system data using vcgencmd commands."""
    #Collect system data and return it in a dictionary format
    temperature = round(float(os.popen("vcgencmd measure_temp").readline().split('=')[1].replace("'C", "").strip()), 1)
    voltage = round(float(os.popen("vcgencmd measure_volts core").readline().split('=')[1].replace("V", "").strip()), 1)
    gpu_memory = int(os.popen("vcgencmd get_mem gpu").readline().split("=")[1].replace("M", "").strip())
    core_clock = round(int(os.popen("vcgencmd measure_clock core").readline().split("=")[1]) // 1_000_000, 1)
    arm_clock = round(int(os.popen("vcgencmd measure_clock arm").readline().split("=")[1]) // 1_000_000, 1)

    #Return the collected data as a dictionary
    return {
        "Temperature": temperature,
        "Voltage": voltage,
        "GPUMemory": gpu_memory,
        "CoreClock": core_clock,
        "ARMClock": arm_clock,
        "Iteration": iteration  #Add iteration count to the data
    }

#Main function to handle client operations
def main():
    #Define the GUI layout
    sg.theme("SystemDefault1")  #Set the GUI theme
    layout = [
        [sg.Text("Connection Status:"), sg.Text("🔴", key="-LED-", font=("Helvetica", 24))],  #LED for connection status
        [sg.Button("Exit", key="-EXIT-")]  #Exit button
    ]
    # Create the GUI window
    window = sg.Window("Client Connection", layout, size=(250, 100), finalize=True)

    #Define network configuration (server IP and port)
    host = '127.0.0.1'  #IP address/Local host
    port = 5000         #Port for communication
    iterations = 50     #Number of iterations to send data

    led_state = False   #Initial LED state (off)

    try:
        #Create a socket object and connect to the server
        s = socket.socket()
        s.connect((host, port))       #Connect to the server
        window["-LED-"].update("🟢")  #Change LED to green (connected)

        #Loop to send data 50 times
        for i in range(iterations):
            event, _ = window.read(timeout=100)  #Read GUI events
            if event == "-EXIT-" or event == sg.WIN_CLOSED:  #Exit the loop if Exit button or window is closed
                break

            # Toggle the LED to indicate data transmission activity
#             led_state = not led_state  # Change the LED state
#             window["-LED-"].update("🟢" if led_state else "🔴")  # Update LED symbol

            #Collect and send data to the server
            data = collect_data(i + 1)    #Collect system data
            json_data = json.dumps(data)  #Convert data to JSON
            s.sendall(json_data.encode('utf-8'))  #Send data to the server
            time.sleep(2)  #Wait for 2 seconds before sending the next data

        sg.popup("Data transmission complete.", title="Info")  #Notify user when data transmission is complete
    except Exception as e:
        sg.popup(f"An error occurred: {e}", title="Error")     #Handle any exceptions and show error
    finally:
        s.close()       #Close the socket connection
        window.close()  #Close the GUI window

#Run the main function and handle keyboard interruptions
if __name__ == "__main__":
    try:
        main()  #Execute the main function
    except KeyboardInterrupt:
        print("Client interrupted. Exiting...")  #Graceful exit (Ctrl+C)
