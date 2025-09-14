"""
USB Communication Module for DevDuck
Handles sending commands to the USB-connected rubber duck hardware.

This version lazily initializes the serial connection and attempts to
auto-detect the correct USB port on macOS/Linux. It fails gracefully when
hardware is not connected, so API endpoints won't crash.
"""

import os
import time
import threading
from typing import Optional

import serial
from serial.tools import list_ports

_ser_lock = threading.Lock()
_ser: Optional[serial.Serial] = None


def _find_serial_port() -> Optional[str]:
    """Try to find a likely Arduino/USB-serial port.

    Order of preference:
    - DUCK_PORT env var
    - First port containing 'usbmodem' / 'usbserial' / 'Arduino' / 'wchusbserial'
    """
    env_port = os.getenv("DUCK_PORT")
    if env_port:
        return env_port

    for p in list_ports.comports():
        desc = (p.description or "").lower()
        hwid = (p.hwid or "").lower()
        dev = (p.device or "").lower()
        if any(k in desc or k in hwid or k in dev for k in [
            "usbmodem", "usbserial", "arduino", "wchusbserial"
        ]):
            return p.device
    # Fallback common macOS device name (may not exist)
    if os.path.exists("/dev/cu.usbmodem11101"):
        return "/dev/cu.usbmodem11101"
    return None


def _ensure_serial() -> Optional[serial.Serial]:
    global _ser
    if _ser and _ser.is_open:
        return _ser
    with _ser_lock:
        if _ser and _ser.is_open:
            return _ser
        try:
            port = _find_serial_port() or '/dev/cu.usbmodem21101'
            _ser = serial.Serial(port, 9600, timeout=1)
            # Allow Arduino reset
            time.sleep(2)
            print(f"[duck] Connected to serial port: {port}")
            return _ser
        except Exception as e:
            print(f"[duck] WARNING: Could not open serial port: {e}")
            _ser = None
            return None


# --- CORE SEND FUNCTION ---
def send_command(cmd: str):
    ser = _ensure_serial()
    if not ser:
        print(f"[duck] Skipping send (no serial): {cmd}")
        return
    try:
        ser.write((cmd + "\n").encode())
        print(f"[duck] Sent: {cmd}")
    except Exception as e:
        print(f"[duck] ERROR writing to serial: {e}")


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


# --- MOVEMENT TRIGGER BY ACTION NAME ---
def trigger_movement(action: str):
    action_map = {
        'nod': nod,
        'shake': shake,
        'dance': dance,
        'surprise': surprise,
        'lookup': lookup,
        'lookdown': lookdown,
        'left': left,
        'right': right,
        'danceagain': danceagain
    }
    func = action_map.get((action or "").lower())
    if func:
        func()
    else:
        print(f"[duck] Unknown movement action: {action}")


# --- SEQUENCE FUNCTION ---
def perform(actions, delay: float = 2.5):
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
    perform([nod, shake, surprise], delay=2.5)


def good_luck_routine():
    """A playful 'good luck on your coding journey' routine."""
    perform([nod, lookup, lookdown, dance, surprise, danceagain], delay=3.0)


def is_available() -> bool:
    """Return True if we can open or have an open serial connection."""
    return _ensure_serial() is not None


# --- CLEANUP FUNCTION ---
def close_connection():
    global _ser
    try:
        if _ser:
            _ser.close()
            print("[duck] Connection closed.")
    finally:
        _ser = None

