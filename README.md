# m365-mi
This Python library aims to provide fast communication with the M365 Scooters from Xiaomi.

## Supported devices
- Xiaomi M365 Pro 2

Probably others too. Let us know if you find one that works.

## Getting started

### MQTT example

1. Enter your server location, username and password into examples/mqttdump.py
2. Factory reset your scooter so that we can pair with it later. First, power off the scooter. Then, press the power button on the scooter while also holding down the brake and the throttle. Wait until you hear several beeps, then release all of the buttons. Your scooter is now reset.
3. Find your scooters MAC address - run `sudo hcitool lescan | grep 'MiScooter'`
4. Run the following commands to download and install `m365-mi`:

```
git clone https://github.com/cheetahdotcat/m365-mi
cd m365-mi
pip3 install .
```
5. Ensure your scooter is powered on - then run `python3 examples/mqttdump.py -r <MAC address of your Mi Scooter, e.g. EB:6D:4C:XX:XX:XX>`

## Common issues

### Unresolved dependencies
There appears to be a dependency on `paho-mqtt` that is not resolved by running the setup script when running the example `mqttdump` script. Not sure how to fix this, other than running pip install manually.

### Permissions issues starting scan
Run the following commands to grant network access to BluePy:

```
sudo setcap cap_net_raw+e ~/.local/lib/python3.9/site-packages/bluepy/bluepy-helper
sudo setcap cap_net_admin+eip ~/.local/lib/python3.9/site-packages/bluepy/bluepy-helper
```

If still not working, check that there are no other services accessing the Bluetooth adapter.

#### We're Using GitHub Under Protest

This project is currently hosted on GitHub.  This is not ideal; GitHub is a proprietary, trade-secret system that is not Free and Open Souce Software (FOSS).  We are deeply concerned about using a proprietary system like GitHub to develop our FOSS project.  We have an [open {bug ticket, mailing list thread, etc.} ](INSERT_LINK) where the project contributors are actively discussing how we can move away from GitHub in the long term.  We urge you to read about the [Give up GitHub](https://GiveUpGitHub.org) campaign from [the Software Freedom Conservancy](https://sfconservancy.org) to understand some of the reasons why GitHub is not a good place to host FOSS projects.

If you are a contributor who personally has already quit using GitHub, please [check this resource](INSERT_LINK) for how to send us contributions without using GitHub directly.

Any use of this project's code by GitHub Copilot, past or present, is done without our permission.  We do not consent to GitHub's use of this project's code in Copilot.

![Logo of the GiveUpGitHub campaign](https://sfconservancy.org/img/GiveUpGitHub.png)
