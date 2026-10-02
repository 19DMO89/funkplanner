"""Konstanten für den Funkplaner."""

DOMAIN = "funkplaner"
NAME = "Funkplaner"

# Speicher
STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.projects"

# Panel
PANEL_URL = "/funkplaner"
PANEL_TITLE = "Funkplaner"
PANEL_ICON = "mdi:access-point-network"
STATIC_PATH = f"/{DOMAIN}-static"

# Zuordnung Home-Assistant-Integration -> Netz im Planer
#   zb = Zigbee, th = Thread/Matter, wf = WLAN, bt = Bluetooth,
#   sg = 868 MHz (Z-Wave u. a.), lan = Netzwerk
INTEGRATION_NETS: dict[str, str] = {
    "zha": "zb",
    "zigbee2mqtt": "zb",
    "deconz": "zb",
    "zwave_js": "sg",
    "matter": "th",
    "thread": "th",
    "openthread_border_router": "th",
    "homematicip_cloud": "sg",
    "homematic": "sg",
    "fritzbox": "sg",
    "bluetooth": "bt",
    "bthome": "bt",
    "switchbot": "bt",
    "xiaomi_ble": "bt",
    "govee_ble": "bt",
    "inkbird": "bt",
    "ruuvitag_ble": "bt",
    "esphome": "wf",
    "shelly": "wf",
    "tplink": "wf",
    "tplink_omada": "lan",
    "tasmota": "wf",
    "tuya": "wf",
    "localtuya": "wf",
    "wled": "wf",
    "meross_lan": "wf",
    "unifi": "lan",
    "unifiprotect": "lan",
    "synology_dsm": "lan",
    "proxmoxve": "lan",
    "reolink": "lan",
    "onvif": "lan",
    "knx": "lan",
}

# Integrationen, deren Geräte im Plan als Zentrale/Koordinator gelten
ROOT_ROLE_BY_NET = {"zb": "coord", "th": "br", "sg": "zgw", "wf": "ap", "bt": "proxy", "lan": "gw"}
DEFAULT_ROLE_BY_NET = {"zb": "end", "th": "end", "sg": "end", "wf": "client", "bt": "dev", "lan": "dose"}
ROUTER_ROLE_BY_NET = {"zb": "router", "th": "router", "sg": "router", "wf": "client", "bt": "dev", "lan": "dose"}
