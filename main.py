import json
import socket
import sys
from Tools import log
import app
import Colors
# Default values
PORT = 5500
DEBUG = False

def read_config():
    """Read the configuration from './config.json'."""
    try:
        with open('./config.json', 'r') as config_file:
            config = json.load(config_file)
            return config
    except FileNotFoundError:
        print("[❌] Error: './config.json' not found. Using default values.")
        return None
    except json.JSONDecodeError:
        print("[❌] Error: Failed to parse './config.json'. Using default values.")
        return None

def update_port(config):
    """Update the PORT and DEBUG values based on config or sys.argv."""
    global PORT, DEBUG
    
    # If override_args is true in the config, use the config values directly
    if config and config.get("override_args", "false") == "true":
        print("[⚙️] Using configuration from './config.json'.")
        PORT = config.get("port", PORT)
        DEBUG = config.get("debug", "false").lower() == "true"
        return
    
    # Process command-line arguments
    for arg in sys.argv:
        if arg == "--debug":
            print("[❕] Warning: Debug mode is on!")
            DEBUG = True
        elif arg.startswith("--port="):
            try:
                PORT = int(arg.split("=")[1])
            except ValueError:
                print(f"{Colors.color(text='[❌]', color='red')} Invalid port number provided. Using default port.")
                PORT = 5500  # Default if error

if __name__ == "__main__":
    # Read configuration from file
    config = read_config()
    
    # Update port and debug based on config or arguments
    update_port(config)
    
    # Get the local IP address
    local_ip = socket.gethostbyname(socket.gethostname())
    
    # Log the startup message
    log(message=f"Starting server on {local_ip} with port {PORT}, Debug: {DEBUG}.", 
        app_route="* App Start *", ip=Colors.color(text="SYSTEM", color="indigo"))
    
    # Start the Flask app
    app.main(port=PORT, debug=DEBUG)