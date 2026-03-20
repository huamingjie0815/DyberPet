# ClawPet × OpenClaw 融合方案设计

> v2.1 | 2026-03-19

---

## 目录

1. [需求与现状分析](#1-需求与现状分析)
2. [总体架构设计](#2-总体架构设计)
3. [模块一：功能裁剪](#3-模块一功能裁剪)
4. [模块二：角色 ↔ OpenClaw Gateway 端口管理](#4-模块二角色--openclaw-gateway-端口管理)
5. [模块三：Chat UI 重构](#5-模块三chat-ui-重构)
6. [模块四：宠物右键菜单重构](#6-模块四宠物右键菜单重构)
7. [数据模型设计](#7-数据模型设计)
8. [技术选型分析](#8-技术选型分析)
9. [工作分解与实施计划](#9-工作分解与实施计划)
10. [风险与应对](#10-风险与应对)
11. [交付物清单](#11-交付物清单)

---

## 1. 需求与现状分析

### 1.1 需求清单

| ID | 需求 | 说明 |
|----|------|------|
| R1 | **删除角色状态** | 移除 `statusInterface`（HP/FV/状态日志 等） |
| R2 | **删除游戏存档** | 移除 `gamesaveInterface`（存档读档功能） |
| R3 | **删除日常任务** | 移除 `taskInterface`（番茄钟、专注计时器等） |
| R4 | **角色 = Gateway 实体** | 每个 ClawPet 角色对应一个 OpenClaw Gateway 端口，切换角色时自动停止旧 Gateway、启动新 Gateway |
| R5 | **Chat UI 优化** | 支持 Markdown 渲染、图片展示、查询历史消息 |
| R6 | **菜单简化** | 右键宠物菜单仅保留 **Chat**、**OpenClaw**、**Exit** 三项；删除 Dashboard、System、选择动作、召唤伙伴、更换角色 |
| R7 | **OpenClaw 入口** | 菜单点击 OpenClaw 后打开浏览器访问 `http://127.0.0.1:<当前角色端口>` 的 OpenClaw WebUI |
| R8 | **仅修改 Pet 代码** | 变更范围限于 ClawPet 项目本身，不修改 OpenClaw |

### 1.2 当前集成状态

| 组件 | 文件 | 状态 |
|------|------|------|
| WebSocket 客户端 | `ClawPet/OpenClawClient/websocket_client.py` | ✅ 已实现 |
| Gateway Protocol v3 | `ClawPet/OpenClawClient/protocol.py` | ✅ 已实现 |
| Ed25519 设备认证 | `ClawPet/OpenClawClient/device_identity.py` | ✅ 已实现 |
| Chat UI | `ClawPet/DyberSettings/chat_ui.py` | ⚠️ 基础实现，不支持 Markdown/图片/历史 |
| Settings 配置 | `ClawPet/settings.py` | ✅ `openclaw_enabled`/`url`/`token`/`auto_reconnect` |

### 1.3 需删除的功能模块

| 功能 | 当前所在文件 | 涉及的 UI 入口 |
|------|-------------|---------------|
| 角色状态 (HP/FV/日志) | `ClawPet/Dashboard/status_ui.py` | ControlMainWindow Home 标签 |
| 游戏存档 | `ClawPet/DyberSettings/game_save_ui.py` | ControlMainWindow Save & Load 标签 |
| 日常任务/番茄钟 | `ClawPet/Dashboard/task_ui.py` | ControlMainWindow Focus 标签 |
| 选择动作菜单 | `pet_widget.py` `_set_menu()` → `act_menu` | 右键菜单子菜单 |
| 召唤伙伴菜单 | `pet_widget.py` `_set_menu()` → `companion_menu` | 右键菜单子菜单 |
| 更换角色菜单 | `pet_widget.py` `_set_menu()` → `change_menu` | 右键菜单子菜单 |
| Dashboard 入口 | `pet_widget.py` → `_show_dashboard()` | 右键菜单 Dashboard |
| System 入口 | `pet_widget.py` → `_show_controlPanel()` | 右键菜单 System（设置功能保留但移至 ChatWindow 导航） |

---

## 2. 总体架构设计

### 2.1 重构后架构

```
┌──────────────────────────────────────────────────────────────┐
│                    ClawPet 桌面宠物                          │
│                                                              │
│  ┌────────────────┐      ┌─────────────────────────────────┐ │
│  │   PetWidget    │      │  MainPanel (FluentWindow)       │ │
│  │  (桌面宠物)    │      │                                 │ │
│  │                │      │  ┌─────┐ ┌───────────────────┐  │ │
│  │  右键菜单:     │ ────→│  │ 💬  │ │ Chat 页面         │  │ │
│  │  · Chat       │      │  │Chat │ │ ┌───────────────┐ │  │ │
│  │  · OpenClaw   │      │  │     │ │ │消息列表+Markdown│ │  │ │
│  │  · Exit       │      │  │─────│ │ │(流式+图片+历史)│ │  │ │
│  │               │      │  │ ⚙️  │ │ ├───────────────┤ │  │ │
│  └───────┬───────┘      │  │设置 │ │ │输入框 + 发送   │ │  │ │
│          │               │  │     │ │ ├───────────────┤ │  │ │
│          │               │  └─────┘ │ │角色-Gateway    │ │  │ │
│          │               │          │ │管理区(下方)    │ │  │ │
│          │               │          │ └───────────────┘ │  │ │
│          │               │          ├───────────────────┤  │ │
│          │               │          │ Settings 页面     │  │ │
│          │               │          │ (缩放/置顶/语言等)│  │ │
│          │               │          └───────────────────┘  │ │
│          │               └─────────────────────────────────┘ │
│          │                                                    │
│  ┌───────▼──────────────────────────────────────────────────┐ │
│  │            GatewayProcessManager (单例)                  │ │
│  │  · 管理当前角色对应的 Gateway 子进程                       │ │
│  │  · 同一时刻只有一个 Gateway 运行                           │ │
│  │  · 切换角色: stop 旧 → start 新 → WS 自动重连             │ │
│  └──────────────────────┬───────────────────────────────────┘ │
└─────────────────────────┼────────────────────────────────────┘
                          │
               ┌──────────▼──────────────┐
               │  OpenClaw Gateway       │
               │  --profile <角色名>     │
               │  --port <角色端口>      │
               │  ~/.openclaw-<角色名>/  │
               └─────────────────────────┘
```

### 2.2 核心设计决策

| 决策 | 方案 | 理由 |
|------|------|------|
| 主面板形态 | **FluentWindow** 多导航 | Chat 和 Settings 同一面板不同导航页，复用 qfluentwidgets 风格 |
| 角色管理入口 | Chat 页面 **底部** 角色-Gateway 管理区 | 用户在 Chat 下方直接管理角色切换和 Gateway 状态 |
| Gateway 进程管理 | `QProcess` 单例 | 同一时刻只运行当前角色的 Gateway |
| Gateway 隔离 | `--profile <name>` | OpenClaw 原生支持，隔离到 `~/.openclaw-<name>/` |
| Markdown 渲染 | `QTextBrowser` + `markdown` Python 库 | PySide6 内置，无额外 UI 依赖 |
| 图片展示 | `<img>` 标签嵌入 `QTextBrowser` | 支持 base64 和本地路径 |
| 历史消息 | 本地 JSON 文件 | 简单，与项目现有模式一致 |
| OpenClaw WebUI | `QDesktopServices.openUrl()` | 直接用系统浏览器打开，无需内嵌 |

### 2.3 信号流总览

```
PetWidget
│
├── 右键菜单 "Chat"
│   └── → show_chat.emit()
│         └── → MainPanel.show() + 切换到 Chat 页面
│
├── 右键菜单 "OpenClaw"
│   └── → open_openclaw_webui()
│         └── → QDesktopServices.openUrl("http://127.0.0.1:<port>")
│
├── 右键菜单 "Exit"
│   └── → quit()
│
└── _change_pet(new_name)  [由 MainPanel Chat 页面角色管理区触发]
    ├── 切换动画/资源
    └── GatewayProcessManager.switch_gateway(new_name, port)
        ├── stop_gateway()  ← 停止旧进程
        ├── start_gateway()  ← 启动新进程
        └── gateway_started → Chat 页面自动重连 WS
```

---

## 3. 模块一：功能裁剪

### 3.1 删除的组件与文件变更

#### 3.1.1 ControlMainWindow 重构

**当前** (`control_panel.py`):
```
ControlMainWindow(FluentWindow)
├── statusInterface (Home)         ← 删除
├── charCardInterface (Characters) ← 角色管理移入 Chat 页面底部
├── taskInterface (Focus)          ← 删除
├── gamesaveInterface (Save & Load)← 删除
├── chatInterface (Chat)           ← 重构为 Chat 导航页
├── settingInterface (Settings)    ← 保留为 Settings 导航页
```

**重构后**：`ControlMainWindow` 重构为 `MainPanel(FluentWindow)`，仅保留 Chat 和 Settings 两个导航页：
```
MainPanel(FluentWindow)
├── chatInterface (Chat)           ← 包含聊天 + 角色-Gateway 管理
└── settingInterface (Settings)    ← 保留原有设置功能
```

#### 3.1.2 run_ClawPet.py 变更

删除以下信号连接：

```python
# 删除 - statusInterface 相关
self.note.noteToLog.connect(self.conp.statusInterface._addNote)

# 删除 - settingInterface 相关
self.conp.settingInterface.ontop_changed.connect(...)
self.conp.settingInterface.scale_changed.connect(...)
self.conp.settingInterface.lang_changed.connect(...)

# 删除 - gamesaveInterface 相关
self.conp.gamesaveInterface.refresh_pet.connect(...)

# 删除 - taskInterface 相关
self.conp.taskInterface.focusPanel.start_pomodoro.connect(...)
self.conp.taskInterface.focusPanel.cancel_pomodoro.connect(...)
self.conp.taskInterface.focusPanel.start_focus.connect(...)
self.conp.taskInterface.focusPanel.cancel_focus.connect(...)
self.p.taskUI_Timer_update.connect(...)
self.p.taskUI_task_end.connect(...)
self.p.single_pomo_done.connect(...)

# 删除 - Dashboard 相关
self.p.show_dashboard.connect(...)
```

新增：

```python
# MainPanel 替代 ControlMainWindow（保留 FluentWindow 框架，仅含 Chat + Settings）
self.panel = MainPanel()

# 信号连接
self.p.show_chat.connect(self.panel.show_chat)
self.panel.chatInterface.change_pet.connect(self.p._change_pet)
self.p.change_note.connect(self.panel.chatInterface.on_pet_changed)

# Settings 信号（保留原有设置功能）
self.panel.settingInterface.ontop_changed.connect(self.acc.ontop_changed)
self.panel.settingInterface.scale_changed.connect(self.acc.reset_size_sig)
self.panel.settingInterface.ontop_changed.connect(self.p.ontop_update)
self.panel.settingInterface.scale_changed.connect(self.p.reset_size)
self.panel.settingInterface.lang_changed.connect(self.p.lang_changed)
self.p.change_note.connect(self.panel.settingInterface._update_scale)
```

#### 3.1.3 PetWidget 信号裁剪

删除不再需要的信号：

```python
# 删除
show_controlPanel = Signal(...)   # 不再有独立控制面板入口（设置通过 MainPanel 导航）
show_dashboard = Signal(...)      # 不再有 Dashboard
hp_updated = Signal(...)          # 无 HP 系统
fv_updated = Signal(...)          # 无 FV 系统
compensate_rewards = Signal(...)  # 无奖励系统
refresh_bag = Signal(...)         # 无背包
addCoins = Signal(...)            # 无硬币
autofeed = Signal(...)            # 无自动喂食
taskUI_Timer_update = Signal(...) # 无任务计时
taskUI_task_end = Signal(...)     # 无任务
single_pomo_done = Signal(...)    # 无番茄钟
addItem_toInven = Signal(...)     # 无物品
fvlvl_changed_main_note = Signal(...)  # 无 FV
fvlvl_changed_main_inve = Signal(...)  # 无 FV
hptier_changed_main_note = Signal(...) # 无 HP
```

保留：

```python
setup_notification = Signal(str, str)    # 通知气泡
setup_bubbleText = Signal(dict, int, int)# 文字气泡
close_bubble = Signal(str)               # 关闭气泡
setup_acc = Signal(dict, int, int)       # 配件
change_note = Signal()                   # 角色切换通知
close_all_accs = Signal()               # 关闭所有配件
move_sig = Signal(int, int)             # 位置
send_positions = Signal(list, list)     # 位置
lang_changed = Signal()                 # 语言
show_chat = Signal()                    # 打开 Chat
stopAllThread = Signal()                # 停止线程
```

#### 3.1.4 PetWidget 方法裁剪

删除与已删功能相关的方法/代码：

| 删除方法 | 原因 |
|---------|------|
| `_show_dashboard()` | 无 Dashboard |
| `_show_controlPanel()` | 设置入口改为 MainPanel 导航，不再由右键菜单触发 |
| `_setup_compensate()` / `_stop_compensate()` / `_compensate_rewards()` | 无奖励 |
| `run_tomato()` / `cancel_tomato()` / `run_focus()` / `cancel_focus()` | 无番茄钟 |
| 番茄钟/专注相关 UI (`tomato_time`, `focus_time` 等) | 无计时器 |

#### 3.1.5 HP/FV 系统裁剪

在 `pet_widget.py` 中删除：
- HP 进度条 (`hp_bar`)、FV 进度条 (`fv_bar`)
- HP 等级图标 (`hpicon`)
- 等级徽章 (`lvl_badge`)
- `_init_ui()` 中对应的布局代码

在 `settings.py` 中删除：
- `HP_TIERS`、`TIER_NAMES`、`HP_INTERVAL` 等 HP/FV 常量
- `HP_stop`、`FV_stop` 标志
- `SINGLETASK_REWARD`、`FIVETASK_REWARD` 等任务奖励
- `pet_data`、`task_data`、`act_data` 可视情况保留（`pet_data` 中部分字段被动画引用）

---

## 4. 模块二：角色 ↔ OpenClaw Gateway 端口管理

### 4.1 概述

每个 ClawPet 角色对应一个独立的 OpenClaw Gateway 实例：

```
ClawPet Character          OpenClaw Gateway
──────────────────────────────────────────────────────────
Kitty          ──────→      openclaw --profile Kitty gateway --port 18789
ChrisKitty     ──────→      openclaw --profile ChrisKitty gateway --port 18790
```

**约束**：同一时刻只有一个 Gateway 运行（当前激活角色）。

OpenClaw `--profile <name>` 将所有状态隔离到 `~/.openclaw-<name>/`，包括：
- 独立的配置文件
- 独立的 workspace（SOUL.md、IDENTITY.md 等）
- 独立的 session 和 cron 任务

### 4.2 端口映射

持久化在 `data/settings.json`：

```json
{
    "openclaw_port_dict": {
        "Kitty": 18789,
        "ChrisKitty": 18790
    }
}
```

自动分配逻辑：
```python
DEFAULT_BASE_PORT = 18789

def allocate_port(existing_ports: dict, character_name: str) -> int:
    used = set(existing_ports.values())
    port = DEFAULT_BASE_PORT
    while port in used:
        port += 1
    return port
```

### 4.3 GatewayProcessManager

新增 `ClawPet/OpenClawClient/gateway_manager.py`：

```python
class GatewayProcessManager(QObject):
    """
    管理当前激活角色的 OpenClaw Gateway 子进程。
    同一时刻只有一个 Gateway 运行（单例模式）。
    """

    gateway_started = Signal(str, int)       # (character_name, port)
    gateway_stopped = Signal(str)            # (character_name)
    gateway_error = Signal(str, str)         # (character_name, error_msg)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._process: QProcess | None = None
        self._active_character: str | None = None
        self._active_port: int | None = None

    def switch_gateway(self, character_name: str, port: int, token: str = "") -> bool:
        """停止当前 Gateway，启动目标角色的 Gateway。"""

    def start_gateway(self, character_name: str, port: int, token: str = "") -> bool:
        """启动指定角色的 Gateway，若已有进程则先停止。"""

    def stop_gateway(self) -> None:
        """优雅停止当前 Gateway（terminate → waitForFinished → kill）。"""

    def is_running(self) -> bool:
        """当前 Gateway 是否在运行。"""

    @property
    def active_character(self) -> str | None: ...

    @property
    def active_port(self) -> int | None: ...
```

**进程启动命令**：

```python
def _build_command(self, character_name: str, port: int, token: str = "") -> list[str]:
    cmd = ["openclaw", "--profile", character_name, "gateway", "--port", str(port)]
    if token:
        cmd.extend(["--token", token])
    return cmd
```

**生命周期**：

| 事件 | 行为 |
|------|------|
| 启动 | `QProcess.start(cmd)` → 监听 `started`/`errorOccurred` |
| 正常退出 | `finished` → 发射 `gateway_stopped` |
| 异常退出 | 解析 stderr → 发射 `gateway_error` |
| 切换角色 | `stop_gateway()` → `start_gateway()` → `gateway_started` |
| 应用退出 | `stop_gateway()`: `terminate()` → `waitForFinished(3000)` → `kill()` |

**端口冲突检测**：

```python
import socket

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0
```

### 4.4 Chat 页面中的角色-Gateway 管理区（底部）

在 Chat 页面输入框下方提供角色切换 + Gateway 状态：

```
┌────────────────────────────────────────────────┐
│       Chat with Kitty              [新对话] [重连]  │  ← 标题栏
├────────────────────────────────────────────────┤
│                                                │
│             (消息列表区)                        │
│                                                │
├────────────────────────────────────────────────┤
│  [  输入消息...                     ] [发送]     │  ← 输入框
├────────────────────────────────────────────────┤
│  [角色: Kitty ▼]  :18789  ● 运行中  [⚙]       │  ← 角色-Gateway 管理栏
└──────────────────────────────────────────────────┘
```

组件说明：

| 组件 | 类型 | 功能 |
|------|------|------|
| 角色下拉框 | `ComboBox` | 列出所有可用角色，选择后触发角色切换 |
| 端口标签 | `CaptionLabel` | 显示当前角色的 Gateway 端口号 |
| 状态指示灯 | `QLabel` | `●` 绿色=运行中，`○` 灰色=已停止，`◐` 黄色=启动中 |
| 设置按钮 | `TransparentToolButton` | 弹出端口编辑对话框 |

**角色切换流程**：

```
用户在底部角色下拉框选择 "ChrisKitty"
    │
    ▼
ChatInterface._on_character_selected("ChrisKitty")
    │
    ├── 1. 发射 change_pet.emit("ChrisKitty")
    │       └── PetWidget._change_pet("ChrisKitty")
    │           ├── 切换动画/资源
    │           └── GatewayProcessManager.switch_gateway("ChrisKitty", 18790)
    │                   ├── stop "Kitty:18789"
    │                   └── start "ChrisKitty:18790"
    │
    └── 2. gateway_started 信号回调
            ├── 更新状态指示灯 → ● 绿色
            ├── 更新端口标签 → :18790
            └── WS 客户端重连到 ws://127.0.0.1:18790
```

### 4.5 应用启动时 Gateway 行为

```
ClawPetApp.__init__()
    │
    ├── 创建 GatewayProcessManager 实例
    │
    ├── 读取当前角色 settings.petname
    │
    ├── 查找端口 settings.openclaw_port_dict.get(petname)
    │   └── 若无 → allocate_port() 分配
    │
    └── 若 settings.openclaw_enabled:
        └── gateway_manager.start_gateway(petname, port, token)
```

### 4.6 应用退出时清理

```python
# PetWidget.quit() 或 ClawPetApp 关闭时
gateway_manager.stop_gateway()
```

### 4.7 Gateway 启动后 WS 重连

```python
def _on_gateway_started(self, character_name: str, port: int):
    settings.openclaw_url = f"ws://127.0.0.1:{port}"
    if self._openclaw:
        self._openclaw.stop_connection()
        self._openclaw.update_url(settings.openclaw_url)
        self._openclaw.start_connection()
```

---

## 5. 模块三：Chat UI 重构

### 5.1 MainPanel (多导航面板)

复用 `FluentWindow` 框架，替代原 `ControlMainWindow`，仅保留 Chat 和 Settings 两个导航页：

```python
class MainPanel(FluentWindow):
    """主面板，包含 Chat 和 Settings 两个导航页。"""

    def __init__(self, minWidth=800, minHeight=800):
        super().__init__()
        self.chatInterface = ChatInterface(sizeHintDyber=(minWidth, minHeight), parent=self)
        self.settingInterface = SettingInterface(self)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.chatInterface, FIF.CHAT, self.tr('Chat'))
        self.addSubInterface(self.settingInterface, FIF.SETTING, self.tr('Settings'))

    def show_chat(self):
        self.show()
        self.stackedWidget.setCurrentWidget(self.chatInterface)
```

### 5.2 ChatInterface 布局（上→下：消息 + 输入 + 角色管理）

Chat 页面采用上下三层布局：

```
┌──────────────────────────────────────────────────────────┐
│  Chat with Kitty                       [新对话] [重连]  │  ← 标题栏
├──────────────────────────────────────────────────────────┤
│           ○ 2026-03-19 10:30                                │
│                                                            │
│  ┌──────┐ ┌────────────────────────────────┐                │
│  │avatar│ │ **AI 回复**                      │ 10:30          │
│  └──────┘ │ ```python                     │                │
│           │ print("hello")                │                │
│           │ ```                            │                │
│           │ ![image](data:image/png;...)  │                │
│           └────────────────────────────────┘                │
│                                                            │
│           ┌────────────────────────────────┐ ┌──────┐    │
│    10:31  │ 用户消息                        │ │avatar│    │
│           └────────────────────────────────┘ └──────┘    │
│                                                            │
├──────────────────────────────────────────────────────────┤
│  [  输入消息...                                ] [发送]    │  ← 输入栏
├──────────────────────────────────────────────────────────┤
│  [角色: Kitty ▼]  :18789  ● 运行中  [⚙]               │  ← 角色-GW 管理
└──────────────────────────────────────────────────────────┘
```

### 5.3 Markdown 渲染

**方案**：`QTextBrowser` + `markdown` Python 库

```
消息文本 → markdown.markdown(text, extensions) → HTML → QTextBrowser.setHtml()
```

extensions：`['fenced_code', 'tables', 'nl2br']`

**MarkdownBubbleWidget**：

```python
class MarkdownBubbleWidget(QTextBrowser):
    """Markdown 渲染气泡，替代原 BodyLabel。"""

    STYLESHEET = """
    body { font-family: -apple-system, 'PingFang SC', sans-serif; font-size: 14px; }
    code { background: #f0f0f0; padding: 2px 6px; border-radius: 4px; font-family: 'SF Mono', Consolas, monospace; }
    pre { background: #1e1e1e; color: #d4d4d4; padding: 12px; border-radius: 8px; }
    pre code { background: transparent; color: inherit; padding: 0; }
    blockquote { border-left: 3px solid #4A90D9; padding-left: 12px; color: #666; }
    img { max-width: 100%; border-radius: 8px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 6px 10px; }
    """

    def set_markdown(self, text: str):
        html = markdown.markdown(text, extensions=['fenced_code', 'tables', 'nl2br'])
        self.setHtml(f"<style>{self.STYLESHEET}</style>{html}")
        self._adjust_height()
```

**图片支持**：
- Markdown 中的 `![alt](url)` 自动渲染为 `<img>` 标签
- `QTextBrowser` 原生支持 `<img src="...">` 标签
- 支持 base64 内联图片：`<img src="data:image/png;base64,...">`
- 支持本地文件路径：`<img src="file:///path/to/image.png">`

**流式渲染优化**：
- 每次 `stream_delta` 拼接到 `_streaming_buffer`
- 100ms 节流 `QTimer`，避免频繁 `setHtml()`
- 流式结束后做一次最终渲染

### 5.4 历史消息

**存储格式** (`data/chat_history/<角色名>.json`)：

```json
{
  "messages": [
    {
      "id": "uuid",
      "sender": "user",
      "content": "你好",
      "timestamp": "2026-03-19T10:30:00"
    },
    {
      "id": "uuid2",
      "sender": "pet",
      "content": "# 你好！\n我是 AI 助手",
      "timestamp": "2026-03-19T10:30:02"
    }
  ]
}
```

**ChatHistoryManager**：

```python
class ChatHistoryManager:
    def save_message(self, character: str, message: ChatMessage): ...
    def load_history(self, character: str, limit: int = 50, offset: int = 0) -> list[ChatMessage]: ...
    def clear_history(self, character: str): ...
```

**加载流程**：
1. ChatWindow 打开/角色切换 → `load_history(character, limit=50)` → 渲染到列表
2. 上滑到顶 → `load_history(character, limit=50, offset=已加载数)` → 追加到列表顶部
3. 每次收发消息 → `save_message()` 追加

### 5.5 聊天工具栏

位于标题栏右侧：

| 按钮 | 功能 |
|------|------|
| 新对话 | 发送 `/new` 清空当前 session |
| 重连 | 手动触发 WS 重连 |

### 5.6 配色方案

| 元素 | Light |
|------|-------|
| 用户气泡 | `#007AFF` 白字 |
| AI 气泡 | `#F2F2F7` 黑字 |
| 代码块 | `#1E1E1E` 浅字 |
| 发送按钮 | `#007AFF` |

---

## 6. 模块四：宠物右键菜单重构

### 6.1 重构前菜单

```
StatMenu (RoundMenu)
├── [statusTitle]           ← 删除（HP/FV 状态栏）
├── ─────────────
├── Dashboard               ← 删除
├── System                  ← 删除
├── Chat                    ✅ 保留
├── ─────────────
├── ▶ 选择动作 (act_menu)    ← 删除
├── ▶ 召唤伙伴 (companion)   ← 删除
├── ▶ 更换角色 (change_menu) ← 删除
├── ─────────────
└── Exit                    ✅ 保留
```

### 6.2 重构后菜单

```
StatMenu (RoundMenu)
├── Chat        → 打开 MainPanel 并切换到 Chat 页面
├── OpenClaw    → 打开浏览器访问当前端口的 WebUI
├── ───────────
└── Exit        → 退出应用
```

### 6.3 实现

```python
def _set_Statusmenu(self):
    self.StatMenu = RoundMenu(parent=self)

    self.StatMenu.addActions([
        Action(FIF.CHAT, self.tr('Chat'), triggered=self._show_chat),
        Action(QIcon(os.path.join(basedir, "res/icons/openclaw.svg")),
               self.tr('OpenClaw'), triggered=self._open_openclaw_webui),
    ])
    self.StatMenu.addSeparator()
    self.StatMenu.addActions([
        Action(FIF.POWER_BUTTON, self.tr('Exit'), triggered=self.quit),
    ])

def _show_chat(self):
    self.show_chat.emit()

def _open_openclaw_webui(self):
    port = settings.openclaw_port_dict.get(
        settings.petname, 18789
    )
    QDesktopServices.openUrl(QUrl(f"http://127.0.0.1:{port}"))
```

### 6.4 删除的菜单相关代码

| 删除项 | 文件位置 |
|-------|---------|
| `_set_menu()` 中的 `act_menu`、`companion_menu`、`change_menu` | `pet_widget.py` |
| `_update_fvlock()`、`_update_actlist()` | `pet_widget.py` |
| `_add_pet()`（召唤伙伴） | `pet_widget.py` |
| `statusTitle` 及相关 HP/FV 进度条 | `pet_widget.py` |

### 6.5 _init_ui() 简化

删除 `_init_ui()` 中不再需要的 UI 组件：

```python
# 删除 - HP 进度条
# 删除 - FV 进度条
# 删除 - HP 图标
# 删除 - 等级徽章
# 删除 - 番茄钟进度条和图标
# 删除 - 专注时间进度条和图标

# 保留 - 角色 QLabel (self.label)
```

---

## 7. 数据模型设计

### 7.1 ChatMessage

```python
@dataclass
class ChatMessage:
    id: str                          # UUID
    sender: str                      # "user" | "pet"
    content: str                     # Markdown 文本
    timestamp: datetime
    message_type: str = "text"       # "text" | "system" | "error"
    is_streaming: bool = False
```

### 7.2 Settings 变更

**新增**：

```python
openclaw_port_dict = {}              # {"Kitty": 18789, "ChrisKitty": 18790}
openclaw_gateway_auto_start = True   # 启动时自动启动当前角色的 Gateway
```

**保留**：

```python
openclaw_enabled = False
openclaw_url = "ws://127.0.0.1:18789"
openclaw_token = ""
openclaw_auto_reconnect = True
```

**删除**（可选）：

```python
# HP/FV 相关常量 - 可保留不影响运行，但建议清理
# HP_TIERS, TIER_NAMES, HP_INTERVAL, LVL_BAR
# SINGLETASK_REWARD, FIVETASK_REWARD
# HUNGERSTR, FAVORSTR
```

---

## 8. 技术选型分析

### 8.1 Markdown 渲染

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| `QTextBrowser` + `markdown` lib | 无额外 UI 依赖，原生 PySide6 | HTML 子集限制 | ✅ 推荐 |
| `QWebEngineView` | 完美 CSS/JS | 太重，内存大 | ❌ 过重 |

### 8.2 历史消息

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| JSON 文件 | 简单，与项目模式一致 | 大量消息时慢 | ✅ 推荐 |
| SQLite | 查询灵活 | 增加复杂度 | ❌ 过度 |

### 8.3 进程管理

| 方案 | 优点 | 缺点 | 结论 |
|------|------|------|------|
| `QProcess` | 与 Qt 事件循环集成，有信号通知 | 无 | ✅ 推荐 |
| `subprocess.Popen` | 简单 | 需自行管理异步 | ❌ |

### 8.4 新增依赖

| 包 | 版本 | 用途 |
|----|------|------|
| `markdown` | >=3.4 | Markdown → HTML 转换 |

---

## 9. 工作分解与实施计划

### Phase 1：功能裁剪 + Gateway 管理器

| # | 任务 | 涉及文件 | 验收标准 |
|---|------|---------|---------|
| 1.1 | 实现 `GatewayProcessManager` | `ClawPet/OpenClawClient/gateway_manager.py` (新建) | 可启动/停止 Gateway，信号正常 |
| 1.2 | 新增 `openclaw_port_dict` 到 settings | `ClawPet/settings.py` | 端口映射持久化 |
| 1.3 | 裁剪 PetWidget 信号和方法 | `ClawPet/pet_widget.py` | 删除 HP/FV/任务/Dashboard 相关代码 |
| 1.4 | 重构右键菜单为 Chat + OpenClaw + Exit | `ClawPet/pet_widget.py` | 菜单仅显示 3 项，OpenClaw 打开浏览器 |

### Phase 2：MainPanel 多导航面板 + Chat UI 重构

| # | 任务 | 涉及文件 | 验收标准 |
|---|------|---------|----------|
| 2.1 | 重构 `ControlMainWindow` 为 `MainPanel` | `ClawPet/DyberSettings/control_panel.py` (重构) | FluentWindow 仅含 Chat + Settings 导航 |
| 2.2 | 实现角色-Gateway 管理区（Chat 页面底部） | `ClawPet/DyberSettings/chat_ui.py` | 角色下拉、端口、状态灯、设置按钮 |
| 2.3 | 实现 `MarkdownBubbleWidget` | `ClawPet/DyberSettings/chat_ui.py` | Markdown 正确渲染 |
| 2.4 | 实现 `ChatHistoryManager` | `ClawPet/OpenClawClient/chat_history.py` (新建) | 历史消息读写正常 |
| 2.5 | 重构 `ChatCardGroup` 使用 Markdown 气泡 | `ClawPet/DyberSettings/chat_ui.py` | 流式 Markdown、图片展示 |
| 2.6 | 实现历史消息加载（打开时 + 上滑） | `ClawPet/DyberSettings/chat_ui.py` | 打开加载历史，上滑加载更多 |

### Phase 3：集成与清理

| # | 任务 | 涉及文件 | 验收标准 |
|---|------|---------|---------|
| 3.1 | 重构 `run_ClawPet.py` 信号连接 | `run_ClawPet.py` | 使用 MainPanel 替代 ControlMainWindow |
| 3.2 | 角色切换触发 Gateway 切换 + WS 重连 | `pet_widget.py` + `chat_ui.py` | 切换角色后 Chat 自动连接新端口 |
| 3.3 | 应用启动时自动启动当前角色 Gateway | `run_ClawPet.py` | 启动后 Gateway 自动运行 |
| 3.4 | 应用退出时清理 Gateway 进程 | `pet_widget.py` | 退出时 Gateway 进程被终止 |
| 3.5 | 删除不再使用的文件引用 | 各文件 | 无 import 错误，程序正常运行 |

### 里程碑

| Phase | 交付 | 依赖 |
|-------|------|------|
| Phase 1 | Gateway 管理器 + 菜单重构 + 代码裁剪 | 无 |
| Phase 2 | MainPanel（Chat 导航 + Settings 导航 + Markdown + 历史 + Gateway 管理） | Phase 1 |
| Phase 3 | 全部集成，应用可正常运行 | Phase 1 + 2 |

---

## 10. 风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| `openclaw` CLI 未安装 | Gateway 无法启动 | 检测 CLI 可用性，不可用时提示用户安装 |
| Gateway 端口冲突 | 启动失败 | 启动前检测端口占用，冲突时提示用户换端口 |
| Gateway 进程崩溃 | Chat 断联 | 监听 `QProcess.finished`，显示错误状态 |
| Markdown HTML 注入 | 安全风险 | `markdown` 库默认转义 HTML |
| 大量历史消息 | 加载慢 | 分页加载（每次 50 条），上滑加载更多 |
| 删除功能后残留引用 | import 报错 | 全文搜索清理所有引用 |
| 流式渲染性能 | UI 卡顿 | 100ms 节流 + 最终渲染 |

---

## 11. 交付物清单

### 新增文件

| 文件 | 用途 |
|------|------|
| `ClawPet/OpenClawClient/gateway_manager.py` | Gateway 进程管理器 |
| `ClawPet/OpenClawClient/chat_history.py` | 聊天历史持久化 |

### 修改文件

| 文件 | 变更 |
|------|------|
| `ClawPet/pet_widget.py` | 裁剪信号/方法，重构右键菜单为 Chat + OpenClaw + Exit |
| `ClawPet/settings.py` | 新增 `openclaw_port_dict`，可选移除 HP/FV 常量 |
| `ClawPet/DyberSettings/control_panel.py` | 重构为 `MainPanel(FluentWindow)`，仅含 Chat + Settings 导航 |
| `ClawPet/DyberSettings/chat_ui.py` | Markdown 气泡、图片支持、流式优化、角色-Gateway 管理区 |
| `run_ClawPet.py` | 用 MainPanel 替代 ControlMainWindow，新信号连接 |
| `ClawPet/OpenClawClient/__init__.py` | 导出 GatewayProcessManager |

### 不再使用的文件（可保留但不引入）

| 文件 | 原功能 |
|------|--------|
| `ClawPet/DyberSettings/game_save_ui.py` | 游戏存档 |
| `ClawPet/DyberSettings/char_card_ui.py` | 角色卡片管理（角色管理移入 Chat 页面） |
| `ClawPet/Dashboard/status_ui.py` | 角色状态 |
| `ClawPet/Dashboard/task_ui.py` | 日常任务 |
| `ClawPet/Dashboard/dashboard_widgets.py` | Dashboard 组件 |

---

## 附录 A：OpenClaw CLI 参考

**Gateway 启动**：
```bash
openclaw --profile <name> gateway --port <port> --token <token>
```

**状态隔离**：`--profile <name>` → 状态目录 `~/.openclaw-<name>/`

**WebUI 地址**：`http://127.0.0.1:<port>`（Gateway 同端口多路复用 HTTP + WS）

**Gateway 状态查询**：
```bash
openclaw --profile <name> gateway status --json
openclaw --profile <name> gateway health --url ws://127.0.0.1:<port>
```
