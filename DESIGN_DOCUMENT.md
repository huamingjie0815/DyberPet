# DyberPet 完整程序设计说明

## 1. 项目概述

### 1.1 项目介绍
- **名称**: 呆啵宠物 (DyberPet)
- **版本**: v0.7.7
- **定义**: 基于 PySide6 的桌面宠物开发框架
- **目标**: 为开发者提供创造桌面宠物的底层软件框架
- **开发阶段**: 进行中（LLM 模块暂未开源）
- **编程语言**: Python 3.9+
- **主要依赖**: PySide6, PySide6-Fluent-Widgets, APScheduler

### 1.2 核心特性
- ☑ 多宠物支持（Kitty, ChrisKitty, 派蒙等）
- ☑ 养成系统（HP/Satiety、FV/Favorability）
- ☑ 任务系统（Daily Tasks、Weekly Tasks）
- ☑ 物品系统（消耗品、收集品、配件）
- ☑ Buff系统（临时增益效果）
- ☑ 动画系统（随机动作、交互反应）
- ☑ 仪表板管理（Dashboard）
- ☑ 设置系统（DyberSettings）
- ☑ 气泡消息系统（BubbleManager）
- ☑ 配件系统（DPAccessory）

---

## 2. 整体架构设计

### 2.1 应用架构层级
```
┌─────────────────────────────────────────────────────────┐
│              Application Entry (run_DyberPet.py)        │
│                    DyberPetApp (QApplication)           │
└────────────┬────────────────────────────────────────────┘
             │
    ┌────────┴─────────┬──────────────────┐
    │                  │                  │
    v                  v                  v
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│ PetWidget   │  │ Dashboard    │  │ Settings     │
│ (Main Pet)  │  │ Panels       │  │ Control Panel│
└─────────────┘  └──────────────┘  └──────────────┘
    │                  │                  │
    │ Signal Slots     │ Signal Slots     │ Signal Slots
    │                  │                  │
    v                  v                  v
┌──────────────────────────────────────────────────────────┐
│        Core Module Layer (modules.py)                    │
│  ┌──────────────┐  ┌──────────┐  ┌─────────────────┐   │
│  │ Animation    │  │ Buff     │  │ Bubble          │   │
│  │ worker       │  │ Thread   │  │ Manager         │   │
│  └──────────────┘  └──────────┘  └─────────────────┘   │
└──────────────────────────────────────────────────────────┘
    │       │       │
    v       v       v
┌──────────────────────────────────────────────────────────┐
│        Data Layer (conf.py + settings.py)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │Pet Config│  │Act Data  │  │Task Data │  │Item Data│ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└──────────────────────────────────────────────────────────┘
    │       │       │       │
    v       v       v       v
┌──────────────────────────────────────────────────────────┐
│        Persistence Layer (JSON files)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │pet_data.json │  │act_data.json │  │settings.json │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 2.2 模块化结构

```
DyberPet/
├── DyberPet.py              # 主宠物窗口 (PetWidget) - 核心UI
├── modules.py               # 核心模块 (Animation, Buff, Bubble处理)
├── conf.py                  # 配置系统 (PetConfig, ActData 等)
├── settings.py              # 设置系统 (全局设置, 宠物数据)
├── utils.py                 # 工具函数库
├── Accessory.py             # 宠物配件系统
├── bubbleManager.py         # 气泡消息管理
├── Notification.py          # 通知系统
├── custom_widgets.py        # 自定义QT组件
├── custom_roundmenu.py      # 自定义问卷菜单
├── Dashboard/               # 仪表板模块
│   ├── DashboardUI.py       # 仪表板主窗口
│   ├── statusUI.py          # 状态面板
│   ├── inventoryUI.py       # 背包面板
│   ├── shopUI.py            # 商店面板
│   ├── taskUI.py            # 任务面板
│   ├── animationUI.py       # 动画面板
│   ├── dashboard_widgets.py # 仪表板组件库
│   └── buffModule.py        # Buff处理模块
├── DyberSettings/           # 设置面板模块
│   ├── DyberControlPanel.py # 设置主窗口
│   ├── BasicSettingUI.py    # 基础设置
│   ├── GameSaveUI.py        # 游戏存档
│   ├── CharCardUI.py        # 角色卡片
│   ├── PetCardUI.py         # 宠物卡片
│   └── ...
├── HideDock/                # 隐藏停靠模块
└── SelfStartup/             # 自启动模块

res/                         # 资源文件
├── icons/
│   ├── Dashboard/           # 仪表板图标/样式
│   └── ...
├── pet/                     # 宠物资源
│   └── 派蒙/
│       ├── pet_conf.json    # 宠物配置
│       ├── act_conf.json    # 动作配置
│       ├── action/          # 动作帧图
│       └── info/
├── role/                    # 角色资源
│   ├── Kitty/
│   ├── ChrisKitty/
│   └── sys/
└── language/                # 多语言支持

