import serial
import time

# --- SETUP SERIAL PORT ---
# Change 'COM3' to your port (Linux/Mac example: '/dev/ttyUSB0')
ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # allow Arduino reset

# --- DEFINE COMMANDS ---
COMMANDS = {
    "nod": "NOD\n",
    "shake": "SHAKE\n",
    "lookup": "LOOKUP\n",
    "lookdown": "LOOKDOWN\n",
    "left": "LEFT\n",
    "right": "RIGHT\n",
    "dance": "DANCE\n",
    "surprise": "SURPRISE\n",
    "danceagain": "DANCEAGAIN\n"
}

def send_command(command: str):
    """Send a command string to the duck if valid."""
    cmd = COMMANDS.get(command.lower())
    if cmd:
        ser.write(cmd.encode())
        print(f"Sent: {cmd.strip()}")
    else:
        print(f"Unknown command: {command}")

# --- INTERACTIVE LOOP ---
if __name__ == "__main__":
    print("Duck Control Ready 🦆")
    print("Available commands:", ", ".join(COMMANDS.keys()))
    print("Type 'exit' to quit.")

    while True:
        user_input = input("Enter command: ").strip().lower()
        if user_input == "exit":
            break
        send_command(user_input)

    ser.close()
    print("Connection closed.")
