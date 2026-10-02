"""WebSocket-Schnittstelle des Funkplaners."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback

from . import devices as devices_mod
from .const import DOMAIN
from .store import ProjectStore


def _store(hass: HomeAssistant) -> ProjectStore:
    return hass.data[DOMAIN]["store"]


@callback
def async_register(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_list)
    websocket_api.async_register_command(hass, ws_get)
    websocket_api.async_register_command(hass, ws_save)
    websocket_api.async_register_command(hass, ws_delete)
    websocket_api.async_register_command(hass, ws_devices)
    websocket_api.async_register_command(hass, ws_signal)


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/list"})
@websocket_api.async_response
async def ws_list(hass: HomeAssistant, connection, msg: dict[str, Any]) -> None:
    connection.send_result(msg["id"], _store(hass).list())


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/get", vol.Required("project_id"): str}
)
@websocket_api.async_response
async def ws_get(hass: HomeAssistant, connection, msg: dict[str, Any]) -> None:
    connection.send_result(msg["id"], _store(hass).get(msg["project_id"]))


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/save",
        vol.Required("project_id"): str,
        vol.Required("name"): str,
        vol.Required("state"): dict,
        vol.Optional("images"): dict,
    }
)
@websocket_api.async_response
async def ws_save(hass: HomeAssistant, connection, msg: dict[str, Any]) -> None:
    await _store(hass).async_save(
        msg["project_id"], msg["name"], msg["state"], msg.get("images")
    )
    connection.send_result(msg["id"], {"saved": True})


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/delete", vol.Required("project_id"): str}
)
@websocket_api.async_response
async def ws_delete(hass: HomeAssistant, connection, msg: dict[str, Any]) -> None:
    await _store(hass).async_delete(msg["project_id"])
    connection.send_result(msg["id"], {"deleted": True})


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/devices"})
@websocket_api.async_response
async def ws_devices(hass: HomeAssistant, connection, msg: dict[str, Any]) -> None:
    connection.send_result(msg["id"], await devices_mod.async_collect(hass))


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/signal"})
@websocket_api.async_response
async def ws_signal(hass: HomeAssistant, connection, msg: dict[str, Any]) -> None:
    connection.send_result(
        msg["id"], {"measurements": await devices_mod.async_signal_quality(hass)}
    )