data/                        # 数据文件
├── pet_data.json            # 宠物状态数据
├── act_data.json            # 动作数据
├── settings.json            # 用户设置
└── task_data.json           # 任务数据
```

### 2.3 关键技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **UI框架** | PySide6 | Qt Python绑定，官方维护 |
| **UI组件库** | PySide6-Fluent-Widgets | 微软Fluent Design风格组件 |
| **调度器** | APScheduler | 定时任务和事件调度 |
| **数据格式** | JSON | 配置和数据存储 |
| **输入处理** | pynput | 鼠标键盘事件监听 |
| **多线程** | QThread | 后台任务处理 |
| **信号机制** | Qt Signal/Slot | 组件间通信 |

---

## 3. 核心模块设计

### 3.1 Application Entry (run_DyberPet.py)

#### 3.1.1 DyberPetApp 类

```python
class DyberPetApp(QApplication)
```

**职责**:
- Qt应用程序初始化
- 多屏幕支持处理
- 日期变化信号检测
- 全局应用配置

**关键方法**:
- `__init__()`: 应用初始化，设置不在最后窗口关闭时退出
- `date_changed.emit()`: 每日切换时触发

**信号**:
- `date_changed`: QDate，每日凌晨触发

**特点**:
- 单例模式（使用tendo.singleton确保单一实例）
- 支持Windows/Mac/Linux跨平台
- DPI缩放处理

---

### 3.2 Main Pet Widget (DyberPet.py)

#### 3.2.1 DP_HpBar (HP进度条)

```python
class DP_HpBar(QProgressBar)
```

**职责**: 自定义HP显示进度条

**特性**:
- 圆角设计
- 自定义颜色 (#FAC486 - 金色背景)
- 实时更新显示
- 分级显示 (0, 50, 80, 100)

**信号**:
- `hptier_changed`: (int tier, str name) - HP等级变化
- `hp_updated`: (int value) - HP值更新

---

#### 3.2.2 PetWidget (主宠物窗口)

```python
class PetWidget(QWidget)
```

**职责**: 主宠物的图形界面和交互处理

**核心属性**:
```python
self.pet_conf: PetConfig          # 宠物配置
self.pic_dict: dict               # 宠物图片缓存
self.animation_worker: Animation_worker  # 动画工作线程
self.bubble_manager: BubbleManager # 气泡管理器
```

**关键特性**:

1. **物理引擎**
   - 重力模拟 (gravity = 0.41)
   - 速度衰减 (friction)
   - 碰撞检测 (屏幕边界)

2. **动画系统**
   - 逐帧图片显示
   - 随机动作触发
   - 优先级控制 (拖拽 > 互动 > 随机)

3. **交互系统**
   - 鼠标拖拽
   - 图片点击触发 (pat)
   - 右键菜单

4. **通知系统**
   - HP自动下降
   - FV变化
   - 任务提醒

**关键方法**:

```python
def setup_pet(pet_name: str)
    # 宠物初始化

def random_stand()
    # 随机移动到屏幕边角站立

def show_act(act_obj, duration)
    # 播放动作
    
def apply_act_effect(act_data)
    # 应用动作效果 (动作特殊效果)

def patpat()
    # 点击宠物响应

def mousePressEvent()
def mouseMoveEvent()
def mouseReleaseEvent()
    # 鼠标交互
```

**信号定义**:
```python
changePet: 宠物切换
addCoins: 增加硬币
task_over: 任务完成
level_up: 升级
state_change: 状态变化
```

---

### 3.3 Animation Module (modules.py)

#### 3.3.1 Animation_worker 类

```python
class Animation_worker(QObject)
```

**职责**: 管理宠物动画播放，根据宠物状态随机选择动作

**核心逻辑**:
1. 根据 HP 等级 (hp_tier) 和好感度等级 (fv_lvl) 计算当前状态
2. 按照配置的动作概率列表选择动作
3. 在独立线程中运行，定时触发随机动作

**关键属性**:
```python
self.pet_conf: PetConfig          # 宠物配置
self.current_status: [hp_tier, fv_lvl]  # 当前宠物状态
self.act_cmlt_prob: list          # 累积概率分布
self.nonDefault_prob: float       # 非默认动作概率
self.is_killed: bool              # 线程活动标志
self.is_paused: bool              # 暂停标志
```

**状态系统**:
- **HP 分级** (HP_TIERS):
  - 0: Starving (0-50)      - 饥饿：只能做hp_tier==0的动作
  - 1: Hungry (50-80)       - 饥饿：可做hp_tier≤1的动作
  - 2: Normal (80-100)      - 正常：可做hp_tier≤2的动作
  - 3: Energetic (100+)     - 饱足：可做所有动作

- **FV 等级** (fv_lvl): 0-200+，影响高级动作解锁

**概率计算算法**:
```
对每个动作：
  if 动作未解锁:
    新概率 = 0
  else if HP_tier==0 且 动作状态类型!=0:
    新概率 = 0
  else if fv_lvl < 动作所需fv_lvl:
    新概率 = 0
  else if 动作状态类型==0:
    新概率 = 原概率 * (当前hp_tier==0 ? 1 : 0)
  else:
    新概率 = 原概率 * (1/4)^|动作状态-当前状态| * (动作在播放列表 ? 1 : 0)

计算累积概率分布用于随机选择
```

**关键方法**:

```python
def run()
    # 线程主循环，每隔refresh秒触发一次
    
def random_act()
    # 随机选择一个动作
    
def _cal_prob(current_status) -> list
    # 计算当前状态下的动作概率分布
    
def hpchange(hp_tier, direction)
    # HP等级变化时更新概率
    
def fvchange(fv_lvl)
    # FV等级变化时更新概率
    
def pause() / resume() / kill()
    # 线程控制
```

**信号定义**:
```python
sig_setimg_anim: 设置动画图片
sig_move_anim(float, float): 移动宠物
sig_repaint_anim: 重绘宠物
acc_regist(dict): 注册配件
```

---

#### 3.3.2 BuffAdd 和 BuffAlt 类

**BuffAdd** - 增加型Buff:
```python
class BuffAdd(QObject)
```

**职责**: 管理增益效果（如+HP、+FV、+Gold）

**机制**:
- 每隔 `interval` 秒触发一次效果
- 持续 `expiration` 秒（如果指定）
- 可以堆叠（多个相同buff可以同时存在）
- 支持多层计数

**效果类型**:
- `hp`: 增/减 HP
- `fv`: 增/减 FV (Favorability)
- `coin`: 增/减硬币

**BuffAlt** - 状态型Buff:
```python
class BuffAlt(QObject)
```

**职责**: 管理状态效果（如停止HP下降）

**效果类型**:
- `HP_stop`: 停止HP自动下降
- `FV_stop`: 停止FV自动上升

---

### 3.4 Configuration System (conf.py)

#### 3.4.1 PetConfig 类

```python
class PetConfig
```

**职责**: 管理单个宠物的配置信息

**核心属性**:
```python
# 基本信息
petname: str                  # 宠物名称
width: float                  # 宽度 (像素)
height: float                 # 高度 (像素)
scale: float                  # 缩放因子

