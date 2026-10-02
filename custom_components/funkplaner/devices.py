"""Geräte aus Home Assistant für den Funkplaner aufbereiten."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
    floor_registry as fr,
)

from .const import (
    DEFAULT_ROLE_BY_NET,
    INTEGRATION_NETS,
    ROOT_ROLE_BY_NET,
    ROUTER_ROLE_BY_NET,
)

# Entitäten, die auf Batteriebetrieb hindeuten
_BATTERY_CLASSES = {"battery"}
# Gerätenamen, die typischerweise die Zentrale sind
_ROOT_HINTS = ("coordinator", "koordinator", "controller", "border router", "bridge", "gateway", "hub", "dongle", "stick")


def _net_for(domains: set[str]) -> str | None:
    for domain in domains:
        net = INTEGRATION_NETS.get(domain)
        if net:
            return net
    return None


def _looks_like_root(name: str, model: str) -> bool:
    text = f"{name} {model}".lower()
    return any(hint in text for hint in _ROOT_HINTS)


async def async_collect(hass: HomeAssistant) -> dict[str, Any]:
    """Geräte, Bereiche und Etagen einsammeln."""
    dev_reg = dr.async_get(hass)
    ent_reg = er.async_get(hass)
    area_reg = ar.async_get(hass)
    floor_reg = fr.async_get(hass)

    floors = {
        floor.floor_id: {"id": floor.floor_id, "name": floor.name, "level": floor.level}
        for floor in floor_reg.async_list_floors()
    }
    areas = {
        area.id: {"id": area.id, "name": area.name, "floor_id": area.floor_id}
        for area in area_reg.async_list_areas()
    }

    # Entitäten je Gerät vorsortieren
    entities_by_device: dict[str, list[er.RegistryEntry]] = {}
    for entry in ent_reg.entities.values():
        if entry.device_id:
            entities_by_device.setdefault(entry.device_id, []).append(entry)

    devices: list[dict[str, Any]] = []
    for device in dev_reg.devices.values():
        if device.disabled_by:
            continue

        domains = {
            hass.config_entries.async_get_entry(entry_id).domain
            for entry_id in device.config_entries
            if hass.config_entries.async_get_entry(entry_id)
        }
        # Zigbee2MQTT läuft über die MQTT-Integration
        name = device.name_by_user or device.name or "Gerät"
        if "mqtt" in domains and any(
            identifier[0] == "mqtt" for identifier in device.identifiers
        ):
            domains.add("zigbee2mqtt")

        net = _net_for(domains)
        if net is None:
            continue

        entities = entities_by_device.get(device.id, [])
        battery = any(
            (entry.original_device_class in _BATTERY_CLASSES)
            or (entry.device_class in _BATTERY_CLASSES)
            or entry.entity_id.endswith("_battery")
            for entry in entities
        )

        model = device.model or ""
        if _looks_like_root(name, model):
            role = ROOT_ROLE_BY_NET.get(net, "end")
        elif battery:
            role = DEFAULT_ROLE_BY_NET.get(net, "end")
        else:
            role = ROUTER_ROLE_BY_NET.get(net, "end")

        area = areas.get(device.area_id) if device.area_id else None
        floor = floors.get(area["floor_id"]) if area and area.get("floor_id") else None

        devices.append(
            {
                "id": device.id,
                "name": name,
                "manufacturer": device.manufacturer,
                "model": model,
                "integrations": sorted(domains),
                "net": net,
                "role": role,
                "battery": battery,
                "area": area["name"] if area else None,
                "area_id": device.area_id,
                "floor": floor["name"] if floor else None,
                "floor_id": floor["id"] if floor else None,
                "entities": len(entities),
            }
        )

    devices.sort(key=lambda d: ((d["floor"] or "~"), (d["area"] or "~"), d["name"]))
    return {
        "devices": devices,
        "areas": list(areas.values()),
        "floors": sorted(floors.values(), key=lambda f: (f.get("level") or 0)),
    }


async def async_signal_quality(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Gemessene Werte (LQI, RSSI) je Gerät – Grundlage für eine spätere Kalibrierung."""
    dev_reg = dr.async_get(hass)
    ent_reg = er.async_get(hass)
    result: list[dict[str, Any]] = []

    for entry in ent_reg.entities.values():
        if not entry.device_id:
            continue
        key = entry.entity_id.rsplit(".", 1)[-1]
        if not any(token in key for token in ("lqi", "rssi", "link_quality", "signal_strength")):
            continue
        state = hass.states.get(entry.entity_id)
        if state is None or state.state in ("unknown", "unavailable", ""):
            continue
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            continue
        device = dev_reg.async_get(entry.device_id)
        result.append(
            {
                "device_id": entry.device_id,
                "device": (device.name_by_user or device.name) if device else None,
                "entity_id": entry.entity_id,
                "kind": "lqi" if ("lqi" in key or "link_quality" in key) else "rssi",
                "value": value,
            }
        )
    return result
