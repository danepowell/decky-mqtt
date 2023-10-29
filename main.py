import os
import sys

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code one directory up
# or add the `decky-loader/plugin` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky_plugin
from time import sleep
PLUGIN_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(PLUGIN_DIR+"/py_modules")
#from psutil import sensors_battery
import paho.mqtt.publish as publish

battery_capacity_file = "/sys/class/power_supply/BAT1/capacity"
battery_status_file = "/sys/class/power_supply/ACAD/online"

class Plugin:
    # A normal method. It can be called from JavaScript using call_plugin_function("method_1", argument1, argument2)
    async def add(self, left, right):
        return left + right

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    # @todo obviously make hostname, password, topic, send interval, etc configurable
    async def _main(self):
        capacity = 0
        status = 'Unknown'
        while True:
            with open(battery_capacity_file) as state:
                new_capacity = int(state.read())
                if capacity != new_capacity:
                    capacity = new_capacity
                    decky_plugin.logger.info("Sending battery capacity %d" % capacity)
                    publish.single("decky/battery", str(capacity), hostname="", auth={'username':'mosquitto', 'password':''})
            with open(battery_status_file) as state:
                raw_status = int(state.read())
                new_status = 'Discharging'
                if raw_status == 1:
                    new_status = 'Charging'
                if status != new_status:
                    status = new_status
                    decky_plugin.logger.info("Sending battery status %s" % status)
                    publish.single("decky/status", status, hostname="", auth={'username':'mosquitto', 'password':''})
            sleep(10)
        # psutil is broken: https://github.com/giampaolo/psutil/issues/2212
        # while True:
        #     battery = sensors_battery()
        #     plugged = str(battery.power_plugged)
        #     percent = str(battery.percent)

    # Function called first during the unload process, utilize this to handle your plugin being removed
    async def _unload(self):
        decky_plugin.logger.info("Goodbye World!")
        pass

    # Migrations that should be performed before entering `_main()`.
    async def _migration(self):
        decky_plugin.logger.info("Migrating")
        # Here's a migration example for logs:
        # - `~/.config/decky-template/template.log` will be migrated to `decky_plugin.DECKY_PLUGIN_LOG_DIR/template.log`
        decky_plugin.migrate_logs(os.path.join(decky_plugin.DECKY_USER_HOME,
                                               ".config", "decky-template", "template.log"))
        # Here's a migration example for settings:
        # - `~/homebrew/settings/template.json` is migrated to `decky_plugin.DECKY_PLUGIN_SETTINGS_DIR/template.json`
        # - `~/.config/decky-template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_SETTINGS_DIR/`
        decky_plugin.migrate_settings(
            os.path.join(decky_plugin.DECKY_HOME, "settings", "template.json"),
            os.path.join(decky_plugin.DECKY_USER_HOME, ".config", "decky-template"))
        # Here's a migration example for runtime data:
        # - `~/homebrew/template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_RUNTIME_DIR/`
        # - `~/.local/share/decky-template/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_RUNTIME_DIR/`
        decky_plugin.migrate_runtime(
            os.path.join(decky_plugin.DECKY_HOME, "template"),
            os.path.join(decky_plugin.DECKY_USER_HOME, ".local", "share", "decky-template"))
