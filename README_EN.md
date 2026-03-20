<h1 align="center">
  ClawPet
</h1>

<p align="center">
  PySide6-based Desktop Pet Development Framework
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/huamingjie0815/DyberPet.svg">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg">
</p>

![Interface](docs/ClawPet.png)

## Features

- Multiple desktop pet support
- Mouse interaction (drag, click)
- Custom actions and animations
- Lightweight desktop application
- Cross-platform (Windows/macOS)

## Quick Start

### Requirements

- Python 3.9+
- Conda environment

### Install Dependencies

```bash
conda create --name claw_pet python=3.9.18
conda activate claw_pet
conda install -c conda-forge apscheduler
pip install pynput==1.7.6
pip install PySide6-Fluent-Widgets==1.5.4 -i https://pypi.org/simple/
pip install pyside6==6.5.2
pip install tendo
pip install websocket-client
```

### Run

```bash
python run_ClawPet.py
```

## Project Structure

```
ClawPet/
├── ClawPet/           # Core package
│   ├── core/          # Core modules
│   │   ├── pet_animation.py
│   │   ├── pet_interaction.py
│   │   ├── pet_scheduler.py
│   │   ├── accessory.py
│   │   └── notification.py
│   ├── ClawSettings/  # Settings panel
│   ├── OpenClawClient/# OpenClaw integration
│   ├── Dashboard/      # Dashboard
│   ├── pet_widget.py  # Main pet window
│   ├── config.py      # Configuration
│   └── settings.py    # Settings
├── res/               # Resources
│   └── role/          # Character assets
├── docs/              # Documentation
└── run_ClawPet.py    # Entry point
```

## Development

### Asset Development

See [Asset Development Guide](docs/art_dev.md)

### Adding New Characters

1. Create character folder under `res/role/`
2. Configure `pet_conf.json` and `act_conf.json`
3. Import via the app

## Documentation

- [Developer Cheatsheet](DEVELOPER_CHEATSHEET.md)
- [Architecture Deep Dive](ARCHITECTURE_DEEP_DIVE.md)
- [Design Document](DESIGN_DOCUMENT.md)

## License

MIT License