# 动画配置
refresh: int                  # 刷新间隔 (秒)
interact_speed: float         # 交互响应速度 (毫秒)
dropspeed: float              # 掉落速度

# 动作配置
default: Act                  # 默认动作
up/down/left/right: Act       # 移动方向动作
drag: Act                     # 拖拽动作
fall/prefall: Act             # 掉落动作
on_floor: Act                 # 着地动作
patpat: dict[int, Act]        # 敲击动作 (按HP分级)
focus: Act                    # 焦点动作

# 动作列表
act_dict: dict[str, Act]      # 所有动作字典
random_act: list              # 随机动作组合
act_prob: list                # 动作概率
act_name: list                # 动作名称
act_type: list                # 动作类型 [hp_tier, fv_lvl]

# 配件系统
accessory_act: dict           # 配件动作
acc_name: list                # 配件名称
custom_act: dict              # 自定义动作

# 物品偏好
item_favorite: list           # 喜欢的物品
item_dislike: list            # 不喜欢的物品
```

**配置文件结构** (pet_conf.json):
```json
{
  "width": 112,
  "height": 128,
  "scale": 1.0,
  "interact_speed": 0.02,
  
  "default": "default",
  "up": "default",
  "down": "default",
  "left": "default",
  "right": "default",
  "drag": "drag_action",
  "fall": "fall_action",
  "on_floor": "default",
  "patpat": "patpat_action",
  
  "random_act": [
    {
      "name": "default",
      "act_list": ["default"],
      "act_prob": 1.0,
      "act_type": [0, 10000]  // [hp_tier, fv_lvl]
    }
  ],
  
  "main_interact": {}
}
```

**初始化方法**:
```python
@classmethod
def init_config(cls, pet_name: str, pic_dict: dict) -> PetConfig
    # 从JSON配置文件加载宠物配置
    # 初始化所有动作对象
```

---

#### 3.4.2 Act 类

```python
class Act
```

**职责**: 表示单项动作的完整信息

**属性**:
```python
name: str                     # 动作名称
act_frames: list              # 动作帧列表 [QPixmap, ...]
frame_interval: int           # 帧间隔 (毫秒)
loop: int                     # 循环次数 (-1表示无限)
sound: str                    # 动作声音
scale: float                  # 缩放系数
status_type: [int, int]       # [hp_tier_min, fv_lvl_min]
unlocked: bool                # 是否解锁
in_playlist: bool             # 是否在随机播放列表中
```

**配置文件结构** (act_conf.json):
```json
{
  "default": {
    "loop": -1,
    "frame_interval": 100,
    "status_type": [0, 0],
    "act_prob": 1.0,
    "unlocked": true,
    "in_playlist": true,
    "sound": null
  },
  "action_name": {
    "loop": 2,
    "frame_interval": 50,
    "status_type": [1, 50],
    "act_prob": 0.5,
    "unlocked": false,
    "in_playlist": false,
    "sound": "system"
  }
}
```

---

#### 3.4.3 PetData 类

```python
class PetData
```

**职责**: 管理宠物的游戏数据（状态数据）

**关键属性**:
```python
# 生命值系统
HP: int                       # 当前HP值 (0-200)
HP_tier: int                  # HP等级 (0-3)

# 好感度系统
FV: int                       # 当前好感度值
FV_lvl: int                   # 好感度等级 (0-200+)

# 物品和货币
items: dict[str, int]         # 物品库存 {item_id: quantity}
coins: int                    # 硬币数量

# 游玩信息
days: int                     # 累计游玩天数
last_opened: str              # 最后打开时间 (YYYY-m-d)
fv_sys_ver: str               # 好感度系统版本

# 时间跟踪
last_hp_decrease: datetime    # 最后HP下降时间
last_fv_increase: datetime    # 最后FV增加时间
```

**数据文件结构** (pet_data.json):
```json
{
  "Kitty": {
    "HP": 199,
    "HP_tier": 3,
    "FV": 1,
    "FV_lvl": 0,
    "fv_sys_ver": "v2",
    "items": {
      "item_id_1": 5,
      "item_id_2": 3
    },
    "coins": 0,
    "days": 1,
    "last_opened": "2026-3-17"
  }
}
```

---

#### 3.4.4 ActData 类

```python
class ActData
```

**职责**: 管理所有动作的全局数据和状态

**属性**:
```python
allAct_params: dict          # 所有动作参数 {pet_name: {act_name: params}}
allAct_unlocked: dict        # 动作解锁状态
animation_file: str          # 当前动画制作配置
```

**关键方法**:
```python
def _pet_refreshed(fv_lvl)
    # 宠物升级时更新动作解锁状态
```

**数据文件结构** (act_data.json):
```json
{
  "Kitty": {
    "default": {
      "unlocked": true,
      "in_playlist": true,
      "act_prob": 1.0,
      "status_type": [0, 0]
    }
  }
}
```

---

#### 3.4.5 TaskData 类

```python
class TaskData
```

**职责**: 管理任务系统数据

**属性**:
```python
focus_tasks: list            # 当前专注任务
progress_tasks: list         # 进行中的任务
task_pool: dict              # 所有可用任务
completed_today: dict        # 今日完成的任务
```

---

#### 3.4.6 ItemData 类

```python
class ItemData
```

**职责**: 管理物品系统数据

**属性**:
```python
all_items: dict              # 所有物品定义
item_categories: dict        # 物品分类
item_effects: dict           # 物品效果定义
```

---

### 3.5 Settings System (settings.py)

#### 3.5.1 全局设置常量

```python
# 路径配置
BASEDIR: str                  # 基础目录路径
CONFIGDIR: str                # 配置文件目录

# 版本信息
VERSION: str = "v0.6.7"       # 程序版本

# HP系统配置
HP_TIERS: list = [0, 50, 80, 100]      # HP分级阈值
TIER_NAMES: list = ['Starving', 'Hungry', 'Normal', 'Energetic']
HP_INTERVAL: int = 2          # HP下降间隔 (秒)

