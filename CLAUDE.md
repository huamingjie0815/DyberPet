# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DyberPet (呆啵宠物) is a PySide6-based desktop pet development framework. The current branch (`feat/lite-version`) implements a simplified version that removes HP/FV, items, buff, and subpet systems, keeping only core pet display, animation, and mouse interaction.

## Environment Setup

```bash
conda create --name Dyber_pyside python=3.9.18
conda activate Dyber_pyside
conda install -c conda-forge apscheduler
pip install pynput==1.7.6
pip install PySide6-Fluent-Widgets==1.5.4 -i https://pypi.org/simple/
pip install pyside6==6.5.2
pip install tendo
```

**CRITICAL**: All development and testing must be done within the `Dyber_pyside` conda environment.

## Running the Application

```bash
conda activate Dyber_pyside
python run_DyberPet.py
```

## Architecture

```
run_DyberPet.py          # Application entry point
├── DyberPet.DyberPet   # Main PetWidget (desktop pet window)
├── DyberPet.Notification # Bubble/notification system
├── DyberPet.Accessory  # Accessories overlay system
├── DyberPet.DyberSettings.DyberControlPanel # Settings panel
└── DyberPet.Dashboard.DashboardUI # Dashboard with tasks, animations
```

### Core Components

- **PetWidget**: Main desktop pet window with physics, collision detection, animations
- **BubbleManager**: Chat bubbles and notifications
- **ControlMainWindow**: Settings and character management
- **DashboardMainWindow**: Task timers, animation designer, status logs

### Signal-based Communication

The system uses Qt signals for inter-component communication. Key signals include:
- `change_pet`: Switch pet character
- `show_dashboard`: Toggle dashboard
- `setup_notification`: Trigger bubble messages
- `setup_acc`: Show accessories

## Key Constraints

1. **No extra comments**: Do not add explanatory comments to code
2. **Remove unused code**: Delete dead code directly instead of commenting out
3. **Use conda environment**: Always activate `Dyber_pyside` before running or testing
