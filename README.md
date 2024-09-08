# Development

Running this script requires [poetry](https://python-poetry.org/docs/)

Install dependencies:
> poetry install

Run the script:
> poetry run python main.py

### Using nix

On a NixOS or host with nix-commands enabled, the dependencies can be automatically created by running the following in this directory:

> nix develop

This will install poetry in a temporary shell and then the script can be ran using:

> poetry install

> poetry run python main.py

# Production

As it sits in place on this machine, the script main.py is running as a systemd service called acx-gui.service

To start, stop, or restart the service- run a command like:

> systemctl --user restart acx-gui.service

# Future plans

- [ ] Add sun angle adjustment on web UI