# FV系统配置
PP_HEART: float = 0.8         # 取心形物品概率
PP_COIN: float = 0.9          # 取硬币概率
COIN_MU: int = 10             # 硬币均值
COIN_SIGMA: int = 5           # 硬币标准差

# 物品配置
PP_ITEM: float = 0.95         # 掉落物品概率
PP_AUDIO: float = 0.8         # 播放音频概率
PP_BUBBLE: float = 0.15       # 气泡出现概率
ITEM_DEPRECIATION: float = 0.75  # 物品出售贬值

# 任务奖励
SINGLETASK_REWARD: int = 200  # 单任务奖励
FIVETASK_REWARD: int = 1500   # 五任务奖励

# 等级系统
LVL_BAR: list                 # 升级所需经验值列表

# UI文本常量
HUNGERSTR: str = "Satiety"
FAVORSTR: str = "Favorability"
```

#### 3.5.2 全局数据变量

```python
# 当前宠物信息
petname: str                  # 当前宠物名称
pet_data: PetData             # 当前宠物数据
act_data: ActData             # 动作数据
task_data: TaskData           # 任务数据
items_data: ItemData          # 物品数据

# 用户设置
settings_data: dict           # 用户设置配置

# 控制标志
HP_stop: bool = False         # 停止HP下降标志
FV_stop: bool = False         # 停止FV增加标志
usertag_dict: dict            # 用户标签字典

# 缩放配置
scale_dict: dict              # 宠物缩放因子
minipet_scale: dict           # 小宠物缩放

# 主题配置
DEFAULT_THEME_COL: str = "#009faa"
themeColor: str               # 当前主题颜色
language_code: str = "zh_CN"  # 当前语言
```

#### 3.5.3 初始化函数

```python
def init()
    # 初始化所有全局数据
    # 加载配置文件
    # 初始化PetData, ActData等
```

---

### 3.6 Bubble Manager (bubbleManager.py)

#### 3.6.1 BubbleManager 类

```python
class BubbleManager(QObject)
```

**职责**: 管理宠物气泡消息的显示

**气泡行为分类**:

1. **好感度相关**
   - `fv_lvlup`: 好感度升级
   - `fv_drop`: 好感度下降

2. **HP相关**
   - `hp_low`: HP过低
   - `hp_zero`: HP耗尽（饥饿）

3. **喂食相关**
   - `feed_done`: 喂食完成
   - `feed_required`: 需要喂食 (仅正常/低HP状态)

4. **互动相关**
   - `pat_focus`: 集中点击 (焦点状态)
   - `pat_frequent`: 频繁点击
   - `pat_random_[0-9]*`: 随机点击反应 (可自定义)

**配置文件结构** (bubble_conf.json):
```json
{
  "hp_low": {
    "icon": "system",
    "message": "I'm hungry...",
    "countdown": null,
    "start_audio": "system",
    "end_audio": null
  },
  "pat_focus": {
    "icon": "favorite_character",
    "message": "Hehe~ ♡",
    "countdown": 300,
    "start_audio": null,
    "end_audio": null
  }
}
```

**关键属性**:
```python
bubble_conf: dict            # 气泡配置
bubble_hp_tier: dict         # 按HP等级的可用气泡类型
attr_list: list              # 气泡属性名列表
```

**关键方法**:
```python
def load_bubble_config() -> dict
    # 加载系统和宠物配置
    
def trigger_bubble(bb_type: str)
    # 触发指定类型的气泡
    
def _format_bubble_type_conf(conf: dict) -> dict
    # 格式化气泡配置
```

**信号**:
- `register_bubble(dict)`: 注册新气泡显示

---

### 3.7 Accessory System (Accessory.py)

#### 3.7.1 DPAccessory 类

```python
class DPAccessory(QWidget)
```

**职责**: 管理宠物的配件（心形、物品掉落等）

**配件类型**:

1. **物品掉落** (QItemDrop)
   - 掉落图片和物品
   - 自动消失或被点击收集
   - 显示掉落轨迹

2. **子宠物** (SubPet)
   - 可生成的独立小宠物
   - 跟随主宠物
   - 独立动画

3. **心形特效** (Heart)
   - 爱心特效
   - 漂浮上升

**关键属性**:
```python
acc_dict: dict[uuid, Accessory]  # 所有活动配件
heart_list: list                 # 心形特效列表
subpet_dict: dict                # 子宠物字典
follow_main_list: list           # 跟随主宠物的配件列表
```

**关键方法**:
```python
def setup_accessory(acc_act: dict, pos_x: int, pos_y: int)
    # 创建新配件
    
def remove_accessory(acc_id: str)
    # 移除配件
    
def add_heart()
    # 添加心形特效
```

**信号**:
- `send_main_movement`: 主宠物运动信息
- `ontop_changed`: 窗口顶层状态变化
- `reset_size_sig`: 重置大小
- `acc_withdrawed(str)`: 配件移除

---

### 3.8 Module Connection: Buff System

**BuffThread** - Buff线程管理器

```python
class BuffThread(QObject)
```

**职责**: 在后台线程中管理所有Buff的更新

**工作流程**:
```
定时器 (每秒)
    ↓
轮询所有Buff对象
    ↓
更新Buff计时器
    ↓
Buff触发效果 / 计时器过期
    ↓
发送Signal到主线程
    ↓
更新UI和游戏数据
```

**关键方法**:
```python
def add_buff(buff_obj: BuffAdd/BuffAlt) -> str
    # 添加Buff，返回Buff ID
    
def remove_buff(buff_id: str, layer_idx: int)
    # 移除特定Buff
    
def update()
    # 更新所有Buff
```

---

## 4. UI/UX 设计

### 4.1 Dashboard 系统架构

#### 4.1.1 DashboardMainWindow

```python
class DashboardMainWindow(FluentWindow)
```

**架构**:
```
FluentWindow (Fluent Design主窗口)
├── NavigationInterface (左侧导航栏)
│   ├── Status Tab
│   ├── Backpack Tab
│   ├── Shop Tab
│   ├── Daily Tasks Tab
│   └── Animation Tab
└── 内容区域
    └── 各Tab的Content Widget
