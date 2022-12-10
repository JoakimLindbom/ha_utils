# Home Assistant utilities

## Purge superfluous BLE device entries from known_devices.yaml
This scipt will remove entries from config/.storage/known_device.yaml that occur due to e.g. devices changing the MAC address often.

Run the script by placing it in this file in e.g. config/scripts/ an start it with:

```bash
python3 purge_known_devices.py
```
You'll soon get a summary of the execution:
```
2022-12-10 17:23:55 INFO [__main__] Looping through known_devices.yaml
2022-12-10 17:23:55 INFO [__main__] Number of occurrences kept:     21
2022-12-10 17:23:55 INFO [__main__] Number of occurrences removed : 29920
2022-12-10 17:23:55 INFO [__main__] Number of total keys :          29941
2022-12-10 17:23:55 INFO [__main__] Number of total lines :         209589
```
Inspect the file known_devices_new.yaml and if you're happy with the result, execute
```bash
cd ../
mv known_devices.yaml known_devices_old.yaml
mv known_devices_new.yaml known_devices.yaml
```
Restart HA to get an effect of the change

### In case of error
You'll have a backup copy in known_devices_old.yaml to restore if anything goes south.

The program also creates a file called keys_out.yaml. This can be used for error tracking and more.
