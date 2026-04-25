# envforge

> CLI tool to snapshot, diff, and restore environment variable sets across projects and machines.

---

## Installation

```bash
pip install envforge
```

Or with pipx for isolated installs:

```bash
pipx install envforge
```

---

## Usage

**Snapshot your current environment:**
```bash
envforge snapshot save my-project
```

**List saved snapshots:**
```bash
envforge snapshot list
```

**Diff two snapshots (or snapshot vs. current environment):**
```bash
envforge snapshot diff my-project
envforge snapshot diff my-project other-project
```

**Restore a snapshot:**
```bash
envforge snapshot restore my-project
```

Restored variables are written to a `.env` file in the current directory by default, ready for use with tools like `direnv` or `python-dotenv`.

---

## Why envforge?

Switching between projects often means juggling different API keys, database URLs, and config flags. `envforge` lets you capture, compare, and reload those variable sets instantly — no more manual copy-pasting or forgotten variables.

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any significant changes.

---

## License

[MIT](LICENSE)