```

**页面构成**:

| 页面 | 类名 | 功能 |
|------|------|------|
| 状态 | statusInterface | 显示宠物属性、Buff、日志 |
| 背包 | backpackInterface | 物品管理、使用、掉落 |
| 商店 | shopInterface | 物品买卖、收集品展示 |
| 任务 | taskInterface | 日常任务、周任务管理 |
| 动画 | animationInterface | 动作编辑、预览 |

**信号连接网络**:
```
statusInterface
├─> addBuff ──────> backpackInterface._addBuff
├─> rmBuffInThread → 触发Buff移除
└─> addCoins ──────→ UI更新

backpackInterface
├─> addBuff ───────> statusInterface._addBuff
├─> rmBuff ──────────> statusInterface._rmBuff
├─> coinUpdated ────> shopInterface.coinWidget._update2data
├─> item_num_changed → shopInterface._updateItemNum
└─> use_item_inven ──> 触发物品效果

shopInterface
├─> buyItem ───────→ backpackInterface.add_item
├─> sellItem ──────→ backpackInterface.add_item
└─> updateCoin ────→ backpackInterface.addCoins

taskInterface
├─> focusPanel.addCoins ──────> backpackInterface.addCoins
├─> progressPanel.addCoins ───> backpackInterface.addCoins
└─> taskPanel.addCoins ──────> backpackInterface.addCoins
```

**关键方法**:
```python
def initNavigation()
    # 初始化导航栏
    
def __connectSignalToSlot()
    # 连接所有信号槽关系
    
def show_window()
    # 显示Dashboard窗口
```

---

#### 4.1.2 statusInterface (状态面板)

```python
class statusInterface(ScrollArea)
```

**UI Layout**:
```
┌─────────────────────────────────────────────┐
│ Status | Help  [充足空间]  User Name | Input│  (Header)
├─────────────────────────────────────────────┤
│                                             │
│  StatusCard                                 │
│  ┌─────────────────────────────────────┐   │
│  │ Pet Avatar │ Name │ Level │ Badges  │   │
│  │ HP Bar     │ FV Bar │ Exp Bar     │   │
│  │ Stat Values: HP, FV, Coins, Days   │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  BuffCard                                   │
│  ┌─────────────────────────────────────┐   │
│  │ Active Buffs Display (Scrollable)   │   │
│  │ [Buff1] [Buff2] [Buff3] ...         │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Status Log (仪表板外)                     │  
│  ┌─────────────────────────────────────┐   │
│  │ Recent Events & Notifications       │   │
│  │ • HP decreased to 150               │   │
│  │ • Item consumed: Apple              │   │
│  │ • FV increased by 2                │   │
│  └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

**关键组件**:

1. **StatusCard** - 宠物属性卡片
   - 宠物头像
   - 等级徽章
   - HP进度条 (DP_HpBar)
   - FV进度条
   - 经验进度条
   - 属性值显示

2. **BuffCard** - Buff显示卡片
   - 活跃Buff列表
   - 各个Buff的剩余时间
   - 移除按钮

3. **NoteFlowGroup** - 日志流
   - 时间戳
   - 事件类型图标
   - 事件描述

---

#### 4.1.3 backpackInterface (背包面板)

```python
class backpackInterface(ScrollArea)
```

**UI Layout**:
```
┌────────────────────────────────────────────┐
│ Backpack │Help  [空间]  Coins: 12345 Gold  │ (Header)
├────────────────────────────────────────────┤
│ [Food] [Collection] [Pets] ────────  [USE] │ (Tabs)
├────────────────────────────────────────────┤
│                                            │
│  itemTabWidget (Stacked)                  │
│                                            │
│  Tab1: Food (Consumables)                 │
│  ┌──────────┬──────────┬──────────┐       │
│  │Item1     │Item2     │Item3     │       │
│  │Qty: 5    │Qty: 0    │Qty: 2    │       │
│  │★★★       │─         │★★        │       │
│  │+5HP, FV  │          │          │       │
│  └──────────┴──────────┴──────────┘       │
│                                            │
│  Tab2: Collections                        │
│  ┌──────────┬──────────┬──────────┐       │
│  │Rare1     │Rare2     │Rare3     │       │
│  │Obtained  │Missing   │×5 Owned  │       │
│  │Info...   │          │Info...   │       │
│  └──────────┴──────────┴──────────┘       │
│                                            │
└────────────────────────────────────────────┘
```

**关键组件**:

1. **SegmentedToggleToolWidget** - 标签切换
   - 消耗品
   - 收集品
   - 子宠物

2. **itemTabWidget** - 物品网格
   - 物品卡片Grid布局
   - 点击选择
   - 信息显示

3. **coinWidget** - 硬币显示
   - 实时硬币数更新
   - 图标 + 数字

---

#### 4.1.4 shopInterface (商店面板)

```python
class shopInterface(ScrollArea)
```

**功能**:
- 浏览可购物品
- 购买物品
- 出售物品
- 物品收集统计

---

#### 4.1.5 taskInterface (任务面板)

```python
class taskInterface(ScrollArea)
```

**子面板**:
1. **focusPanel** - 专注任务
   - 今日重点任务
   - 进度追踪

2. **progressPanel** - 进行中的任务
   - 通用任务列表
   - 进度条

3. **taskPanel** - 完成任务
   - 勾选完成
   - 领取奖励

---

#### 4.1.6 animationInterface (动画面板)

```python
class animationInterface(ScrollArea)
```

**功能**:
- 动作播放和编辑
- 演出设计

---

### 4.2 Custom Widgets 库

#### 4.2.1 RoundBarBase

```python
class RoundBarBase(QWidget)
```

**用途**: 圆形进度条（用于HP、FV多层显示等）

---

#### 4.2.2 LevelBadge

```python
class LevelBadge(QWidget)
```

**用途**: 等级徽章显示

---

#### 4.2.3 RoundMenu

```python
class RoundMenu(QMenu)
```

**用途**: 圆角菜单，美化右键菜单

---

