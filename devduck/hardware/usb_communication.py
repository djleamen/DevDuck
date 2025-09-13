import serial
import time


ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # allow Arduino reset


# --- CORE SEND FUNCTION ---
def send_command(cmd: str):
    ser.write((cmd + "\n").encode())
    print(f"Sent: {cmd}")


# --- ABSTRACTED FUNCTIONS ---
def nod(): send_command("NOD")
def shake(): send_command("SHAKE")
def lookup(): send_command("LOOKUP")
def lookdown(): send_command("LOOKDOWN")
def left(): send_command("LEFT")
def right(): send_command("RIGHT")
def dance(): send_command("DANCE")
def surprise(): send_command("SURPRISE")
def danceagain(): send_command("DANCEAGAIN")


# --- SEQUENCE FUNCTION ---
def perform(actions, delay: float = 1.0):
    """
    Perform a sequence of duck actions.
    :param actions: list of functions, e.g. [nod, shake, left]
    :param delay: time (s) between actions
    """
    for action in actions:
        action()
        time.sleep(delay)


# --- ROUTINES ---
def greeting_routine():
    """A cheerful greeting sequence."""
    perform([nod, shake, surprise], delay=1.2)

def good_luck_routine():
    """A playful 'good luck on your coding journey' routine."""
    perform([nod, lookup, lookdown, dance, surprise, danceagain], delay=1.5)


# --- CLEANUP FUNCTION ---
def close_connection():
    ser.close()
    print("Connection closed.")

surprise()