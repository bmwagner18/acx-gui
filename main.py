from ruamel.yaml import YAML
from nicegui import ui
import os
import subprocess

# Reads the config file in the same directory as this script
# and returns the value of "server_path" from the yaml
def load_config():
    # Get the current working directory
    current_directory = os.path.dirname(__file__)

    # Generate the path to the config yaml  
    file_path = os.path.join(current_directory, 'config.yaml')
    
    # We need an instance of the yaml class
    yaml=YAML(typ='safe')
    
    # Load the yaml or throw an exception
    try:
        with open(file_path) as f: config = yaml.load(f)
        return config["server_path"]
    except:
        print(f"Loading config from {file_path} failed. \n\
              'server_directory' must be defined as an abolute path. \n\
              See example...")
        exit()

# Loads the available cars and tracks from the content directory
def load_content(path):
    # Use a function to get list of all sub-dirs
    def list_directories(path):
    # Check that path is a directory
        if not os.path.isdir(path):
            raise ValueError(f"{path} is not a valid directory")

        # List all entries in that directory
        all_entries = os.listdir(path)

        # Filter out list_directories
        directories = [entry for entry in all_entries if os.path.isdir(os.path.join(path, entry))]

        return directories
    
    # Save cars and tracks into lists
    cars = list_directories("".join([path, "content/cars/"]))
    tracks = list_directories("".join([path, "content/tracks/csp/"]))

    return [cars, tracks]

# Generate the web interface for selection of track and cars
def create_ui(cars, tracks, path):
    # A function to deal the button being pressed to generate the config files
    def handle_button(car_dict, track):
        # Pop up notification to tell the user the config is being set
        ui.notification("Updating configuration...", type="success")
        # Print out so the systemctl service knows the update started
        print("Updating configuration...")
        # Convert the cars to the ACS format and save the config
        entry_config(car_dict, path)
        # Generate and save the necessary server config
        server_config(cars, track, path)
        # Restart the systemd server
        restart_server()

    # Create a list of the selected cars in the format needed by ACS
    def entry_config(car_dict, path):
        entries = []
        # i is the actual number of entries
        i = 0
        for car in car_dict:
            # Read how many of that car were entered in the UI
            count = int(car_dict[car].value)
            # Add an the requested number of cars to the entry list
            for _ in range(count):
                entries.append(f"[CAR_{i}]")
                i = i+1
                entries.append(f"MODEL={car}")
        # Print entries for debug
        print(entries)
        # Create the path to the config file
        cfg_path = "".join([path, "cfg/entry_list.ini"])
        # Attempt to save the file or throw an error
        try:
            with open(cfg_path, 'w') as file:
                for line in entries:
                    file.write("".join([line, "\n"]))
        except:
            print(f"Failed to write to config file at {cfg_path}")
            return

    # Generate the server config and save it
    def server_config(cars, track, path):
        # Create the car list in the format required by server config
        server_cars = ";".join(cars)
        # Extract the track name from the UI output
        track_name = track.value
        # Create the path to the config file
        cfg_path = "".join([path, "cfg/server_cfg.ini"])
        
        # Attempt to read the current config or throw an error
        try:
            with open(cfg_path, 'r') as file: cfg = file.readlines()
        except:
            print(f"Failed to read the config file at {cfg_path}")
            return

        # Attempt to write the current config or throw an error
        try:
            # Write the relavent lines in the config file
            cfg[2] = "".join(["CARS=", server_cars, "\n"])
            cfg[4] = "".join(["TRACK=csp/2144/../", track_name, "\n"])
            with open(cfg_path, 'w') as file: file.writelines(cfg)
        except:
            print(f"Failed to write the config file at {cfg_path}")
            return

    # Create a dictionary to hold count of each car
    car_dict = dict()

    # Generate the web UI
    with ui.column().classes('w-full items-center'):
        ui.markdown('# Assetto Corsa Server')
        with ui.grid(columns='250px 250px').classes('items-center'):
            ui.label('Track')
            track = ui.select(options=tracks, value=tracks[0])

            for car in cars:
                ui.label(car)
                car_dict[car] = ui.number(value=0, min=0, max=10)
        ui.button('Update config', on_click=lambda: handle_button(car_dict, track))

    ui.run(title="Assetto Corsa Server", dark=True, show=False, port=8080)

# Use systemctl to restart the server
def restart_server():
    def run_command(command):
        try:
            result = subprocess.check_output(command, shell = True, executable = "/bin/bash", stderr = subprocess.STDOUT)

        except subprocess.CalledProcessError as cpe:
            result = cpe.output

        finally:
            for line in result.splitlines():
                print(line.decode())

    run_command("systemctl --user restart assetto-corsa.service")
    run_command("systemctl --user status assetto-corsa.service")    

def __main__():
    path = load_config()
    [cars, tracks] = load_content(path)
    create_ui(cars, tracks, path)

# Run it
__main__()