### 4.3 设置界面 (DyberSettings)

#### 4.3.1 DyberControlPanel

```python
class DyberControlPanel(FluentWindow)
```

**页面**:
- BasicSettingUI - 基础设置
- CharCardUI - 角色卡片
- PetCardUI - 宠物卡片
- ItemCardUI - 物品卡片
- GameSaveUI - 游戏保存

---

## 5. 数据流与交互设计

### 5.1 宠物初始化流程

```
run_DyberPet.py
    ↓
DyberPetApp.__init__()
    ├─> qApp.setQuitOnLastWindowClosed(False)
    ├─> 初始化屏幕配置
    └─> 保存版本号
    ↓
DyberPetApp.main()
    ├─> settings.init()  # 加载全局设置
    ├─> 加载当前宠物: settings.petname
    ├─> 创建 PetWidget(petname)
    │   ├─> PetConfig.init_config()
    │   ├─> 加载宠物图片
    │   ├─> Animation_worker创建
    │   ├─> BubbleManager创建
    │   ├─> 启动动画线程
    │   └─> 显示宠物窗口
    ├─> 创建 SystemTray (系统托盘)
    ├─> 创建 DashboardMainWindow (仪表板)
    └─> 创建 DyberControlPanel (设置)
```

### 5.2 游玩循环

```
Main Loop (100ms 刷新一次)
    ↓
┌─────────────────────────────────────┐
│  1. 检查时间 (HP自动下降)          │
│     if (当前时间 - 最后下降时间 >= interval)
│         HP -= 1
│         更新 HP_tier
│         触发 hptier_changed 信号
│                                    │
│  2. 检查Buff (BuffThread)          │
│     update() - 定时器递减
│     if buff过期: 移除并发送Signal   │
│                                    │
│  3. 处理物理 (重力、碰撞)          │
│     位置 += 速度
│     速度 += 重力加速度
│     if 边界碰撞: 反弹/停止          │
│                                    │
│  4. 动画更新 (Animation_worker)     │
│     if 随机动作触发:                │
│         选择动作并播放
│     else if 有交互命令:             │
│         优先播放交互动作
│     else:                          │
│         播放default动作            │
│                                    │
│  5. 重绘宠物                       │
│     paintEvent() - 绘制当前帧      │
│                                    │
└─────────────────────────────────────┘
```

### 5.3 物品使用流程

```
User: 点击背包中的物品 → 选中
    ↓
User: 点击 "USE" 按钮
    ↓
backpackInterface._buttonClicked()
    ├─> 获取选中物品
    ├─> 检查物品类型
    ├─> 调用物品效果处理
    └─> 发送 use_item_inven 信号
        ↓
        收集到各handlers:
        ├─> 消耗品: 应用Buff, 消耗数量
        │   ├─> 创建 BuffAdd 对象
        │   ├─> 启动 BuffThread
        │   ├─> 发送信号到statusInterface
        │   └─> 播放使用动画
        │
        ├─> 掉落物品: 创建 QItemDrop 配件
        │   ├─> 设置掉落轨迹
        │   ├─> 配件弹出
        │   └─> 可被收集
        │
        └─> 子宠物: 生成 SubPet
            ├─> 跟随主宠物
            └─> 独立动画
```

### 5.4 任务完成流程

```
User: 在taskInterface中勾选任务
    ↓
taskPanel._checkTask()
    ├─> 标记任务为完成
    ├─> 计算奖励
    │   └─> SINGLETASK_REWARD = 200 coins
    │   └─> FIVETASK_REWARD = 1500 coins (每5个)
    ├─> 发送 addCoins 信号
    │   ↓
    │   backpackInterface 接收
    │   ├─> coins += reward_amount
    │   ├─> 更新UI显示
    │   └─> 发送 coinUpdated 信号
    │       ↓
    │       shopInterface 更新硬币显示
    │
    └─> 更新任务数据 (task_data.json)
```

### 5.5 HP自动下降机制

```
Timer (每 HP_INTERVAL = 2 秒一次)
    ↓
if not HP_stop flag:
    HP -= 1
    ↓
    更新 HP_tier:
    ├─> if HP < 50: tier = 0 (Starving)
    ├─> if 50 ≤ HP < 80: tier = 1 (Hungry)
    ├─> if 80 ≤ HP < 100: tier = 2 (Normal)
    └─> if HP ≥ 100: tier = 3 (Energetic)
    ↓
    发送 hptier_changed 信号
    ↓
    Animation_worker 接收
    ├─> update_prob()
    └─> 重新计算动作概率
    ↓
    发送 BubbleManager.trigger_bubble()
    ├─> if HP < 50: 显示 "hp_low" 气泡
    └─> if HP == 0: 显示 "hp_zero" 气泡
```

---

## 6. 系统配置与常数

### 6.1 游戏平衡常数

| 参数 | 值 | 说明 |
|------|---|------|
| `HP_TIERS` | [0,50,80,100] | HP分级阈值 |
| `HP_INTERVAL` | 2秒 | HP下降频率 |
| `PP_HEART` | 0.8 | 心形掉落概率 |
| `PP_COIN` | 0.9 | 硬币掉落概率 |
| `PP_ITEM` | 0.95 | 物品掉落概率 |
| `PP_AUDIO` | 0.8 | 音频播放概率 |
| `PP_BUBBLE` | 0.15 | 气泡出现概率 |
| `ITEM_DEPRECIATION` | 0.75 | 物品出售折扣 |
| `SINGLETASK_REWARD` | 200 | 单任务奖励金币 |
| `FIVETASK_REWARD` | 1500 | 五任务奖励金币 |
| `FACTOR_FEED_REQ` | 5 | 需要喂食时的效果倍数 |

### 6.2 物理模拟参数

| 参数 | 值 | 说明 |
|------|---|------|
| `gravity` | 0.41 | 重力加速度 |
| `dropspeed` | 1.0 | 掉落速度系数 |
| `interact_speed` | 0.02 | 交互响应时间 (x1000ms) |
| `fixdragspeedx` | 1.0 | 拖拽x方向速度系数 |
| `fixdragspeedy` | 1.0 | 拖拽y方向速度系数 |

