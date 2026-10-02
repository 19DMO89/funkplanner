/* Funkplaner – Panel für Home Assistant.
   Lädt den Planer in einem iframe und beantwortet dessen Anfragen über die
   WebSocket-Verbindung von Home Assistant. Dadurch braucht der Planer selbst
   keinen Zugriff auf Tokens. */

class FunkplanerPanel extends HTMLElement {
  static get properties() {
    return { hass: {}, narrow: {}, route: {}, panel: {} };
  }

  set hass(hass) {
    this._hass = hass;
    this._render();
  }
  get hass() {
    return this._hass;
  }

  set panel(panel) {
    this._panel = panel;
    this._render();
  }

  connectedCallback() {
    if (!this._onMessage) {
      this._onMessage = (ev) => this._handle(ev);
      window.addEventListener("message", this._onMessage);
    }
    this._render();
  }

  disconnectedCallback() {
    if (this._onMessage) {
      window.removeEventListener("message", this._onMessage);
      this._onMessage = null;
    }
  }

  _staticPath() {
    return (this._panel && this._panel.config && this._panel.config.static_path) || "/funkplaner-static";
  }

  _render() {
    if (this._frame || !this._hass) return;
    const style = document.createElement("style");
    style.textContent = `
      :host { display:block; position:relative; height:100vh; height:100dvh; }
      iframe { position:absolute; inset:0; border:0; width:100%; height:100%; display:block; background:var(--primary-background-color); }
    `;
    const frame = document.createElement("iframe");
    const dark = this._hass.themes && this._hass.themes.darkMode ? "dark" : "light";
    const ver = (this._panel && this._panel.config && this._panel.config.version) || "";
    frame.src = `${this._staticPath()}/index.html?ha=1&theme=${dark}&v=${encodeURIComponent(ver)}`;
    frame.setAttribute("allow", "clipboard-write");
    this.attachShadow({ mode: "open" });
    this.shadowRoot.append(style, frame);
    this._frame = frame;
  }

  async _handle(ev) {
    const msg = ev.data;
    if (!msg || msg.type !== "fp-request") return;
    if (!this._frame || ev.source !== this._frame.contentWindow) return;

    const reply = (result, error) =>
      this._frame.contentWindow.postMessage(
        { type: "fp-reply", id: msg.id, result, error },
        "*"
      );

    try {
      const p = msg.payload || {};
      let result;
      switch (msg.what) {
        case "list":
          result = await this._hass.callWS({ type: "funkplaner/list" });
          break;
        case "get":
          result = await this._hass.callWS({ type: "funkplaner/get", project_id: p.id });
          break;
        case "save":
          result = await this._hass.callWS({
            type: "funkplaner/save",
            project_id: p.id,
            name: p.name || "Projekt",
            state: p.state,
            images: p.images || {},
          });
          break;
        case "delete":
          result = await this._hass.callWS({ type: "funkplaner/delete", project_id: p.id });
          break;
        case "devices":
          result = await this._hass.callWS({ type: "funkplaner/devices" });
          break;
        case "signal":
          result = await this._hass.callWS({ type: "funkplaner/signal" });
          break;
        default:
          throw new Error(`Unbekannte Anfrage: ${msg.what}`);
      }
      reply(result, undefined);
    } catch (err) {
      reply(undefined, (err && err.message) || String(err));
    }
  }
}

customElements.define("funkplaner-panel", FunkplanerPanel);
