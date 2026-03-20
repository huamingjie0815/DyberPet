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

## Copyright & License

This project is open source under **GNU General Public License v3 (GPL-3.0)**.

- **Original Version**: Copyright (C) 2022 Chaozhong Liu \<czliubioinfo@gmail.com\>
- **Fork Version**: Copyright (C) 2026 huamingjie0815

This project is a fork of [ChaozhongLiu/DyberPet](https://github.com/ChaozhongLiu/DyberPet), developed on the `feat/lite-version` branch.

### GPL-3.0 License Terms

Under GPL-3.0, you have the right to:

- Freely use, modify, and distribute this software
- Commercial use
- Permanent use

You must:

- **Open Source Distribution**: If you distribute this software or derivative works, you must release under GPL-3.0
- **Retain Copyright Notices**: You must preserve original copyright notices and license files
- **Mark Modifications**: If you modify this project, you must clearly indicate
- **Provide Source Code**: If distributing binaries, you must provide source code

### Derivative Works

If you modify and redistribute this project:

1. Modified versions must be clearly marked as "modified version"
2. All original copyright notices must be retained
3. Derivative works must also be released under GPL-3.0
4. You may add your own copyright notice to the project

See [LICENSE](LICENSE) file for full terms.

---

## Project Origin

This project is forked from [ChaozhongLiu/DyberPet](https://github.com/ChaozhongLiu/DyberPet), developed on the `feat/lite-version` branch.

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

---

## OpenClaw Deep Integration

This project integrates deeply with OpenClaw for real-time pet LLM conversations:

- **WebSocket Real-time Communication**: Pet connects to OpenClaw Gateway via WebSocket
- **Streaming Responses**: AI replies stream in real-time, displayed in chat bubbles
- **Multi-character Port Management**: Each pet character maps to an independent port
- **Chat Panel**: Built-in Chat UI for natural language interaction

### OpenClaw Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        ClawPet                              │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐  │
│  │  PetWidget  │◄──►│ Chat Panel   │◄──►│ OpenClaw    │  │
│  │             │    │              │    │  Client     │  │
│  └─────────────┘    └──────────────┘    └──────┬──────┘  │
│         │                                       │          │
└─────────┼───────────────────────────────────────┼──────────┘
          │                                       ▼
          │              ┌──────────────────────────────┐
          │              │     OpenClaw Gateway          │
          │              └──────────────┬───────────────┘
          │                             │
          ▼                             ▼
   ┌─────────────┐              ┌──────────────────┐
   │  Chat Bubble│              │   LLM Provider   │
   │  (AI Reply) │              │   (GPT/Claude)  │
   └─────────────┘              └──────────────────┘
```

---

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

---

## Project Structure

```
ClawPet/
├── ClawPet/              # Core package
│   ├── core/             # Core modules
│   ├── ClawSettings/     # Settings panel
│   ├── OpenClawClient/   # OpenClaw integration
│   ├── Dashboard/        # Dashboard
│   └── ...
├── res/                  # Resources
├── docs/                 # Documentation
└── run_ClawPet.py        # Entry point
```

---

## Documentation

- [OpenClaw Integration Design](docs/OPENCLAW_INTEGRATION_DESIGN.md)
- [Developer Cheatsheet](DEVELOPER_CHEATSHEET.md)
- [Architecture Deep Dive](ARCHITECTURE_DEEP_DIVE.md)
- [Design Document](DESIGN_DOCUMENT.md)

---

## Third-Party Dependencies

This project uses the following open source libraries:

- [PySide6](https://doc.qt.io/qtforpython/) - Qt bindings
- [PySide6-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) - Fluent UI
- [APScheduler](https://apscheduler.readthedocs.io/) - Task scheduling
- [WebSocket](https://websocket-client.readthedocs.io/) - WebSocket client

See installation commands or environment setup for full dependencies.