### 6.3 路径配置

- Windows: 程序目录 (`basedir = ''`)
- Mac/Linux: 程序父目录 (`basedir = dirname(dirname(__file__))`)
- 配置目录: Windows/Mac同basedir，Linux为`~/.config/DyberPet/`

### 6.4 支持的语言

- 简体中文 (`zh_CN`) - 默认
- 英文 (`en_US`) - 可选

---

## 7. 关键特性深入解析

### 7.1 多宠物系统

**支持的宠物**:
1. **Kitty** - 基础宠物
2. **ChrisKitty** - 变体宠物
3. **派蒙** (Paimon) - 联动宠物

**切换机制**:
```python
# 在设置中选择默认宠物
settings.default_pet = "Kitty"

# 运行时切换 (信号触发)
PetWidget.changePet() 
    ↓
settings.petname = new_pet_name
PetWidget.setup_pet(new_pet_name)
    ↓
加载新宠物配置和资源
```

---

### 7.2 等级系统

**升级经验表**:
```
LVL_BAR = [20] + [120] * 200
# 第1级需要20经验
# 第2-201级各需要120经验
# 总计约24020经验达到满级
```

**升级机制**:
```
当 current_exp >= LVL_BAR[current_level]:
    ↓
current_exp -= LVL_BAR[current_level]
current_level += 1
    ↓
发送 level_up 信号
    ├─> 解锁新动作
    ├─> 增加好感度
    └─> 播放升级动画
```

---

### 7.3 Buff系统详解

**Buff类型**:

1. **增益型 (BuffAdd)** - 定时触发效果
   ```
   {
     "effect": "hp",           // 效果类型
     "value": 5,               // 每次增加值
     "interval": 10,           // 每10秒触发一次
     "expiration": 300         // 持续300秒
   }
   ```

2. **状态型 (BuffAlt)** - 改变状态
   ```
   {
     "effect": "HP_stop",      // 停止HP下降
     "expiration": 600         // 持续600秒
   }
   ```

**Buff堆叠**:
- 同类型Buff可多个存在
- 每个Buff维护独立的计时器
- 单个Buff过期时移除该层

**Buff优先级**:
- 移除操作按索引处理
- 最后添加的Buff索引最高

---

### 7.4 动作系统深入

**动作帧加载**:
```
act_conf.json 配置 + 文件夹中的PNG
    ↓
遍历 role/{pet_name}/action/ 目录
    ↓
按文件名数字排序 (0, 1, 2, ...)
    ↓
加载每张为 QPixmap 对象
    ↓
组成 frames 列表
    ↓
Act 对象保存：动作名、帧列表、帧间隔、循环次数
```

**动作播放演算法**:
```
_show_act(act_obj, duration):
    ↓
    当前帧 = 0
    播放计时器启动
    ↓
    Timer 回调 (每帧间隔)
        ↓
        绘制当前帧
        当前帧 += 1
        ↓
        if 当前帧 >= 总帧数:
            if 循环次数 > 0:
                循环次数 -= 1
                当前帧 = 0
            else if 循环 == -1 (无限循环):
                当前帧 = 0
            else:
                动作结束 ✓
```

---

### 7.5 好感度系统

**FV升级机制** (v2版本):
```
每当用户与宠物互动：
    ├─> 敲击宠物 (patpat)
    ├─> 使用道具
    ├─> 在仪表板查看
    └─> 完成任务

    ↓

FV_value += interaction_points
    ↓
if FV_value >= LVL_BAR[current_fv_lvl]:
    FV_value -= LVL_BAR[current_fv_lvl]
    FV_lvl += 1
    ↓
    发送 fv_lvlup 气泡
    ↓
    Animation_worker.fvchange()
    ├─> 更新动作概率分布
    └─> 解锁新动作
```

**好感度等级效果**:
- 解锁更高级动作（需要FV_lvl >= 特定值）
- 改变动作播放概率
- 影响气泡内容

---

## 8. 扩展点与自定义指南

### 8.1 添加新宠物

1. **创建宠物资源目录**
   ```
   res/role/{new_pet_name}/
   ├── pet_conf.json
   ├── act_conf.json
   ├── action/
   │   ├── 0.png, 1.png, ... (动作帧)
   │   └── ...
   └── info/
       └── info.json (宠物信息)
   ```

2. **配置 pet_conf.json**
   ```json
   {
     "width": 112,
     "height": 128,
     "scale": 1.0,
     "default": "default",
     "drag": "drag_action",
     "fall": "fall_action",
     "patpat": "patpat_action",
     "random_act": [...]
   }
   ```

3. **配置 act_conf.json**
   ```json
   {
     "action_name": {
       "loop": -1,
       "frame_interval": 100,
       "status_type": [0, 0],
       "act_prob": 0.5,
       "unlocked": true,
       "in_playlist": true,
       "sound": null
     }
   }
   ```

4. **在 settings.py 中注册**
   ```python
   PetConfig.init_config(new_pet_name, pic_dict)
   ```

### 8.2 添加新Buff

1. **在 item_conf.json 中配置**
   ```json
   {
     "item_id": {
       "buff": {
         "effect": "hp",
         "value": 10,
         "interval": 5,
         "expiration": 300
       }
     }
   }
   ```

2. **在使用物品时自动应用**
   - BuffThread 会自动处理

### 8.3 添加新气泡类型

1. **编辑 bubble_conf.json**
   ```json
   {
     "custom_bubble": {
       "icon": "pet_name",
       "message": "自定义消息",
       "countdown": null,
       "start_audio": null,
       "end_audio": null
     }
   }
   ```

2. **在代码中触发**
   ```python
   bubble_manager.trigger_bubble("custom_bubble")
   ```

### 8.4 添加新任务类型

1. **扩展 TaskData 类**
2. **在 taskUI.py 中添加处理**
3. **配置奖励机制**

---

## 9. 性能与优化考虑

### 9.1 渲染优化

