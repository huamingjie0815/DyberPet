<h1 align="center">
  ClawPet | 爪宠物
</h1>

<p align="center">
  基于 PySide6 的桌面宠物开发框架
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/huamingjie0815/DyberPet.svg">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg">
</p>

![Interface](docs/ClawPet.png)

## 特性

- 多种桌面宠物支持
- 鼠标交互（拖拽、点击）
- 自定义动作和动画
- 轻量级桌面应用
- 跨平台支持（Windows/macOS）

## 快速开始

### 环境要求

- Python 3.9+
- Conda 环境

### 安装依赖

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

### 运行

```bash
python run_ClawPet.py
```

## 项目结构

```
ClawPet/
├── ClawPet/           # 核心包
│   ├── core/          # 核心模块
│   │   ├── pet_animation.py
│   │   ├── pet_interaction.py
│   │   ├── pet_scheduler.py
│   │   ├── accessory.py
│   │   └── notification.py
│   ├── ClawSettings/  # 设置面板
│   ├── OpenClawClient/# OpenClaw 集成
│   ├── Dashboard/      # 仪表盘
│   ├── pet_widget.py  # 主宠物窗口
│   ├── config.py      # 配置
│   └── settings.py    # 设置
├── res/               # 资源文件
│   └── role/          # 角色素材
├── docs/              # 文档
└── run_ClawPet.py    # 入口
```

## 开发

### 素材开发

参考 [素材开发文档](docs/art_dev.md)

### 添加新角色

1. 在 `res/role/` 下创建角色文件夹
2. 配置 `pet_conf.json` 和 `act_conf.json`
3. 在应用中选择导入

## 文档

- [开发速查表](DEVELOPER_CHEATSHEET.md)
- [架构分析](ARCHITECTURE_DEEP_DIVE.md)
- [设计文档](DESIGN_DOCUMENT.md)

## License

MIT License
