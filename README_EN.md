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

---

## Fork Origin

This project is forked from [ChaozhongLiu/DyberPet](https://github.com/ChaozhongLiu/DyberPet), developed on the `feat/lite-version` branch.

## Lite Version

This is a **lite version** with simplified features, keeping only the core experience:

- ~~HP/Satiety system~~
- ~~Item/Inventory system~~
- ~~Buff system~~
- ~~Mini-pet system~~

Kept core features:
- Desktop pet display and animation
- Mouse interaction (drag, click, pet)
- Multi-pet switching
- OpenClaw deep integration

## OpenClaw Deep Integration

This project provides **deep integration with OpenClaw** for real-time pet LLM conversations:

- **WebSocket Real-time Communication**: Pet connects to OpenClaw Gateway via WebSocket
- **Streaming Responses**: AI replies stream in real-time, displayed in chat bubbles
- **Multi-character Port Management**: Each pet character maps to an independent port
- **Chat Panel**: Built-in Chat UI for natural language interaction
- **Context Memory**: Multi-turn conversations via OpenClaw history management

### OpenClaw Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        ClawPet                              │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐  │
│  │  PetWidget  │◄──►│ Chat Panel   │◄──►│ OpenClaw    │  │
│  │  (Desktop)  │    │              │    │  Client     │  │
│  └─────────────┘    └──────────────┘    └──────┬──────┘  │
│         │                                       │          │
└─────────┼───────────────────────────────────────┼──────────┘
          │                                       ▼
          │              ┌──────────────────────────────┐
          │              │     OpenClaw Gateway         │
          │              │   (WebSocket Server)        │
          │              └──────────────┬───────────────┘
          │                             │
          ▼                             ▼
   ┌─────────────┐              ┌──────────────────┐
   │  Chat Bubble│              │   LLM Provider   │
   │  (AI Reply)│              │   (GPT/Claude)  │
   └─────────────┘              └──────────────────┘
```

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

### Configure OpenClaw

1. Enable OpenClaw in Settings
2. Configure OpenClaw Gateway address and port
3. Set authentication Token
4. Restart app to start chatting with your pet

## Project Structure

```
ClawPet/
├── ClawPet/              # Core package
│   ├── core/             # Core modules
│   │   ├── pet_animation.py    # Animation module
│   │   ├── pet_interaction.py  # Interaction module
│   │   ├── pet_scheduler.py    # Scheduler
│   │   ├── accessory.py       # Accessory system
│   │   └── notification.py    # Notification system
│   ├── ClawSettings/     # Settings panel
│   │   ├── control_panel.py    # Main control panel
│   │   ├── chat_ui.py         # Chat interface
│   │   └── appearance_ui.py    # Appearance settings
│   ├── OpenClawClient/   # OpenClaw integration
│   │   ├── websocket_client.py  # WebSocket client
│   │   ├── gateway_manager.py   # Gateway port management
│   │   └── chat_history.py     # Chat history
│   ├── Dashboard/        # Dashboard
│   ├── pet_widget.py     # Main pet window
│   ├── config.py         # Configuration
│   └── settings.py       # Settings
├── res/                  # Resources
│   └── role/            # Character assets
├── docs/                 # Documentation
└── run_ClawPet.py        # Entry point
```

## Differences from Original DyberPet

| Feature | Original DyberPet | ClawPet (Lite) |
|---------|-----------------|-----------------|
| HP/Satiety | ✓ | ✗ |
| Item System | ✓ | ✗ |
| Buff System | ✓ | ✗ |
| Mini-pet | ✓ | ✗ |
| Shop | ✓ | ✗ |
| Task System | ✓ | ✗ |
| Desktop Pet Core | ✓ | ✓ |
| Mouse Interaction | ✓ | ✓ |
| OpenClaw Integration | ✗ | ✓ (Deep) |

## Development

### Asset Development

See [Asset Development Guide](docs/art_dev.md)

### Adding New Characters

1. Create character folder under `res/role/`
2. Configure `pet_conf.json` and `act_conf.json`
3. Import via the app

## Documentation

- [OpenClaw Integration Design](docs/OPENCLAW_INTEGRATION_DESIGN.md)
- [Developer Cheatsheet](DEVELOPER_CHEATSHEET.md)
- [Architecture Deep Dive](ARCHITECTURE_DEEP_DIVE.md)
- [Design Document](DESIGN_DOCUMENT.md)

## License

MIT License