- **部分刷新**: 仅更新改变的宠物区域
- **帧缓存**: 动画帧预加载到内存
- **图片缩放**: 使用 `QPixmap.scaledToWidth()` 缓存

### 9.2 内存管理

- **资源缓存**: pic_dict 存储已加载图片
- **及时释放**: 窗口关闭时清理资源
- **Buff清理**: 过期Buff立即移除

### 9.3 线程管理

- **Animation Worker**: 独立线程，不阻塞UI
- **Buff Thread**: 后台定时器，低频率更新
- **Signal/Slot**: 确保线程安全通信

### 9.4 性能指标目标

- **主循环**: 60fps (16.7ms/frame)
- **内存占用**: <200MB (含所有资源)
- **CPU使用**: <5% (空闲时)
- **响应延迟**: <100ms (用户操作)

---

## 10. 调试与维护

### 10.1 日志系统

```python
# 在 utils.py 中
def log(*args, **kwargs):
    print(*args, **kwargs)  # 简单输出到控制台
```

**关键日志点**:
```python
log('start running pet %s' % pet_conf.petname)
log('animation module is aware of the hp tier change!')
log('animation module is aware of the fv lvl change! %i' % fv_lvl)
```

### 10.2 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|--------|
| 宠物不动 | Animation线程未启动 | 检查 Animation_worker.run() |
| Buff不生效 | BuffThread未启动 | 检查 statusInterface.startBuffThread() |
| UI卡顿 | 主线程阻塞 | 确保重操作在后台线程 |
| 配置不加载 | JSON格式错误 | 使用JSON验证工具检查 |
| 图片显示错误 | 路径错误或缩放问题 | 检查 basedir 和图片路径 |

### 10.3 测试重点

- ☑ 多宠物切换
- ☑ HP自动下降与等级变化
- ☑ Buff添加、叠加、过期
- ☑ 物品使用与掉落
- ☑ 任务完成与奖励
- ☑ 动作播放与转换
- ☑ 跨模块信号通信
- ☑ 窗口管理和焦点

---

## 11. 打包与部署

### 11.1 开发环境

```bash
# 依赖安装
pip install PySide6==6.x.x
pip install PySide6-Fluent-Widgets==1.5.4+
pip install apscheduler
pip install pynput
pip install tendo

# 运行
python run_DyberPet.py
```

### 11.2 打包为可执行文件

**Windows**:
```bash
pyinstaller --noconsole \
  --icon="000.ico" \
  --hidden-import="pynput.mouse._win32" \
  --hidden-import="pynput.keyboard._win32" \
  run_DyberPet.py
```

**Mac**:
```bash
pyinstaller --windowed \
  --icon 000.icns \
  --add-data="res:res" \
  --add-data="DyberPet:DyberPet" \
  --hidden-import="pynput.mouse._darwin" \
  --hidden-import="pynput.keyboard._darwin" \
  run_DyberPet.py
```

**Linux**: 类似Mac配置

### 11.3 发布流程

1. 版本更新: 修改 `settings.py` 中 `VERSION`
2. 版本记录: 更新 `data/version` 文件
3. 构建: 运行 PyInstaller
4. 上传: 发布到 GitHub Release

---

## 12. 总体特征总结

### 设计原则
✓ **模块化**: 清晰的职责分离  
✓ **可扩展**: 易于添加宠物、动作、物品  
✓ **响应式**: UI线程不阻塞，动画流畅  
✓ **配置化**: JSON驱动，无需修改代码  
✓ **跨平台**: Windows/Mac/Linux支持  

### 架构强度
✓ **事件驱动**: Signal/Slot机制  
✓ **数据分离**: 配置与代码解耦  
✓ **线程安全**: 后台任务独立线程  
✓ **资源管理**: 缓存与及时释放  

### 可维护性
✓ 代码结构清晰，模块职责明确  
✓ 配置文件完整，易于调试  
✓ 多语言支持  
✓ UI采用成熟的Fluent Design  

---

## 附录A: 关键文件参考表

| 文件路径 | 主要类 | 作用 |
|---------|--------|------|
| run_DyberPet.py | DyberPetApp | 应用入口 |
| DyberPet.py | PetWidget, DP_HpBar | 主宠物窗口 |
| modules.py | Animation_worker, BuffAdd, BuffAlt | 核心游戏逻辑 |
| conf.py | PetConfig, Act, PetData, ActData, TaskData, ItemData | 配置系统 |
| settings.py | (全局变量和常数) | 全局设置 |
| utils.py | (工具函数) | 公用函数库 |
| Accessory.py | DPAccessory, SubPet, QItemDrop | 配件系统 |
| bubbleManager.py | BubbleManager | 气泡管理 |
| Dashboard/DashboardUI.py | DashboardMainWindow | 仪表板主窗口 |
| Dashboard/statusUI.py | statusInterface, StatusCard, BuffCard | 状态面板 |
| Dashboard/inventoryUI.py | backpackInterface | 背包面板 |
| Dashboard/shopUI.py | shopInterface | 商店面板 |
| Dashboard/taskUI.py | taskInterface | 任务面板 |
| Dashboard/dashboard_widgets.py | 各种自定义组件 | UI组件库 |

---

## 附录B: Signal 信号快速参考

| 发送者 | 信号名 | 参数 | 接收者 |
|--------|--------|------|--------|
| PetWidget | changePet | - | DashboardMainWindow |
| PetWidget | addCoins | int, bool | backpackInterface |
| statusInterface | addBuff | dict | buffThread |
| statusInterface | rmBuffInThread | str | buffThread |
| backpackInterface | addBuff | dict | statusInterface |
| backpackInterface | rmBuff | str | statusInterface |
| shopInterface | buyItem | str | backpackInterface |
| taskInterface.taskPanel | addCoins | int,bool | backpackInterface |
| Animation_worker | sig_move_anim | x, y | PetWidget |
| buffThread | takeEffect | effect, value | PetWidget/statusInterface |

---

**文档版本**: v1.0  
**最后更新**: 2026年3月17日  
**适用版本**: DyberPet v0.7.7+

