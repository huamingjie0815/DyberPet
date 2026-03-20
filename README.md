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

---

## 版权与许可

本项目基于 **GNU General Public License v3 (GPL-3.0)** 开源。

- **原始版本**: Copyright (C) 2022 Chaozhong Liu \<czliubioinfo@gmail.com\>
- **fork 版本**: Copyright (C) 2026 huamingjie0815

本项目是 [ChaozhongLiu/DyberPet](https://github.com/ChaozhongLiu/DyberPet) 的 fork 版本，在 `feat/lite-version` 分支上开发。

### GPL-3.0 许可条款

根据 GPL-3.0 协议，您有权：

- 自由使用、修改、分发本软件
- 商业使用
- 永久使用

您必须：

- **开源分发**：如果分发本软件或基于本项目的衍生作品，必须在 GPL-3.0 许可下开源
- **保留版权声明**：必须保留原始版权声明和许可证文件
- **标明修改**：如果修改本项目，必须明确标明
- **提供源代码**：如果以二进制形式分发，必须提供源代码

### 衍生项目

如果您基于本项目进行修改并分发：

1. 修改版本必须明确标注为"修改版本"
2. 必须保留所有原始版权声明
3. 衍生作品必须同样采用 GPL-3.0 协议开源
4. 可以在项目中添加自己的版权声明

详细条款请参阅 [LICENSE](LICENSE) 文件。

---

## 项目起源

本项目 fork 自 [ChaozhongLiu/DyberPet](https://github.com/ChaozhongLiu/DyberPet)，在 `feat/lite-version` 分支上进行开发。

这是一个**轻量版本**，移除了复杂的功能，保留核心体验：

- ~~HP/饱食度系统~~
- ~~物品/背包系统~~
- ~~Buff 增益系统~~
- ~~迷你宠物系统~~

保留核心功能：
- 桌面宠物显示与动画
- 鼠标交互（拖拽、点击、摸摸）
- 多宠物切换
- OpenClaw 深度集成

---

## OpenClaw 深度集成

本项目深度集成 OpenClaw，实现宠物与 LLM 的实时对话：

- **WebSocket 实时通信**：宠物通过 WebSocket 与 OpenClaw Gateway 保持连接
- **流式响应**：支持 AI 回复的流式输出，实时显示在对话气泡中
- **多角色端口管理**：每个宠物角色对应独立端口
- **聊天面板**：内置 Chat UI，支持与宠物进行自然语言对话

### OpenClaw 架构

```
┌─────────────────────────────────────────────────────────────┐
│                        ClawPet                              │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐  │
│  │  PetWidget  │◄──►│ Chat Panel   │◄──►│ OpenClaw    │  │
│  │  (桌面宠物)  │    │  (聊天面板)   │    │  Client     │  │
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
   │  对话气泡   │              │   LLM Provider   │
   │  显示AI回复 │              │   (GPT/Claude)  │
   └─────────────┘              └──────────────────┘
```

---

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

---

## 项目结构

```
ClawPet/
├── ClawPet/              # 核心包
│   ├── core/             # 核心模块
│   ├── ClawSettings/     # 设置面板
│   ├── OpenClawClient/   # OpenClaw 集成
│   ├── Dashboard/        # 仪表盘
│   └── ...
├── res/                  # 资源文件
├── docs/                 # 文档
└── run_ClawPet.py        # 入口
```

---

## 相关文档

- [OpenClaw 集成设计](docs/OPENCLAW_INTEGRATION_DESIGN.md)
- [开发速查表](DEVELOPER_CHEATSHEET.md)
- [架构深度分析](ARCHITECTURE_DEEP_DIVE.md)
- [设计文档](DESIGN_DOCUMENT.md)

---

## 第三方依赖

本项目使用以下开源库：

- [PySide6](https://doc.qt.io/qtforpython/) - Qt 绑定
- [PySide6-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) - Fluent UI
- [APScheduler](https://apscheduler.readthedocs.io/) - 任务调度
- [WebSocket](https://websocket-client.readthedocs.io/) - WebSocket 客户端

详细依赖请参阅 `requirements.txt` 或环境安装命令。
