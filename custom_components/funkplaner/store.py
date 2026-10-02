"""Projektspeicher des Funkplaners."""

from __future__ import annotations

import time
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .const import STORAGE_KEY, STORAGE_VERSION


class ProjectStore:
    """Hält alle Pläne in .storage/funkplaner.projects."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store[dict[str, Any]] = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, Any] = {"projects": {}, "current": None}
        self._loaded = False

    async def async_load(self) -> None:
        data = await self._store.async_load()
        if isinstance(data, dict) and isinstance(data.get("projects"), dict):
            self._data = {"projects": data["projects"], "current": data.get("current")}
        self._loaded = True

    async def _async_save(self) -> None:
        await self._store.async_save(self._data)

    def list(self) -> dict[str, Any]:
        """Kurzliste ohne Plandaten, damit die Antwort klein bleibt."""
        projects = [
            {"id": pid, "name": p.get("name") or "Projekt", "updated": p.get("updated", 0)}
            for pid, p in self._data["projects"].items()
        ]
        projects.sort(key=lambda p: p["updated"], reverse=True)
        current = self._data.get("current")
        if current not in self._data["projects"]:
            current = projects[0]["id"] if projects else None
        return {"projects": projects, "current": current}

    def get(self, project_id: str) -> dict[str, Any]:
        project = self._data["projects"].get(project_id) or {}
        return {
            "id": project_id,
            "name": project.get("name"),
            "state": project.get("state"),
            "images": project.get("images") or {},
        }

    async def async_save(
        self, project_id: str, name: str, state: dict, images: dict | None
    ) -> None:
        self._data["projects"][project_id] = {
            "name": name,
            "state": state,
            "images": images or {},
            "updated": int(time.time() * 1000),
        }
        self._data["current"] = project_id
        await self._async_save()

    async def async_delete(self, project_id: str) -> None:
        self._data["projects"].pop(project_id, None)
        if self._data.get("current") == project_id:
            self._data["current"] = next(iter(self._data["projects"]), None)
        await self._async_save()
