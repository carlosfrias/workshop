# Installed Extensions

Extensions in this directory are loaded by pi on startup.

## Current Installation

**pi-keyword-router** — Installed from GitHub:
```bash
pi install github:carlosfrias/pi-keyword-router
```

Do NOT manually edit files here — they are managed by `pi install`.

## Configuration

- Project config: `.pi/keyword-router.json`
- Global config: `~/.pi/agent/keyword-router.json`

## Commands

- `/keyword-route` — Show routing status
- `/keyword-route-off` — Disable routing
- `/keyword-route-on` — Re-enable routing

## Development

To develop locally, install from path:
```bash
pi install ../technical-infrastructure/extensions/pi-keyword-router
```

To install from GitHub:
```bash
pi install github:carlosfrias/pi-keyword-router
```
