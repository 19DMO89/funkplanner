"""Funkplaner – Funk- und Netzwerkplanung in Home Assistant."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PANEL_ICON, PANEL_TITLE, PANEL_URL, STATIC_PATH
from .store import ProjectStore
from . import websocket as ws

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration einrichten."""
    store = ProjectStore(hass)
    await store.async_load()

    hass.data.setdefault(DOMAIN, {})["store"] = store

    # Panel, statische Dateien und WebSocket-Befehle nur einmal einrichten
    if not hass.data.get(f"{DOMAIN}_registered"):
        hass.data[f"{DOMAIN}_registered"] = True
        ws.async_register(hass)

        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    STATIC_PATH, str(Path(__file__).parent / "www"), cache_headers=False
                )
            ]
        )

        from homeassistant.components import panel_custom

        await panel_custom.async_register_panel(
            hass,
            frontend_url_path=PANEL_URL.lstrip("/"),
            webcomponent_name="funkplaner-panel",
            module_url=f"{STATIC_PATH}/funkplaner-panel.js",
            sidebar_title=PANEL_TITLE,
            sidebar_icon=PANEL_ICON,
            require_admin=False,
            config={"static_path": STATIC_PATH},
        )
        _LOGGER.debug("Funkplaner-Panel unter %s registriert", PANEL_URL)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration entfernen."""
    from homeassistant.components import frontend

    frontend.async_remove_panel(hass, PANEL_URL.lstrip("/"))
    hass.data.pop(DOMAIN, None)
    hass.data.pop(f"{DOMAIN}_registered", None)
    return True
