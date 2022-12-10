# Home Assistant utilities

## Purge superfluous BLE device entries from known_devices.yaml
This scipt will remove entries from config/.storage/known_device.yaml that occur due to e.g. devices changing the MAC address often.

Run the script by placing it in this file in e.g. config/scripts/ an start it with:

```bash
python3 purge_known_devices.py
```
Inspect the file known_out.yaml and if you're happy with the result, execute
```bash
cd ../.storage
mv known_devices.yaml  known_devices_old.yaml
mv known_out.yaml known_devices.yaml
```
Restart HA to get an effect of the change

### In case of error
You'll have a backup copy in known_devices_old.yaml to restore if anything goes south.
The program also creates a file called keys_out.yaml. This can be used for error tracking and more.
