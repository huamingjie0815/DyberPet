# ClawPet 开发者速查表

## 快速导航

### 📋 文档清单
1. **DESIGN_DOCUMENT.md** - 完整的系统设计文档（推荐首先阅读）
2. **ARCHITECTURE_DEEP_DIVE.md** - 深度技术分析与扩展指南
3. **DEVELOPER_CHEATSHEET.md** - 本文档，快速查阅

---

## 一、项目结构速查

### 目录结构速记
```
ClawPet/              # 主模块
├── ClawPet.py        ⭐ 主宠物窗口 (PetWidget)
├── modules.py         ⭐ 核心逻辑 (Animation, Buff, Bubble)
├── conf.py            ⭐ 配置系统 (PetConfig, Act, Data)
├── settings.py        ⭐ 全局设置
├── Accessory.py       ⭐ 配件系统
├── Dashboard/         ⭐ 仪表板模块
│   ├── DashboardUI.py     主窗口协调
│   ├── statusUI.py        宠物属性显示
│   ├── inventoryUI.py     物品管理
│   ├── shopUI.py          商店购买/出售
│   ├── taskUI.py          任务系统
│   ├── dashboard_widgets.py  UI组件库
│   └── buffModule.py      Buff管理线程
└── DyberSettings/     ⭐ 设置面板模块

res/                   # 资源
├── role/{pet}/        宠物资源文件夹
│   ├── pet_conf.json  🔴 宠物配置（必需！）
│   ├── act_conf.json  🔴 动作配置（必需！）
│   └── action/        动作帧PNG文件

data/                  # 数据保存
├── pet_data.json      🔴 宠物游戏存档（最重要）
├── settings.json      用户设置
├── act_data.json      动作解锁状态
└── task_data.json     任务数据
```

**⭐** = 关键模块 | **🔴** = 必需配置

---

## 二、关键类与方法速查

### 2.1 PetWidget 类

| 方法 | 参数 | 说明 |
|------|------|------|
| `setup_pet(pet_name)` | str | 初始化宠物 👈 最重要 |
| `show_act(act, duration)` | Act, float | 播放动作 |
| `patpat()` | - | 敲击宠物反应 |
| `handleMousePress()` | QMouseEvent | 鼠标按下 |
| `handleMouseMove()` | QMouseEvent | 鼠标移动 |
| `paintEvent()` | QPaintEvent | 绘制宠物 |

**信号**:
- `changePet`: 切换宠物
- `addCoins(int, bool)`: 增加硬币
- `hptier_changed(int, str)`: HP等级变化

---

### 2.2 Animation_worker 类

| 方法 | 说明 |
|------|------|
| `run()` | 线程主循环 (后台运行，5秒刷新) |
| `random_act()` | 选择并触发随机动作 |
| `_cal_prob(status)` | 计算动作概率分布 |
| `hpchange(tier, dir)` | HP变化回调 |
| `fvchange(lvl)` | FV变化回调 |
| `pause() / resume() / kill()` | 线程控制 |

**信号**:
- `sig_setimg_anim`: 设置图片
- `sig_move_anim(x, y)`: 移动位置
- `sig_repaint_anim`: 重绘请求

---

### 2.3 PetConfig 类

| 属性 | 类型 | 说明 |
|------|------|------|
| `petname` | str | 宠物名称 |
| `width / height` | float | 尺寸 |
| `scale` | float | 缩放因子 |
| `refresh` | int | 动画刷新间隔 (秒) |
| `act_dict` | dict | 所有动作 {name: Act} |
| `random_act` | list | 随机动作组 |
| `patpat` | dict | 敲击反应 {tier: Act} |
| `default` | Act | 默认动作 |
| `up/down/left/right` | Act | 移动动作 |
| `drag / fall` | Act | 拖拽/掉落动作 |

**初始化**:
```python
pet_conf = PetConfig.init_config("Kitty", pic_dict)
```

---

### 2.4 Act 类

| 属性 | 类型 | 说明 |
|------|------|------|
| `name` | str | 动作名 |
| `act_frames` | list[QPixmap] | 帧列表 |
| `frame_interval` | int | 帧间隔 (ms) |
| `loop` | int | 循环次数 (-1=无限) |
| `status_type` | [int, int] | [min_hp_tier, min_fv_lvl] |
| `unlocked` | bool | 是否解锁 |
| `in_playlist` | bool | 是否在随机列表 |

---

### 2.5 PetData 类

| 属性 | 类型 | 范围 | 说明 |
|------|------|------|------|
| `HP` | int | 0-200 | 当前血量 |
| `HP_tier` | int | 0-3 | HP等级 (0=饥饿, 3=饱满) |
| `FV` | int | 0-N | 当前好感度值 |
| `FV_lvl` | int | 0-200+ | 好感度等级 |
| `coins` | int | 0-∞ | 硬币数 |
| `items` | dict | - | 物品库存 {id: qty} |
| `days` | int | 1+ | 游玩天数 |
| `last_opened` | str | YYYY-m-d | 最后打开日期 |

---

### 2.6 BuffThread 类

| 方法 | 说明 |
|------|------|
| `add_buff(buff_obj)` | 添加Buff，返回ID |
| `remove_buff(buff_id, idx)` | 移除指定层Buff |
| `update()` | 更新所有Buff (每秒调用) |

**关键属性**:
- `active_buffs`: list[BuffAdd/BuffAlt] - 活跃Buff列表

---

### 2.7 BuffAdd 类 (增益型)

```python
BuffAdd(name="food_buff", {
    "effect": "hp",           # hp / fv / coin
    "value": 5,               # 每次增加量
    "interval": 10,           # 每10秒触发一次
    "expiration": 300         # 持续300秒 (可选)
})
```

| 方法 | 说明 |
|------|------|
| `trigger()` | 触发效果 -> takeEffect 信号 |
| `addnew()` | 添加新层（堆叠） |
| `endone(idx)` | 移除指定层 |
| `terminate()` | 完全移除此Buff |

---

### 2.8 BubbleManager 类

| 方法 | 说明 |
|------|------|
| `trigger_bubble(type)` | 触发气泡 ("hp_low", "fv_lvlup" 等) |
| `load_bubble_config()` | 加载配置 |

**预定义气泡类型**:
- `hp_low`: HP过低
- `hp_zero`: HP耗尽
- `fv_lvlup`: 好感度升级
- `fv_drop`: 好感度下降
- `feed_done`: 喂食完成
- `feed_required`: 需要喂食
- `pat_focus`: 集中点击
- `pat_frequent`: 频繁敲击
- `pat_random`: 随机敲击反应

---

## 三、全局设置速查

### 3.1 settings 全局变量

```python
import ClawPet.settings as settings

# 当前宠物信息
settings.petname              # str, 当前宠物名 ("Kitty")
settings.pet_data             # PetData, 宠物游戏数据
settings.act_data             # ActData, 动作配置
settings.task_data            # TaskData, 任务数据
settings.items_data           # ItemData, 物品数据

# 控制标志
settings.HP_stop              # bool, 停止HP下降
settings.FV_stop              # bool, 停止FV增加

# 用户设置
settings.scale_dict["Kitty"]  # float, 宠物缩放 (1.0=正常)
settings.usertag_dict["Kitty"] # str, 用户昵称

# 版本信息
settings.VERSION              # "v0.7.7"
settings.BASEDIR              # 项目根目录路径
settings.CONFIGDIR            # 配置文件目录
```

### 3.2 游戏常数

```python
settings.HP_TIERS             # [0, 50, 80, 100] - HP分级阈值
settings.TIER_NAMES           # ['Starving', 'Hungry', 'Normal', 'Energetic']
settings.HP_INTERVAL          # 2 - HP下降频率 (秒)

settings.LVL_BAR              # [20] + [120]*200 - 升级经验表
settings.PP_HEART             # 0.8 - 心形掉落概率
settings.PP_COIN              # 0.9 - 硬币掉落概率
settings.PP_ITEM              # 0.95 - 物品掉落概率
settings.PP_AUDIO             # 0.8 - 音频播放概率

settings.SINGLETASK_REWARD    # 200 - 单任务奖励
settings.FIVETASK_REWARD      # 1500 - 五任务奖励

settings.HUNGERSTR            # "Satiety"
settings.FAVORSTR             # "Favorability"
```

---

## 四、JSON 配置格式快查

### 4.1 pet_conf.json 模板

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
  "prefall": "fall_action",
  "on_floor": "default",
  "patpat": "patpat_action",
  
  "random_act": [
    {
      "name": "normal_actions",
      "act_list": ["default", "sit", "jump"],
      "act_prob": [1.0, 0.7, 0.5],
      "act_type": [0, 0]
    }
  ],
  
  "main_interact": {}
}
```

### 4.2 act_conf.json 模板

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

**字段说明**:
- `loop`: -1=无限循环, 0=播放一次, n>0=播放n次
- `frame_interval`: ms/帧，建议50-150ms
- `status_type`: [最小HP等级, 最小FV等级]
- `icon_path`: 动作预览图 (可选)
- `description`: 动作描述 (可选)

### 4.3 pet_data.json 模板

```json
{
  "Kitty": {
    "HP": 199,
    "HP_tier": 3,
    "FV": 1,
    "FV_lvl": 0,
    "fv_sys_ver": "v2",
    "items": {
      "apple": 5,
      "book": 3
    },
    "coins": 1000,
    "days": 15,
    "last_opened": "2026-3-17"
  }
}
```

### 4.4 bubble_conf.json 模板

```json
{
  "hp_low": {
    "icon": "system",
    "message": "I'm hungry...",
    "countdown": null,
    "start_audio": "system_notification",
    "end_audio": null
  },
  "pat_focus": {
    "icon": "pet_name",
    "message": "Hehe~ ♡",
    "countdown": 300,
    "start_audio": null,
    "end_audio": null
  }
}
```

---

## 五、常用操作速查

### 5.1 切换宠物

```python
# 方法1: 在main loop中
settings.petname = "ChrisKitty"
pet_widget.setup_pet("ChrisKitty")

# 方法2: 通过信号
pet_widget.changePet.emit()
```

### 5.2 改变HP

```python
# 直接修改
settings.pet_data.HP = 150
settings.pet_data.HP_tier = 2

# 发送信号更新UI
pet_widget.hptier_changed.emit(2, "Normal")
```

### 5.3 创建和应用Buff

```python
from ClawPet.modules import BuffAdd

buff_config = {
    "effect": "hp",
    "value": 10,
    "interval": 5,
    "expiration": 300
}

buff = BuffAdd("food_buff", buff_config)
buff_thread.add_buff(buff)

# 监听效果
buff.takeEffect.connect(handle_buff_effect)
```

### 5.4 触发气泡

```python
bubble_manager.trigger_bubble("hp_low")
bubble_manager.trigger_bubble("fv_lvlup")
bubble_manager.trigger_bubble("pat_random")
```

### 5.5 播放动作

```python
# 从配置中获取
act = pet_conf.default
pet_widget.show_act(act, duration=5.0)

# 或触发随机动作（让Animation_worker处理）
animation_worker.random_act()
```

### 5.6 添加物品和硬币

```python
# 硬币
settings.pet_data.coins += 100
coin_updated_signal.emit(settings.pet_data.coins)

# 物品
if "apple" not in settings.pet_data.items:
    settings.pet_data.items["apple"] = 0
settings.pet_data.items["apple"] += 5
item_updated_signal.emit("apple")
```

### 5.7 升级好感度

```python
settings.pet_data.FV_lvl += 1
settings.pet_data.fv_sys_ver = "v2"

# 触发升级气泡和动画
bubble_manager.trigger_bubble("fv_lvlup")
animation_worker.fvchange(settings.pet_data.FV_lvl)
```

---

## 六、特殊函数速查

### 6.1 文本处理

```python
from ClawPet.utils import text_wrap, MaskPhrase

# 自动换行处理
wrapped = text_wrap(text, width=30)

# 敏感词过滤
masked = MaskPhrase(text)
```

### 6.2 时间转换

```python
from ClawPet.utils import TimeConverter

converter = TimeConverter()
readable_time = converter.format(timestamp, format='%Y-%m-%d %H:%M')
```

### 6.3 子宠物管理

```python
from ClawPet.utils import SubPet_Manager

manager = SubPet_Manager()
manager.get_subpet(pet_name)
```

### 6.4 JSON读写

```python
from ClawPet.utils import read_json, write_json

# 读取
data = read_json("path/to/config.json")

# 写入
import json
with open(file_path, 'w', encoding='UTF-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

---

## 七、Dashboard 面板速查

### 7.1 statusInterface (状态面板)

**关键Widget**:
- `StatusCard`: 宠物属性卡片 (HP、FV、等级)
- `BuffCard`: Buff列表显示
- `NoteFlowGroup`: 事件日志流

**主要信号**:
- `changePet`: 宠物切换 -> BuffCard._clearBuff
- `addBuff2Thread(dict)`: 添加Buff
- `addCoins(int, bool)`: 增加硬币

---

### 7.2 backpackInterface (背包面板)

**关键Widget**:
- `itemTabWidget`: 物品网格（3个Tab）
  - Tab0: 消耗品 (Food)
  - Tab1: 收集品 (Collection)
  - Tab2: 子宠物 (Pets)
- `coinWidget`: 硬币显示

**主要信号**:
- `use_item_inven(item_id)`: 使用物品
- `addBuff(buff_config)`: 创建Buff
- `addCoins(amount, source)`: 增加硬币

---

### 7.3 shopInterface (商店面板)

**功能**: 物品买卖

**主要信号**:
- `buyItem(item_id)`: 购买物品
- `sellItem(item_id)`: 出售物品
- `updateCoin()`: 更新硬币

---

### 7.4 taskInterface (任务面板)

**子面板**:
- `focusPanel`: 今日专注任务
- `progressPanel`: 进行中的任务
- `taskPanel`: 任务完成

**主要信号**:
- `addCoins()`: 任务奖励

---

## 八、常见问题排查 (Q&A)

| 问题 | 原因 | 解决 |
|------|------|------|
| 宠物不显示 | basedir错误，图片路径不对 | 检查 settings.BASEDIR |
| 宠物不动 | Animation_worker未启动 | 检查 `thread.start()` |
| Buff不生效 | BuffThread未启动 | 启动 statusInterface.startBuffThread() |
| HP不下降 | HP_stop标志为True | 检查Buff或手动设置 `settings.HP_stop = False` |
| UI卡顿 | 主线程阻塞 | 重操作移到后台线程 |
| 配置不加载 | JSON格式错误 | 使用在线JSON验证器检查 |
| 内存泄漏 | 线程未清理 | 在窗口关闭时调用 `worker.kill()` |
| 信号未触发 | Signal未连接 | 检查 `.connect()` 的接收器存活 |

---

## 九、开发工作流

### 9.1 添加新动作的步骤

1. 准备帧图片
   ```
   res/role/{pet}/action/
   ├── existing_action_0.png
   ├── new_action_0.png
   ├── new_action_1.png
   └── new_action_2.png
   ```

2. 添加到 act_conf.json
   ```json
   {
     "new_action": {
       "loop": 2,
       "frame_interval": 100,
       "status_type": [0, 0],
       "act_prob": 0.5,
       "unlocked": false,
       "in_playlist": true
     }
   }
   ```

3. 在 pet_conf.json 中引用 (可选)
   ```json
   {
     "random_act": [
       {
         "name": "normal_actions",
         "act_list": ["default", "new_action"],
         "act_prob": [1.0, 0.5]
       }
     ]
   }
   ```

4. 在代码中使用
   ```python
   new_act = pet_conf.act_dict["new_action"]
   pet_widget.show_act(new_act, duration=2.0)
   ```

### 9.2 添加新物品的步骤

1. 在资源文件夹中放置图片
   ```
   res/items/{category}/{item_id}.png
   ```

2. 添加到物品配置
   ```json
   {
     "item_id": {
       "name": "Apple",
       "description": "A fresh apple",
       "icon": "apple.png",
       "category": "consumable",
       "buff": {
         "effect": "hp",
         "value": 30,
         "interval": 5,
         "expiration": 300
       }
     }
   }
   ```

3. 现有库存添加
   ```python
   settings.pet_data.items["item_id"] = 5
   ```

### 9.3 调试技巧

```python
# 在主循环添加调试输出
if DEBUG:
    print(f"HP: {settings.pet_data.HP}, Tier: {settings.pet_data.HP_tier}")
    print(f"Buff count: {len(buff_thread.active_buffs)}")
    print(f"Position: ({pet_widget.x}, {pet_widget.y})")
    print(f"Current action: {animation_worker.current_act}")

# 保存日志到文件
with open("debug.log", "a") as f:
    f.write(f"[{datetime.now()}] Event: {event_name}\n")
```

---

## 十、性能指标与目标

| 指标 | 目标 | 检查方法 |
|------|------|--------|
| FPS | 60 (16.7ms/帧) | 添加计时器测量 paintEvent |
| 内存占用 | <200MB | 使用memory_profiler |
| 响应延迟 | <100ms | 从click到display |
| CPU使用 | <5% (空闲) | 任务管理器 |
| 启动时间 | <2s | time.time() |

---

## 快速代码片段库

### 片段1: 完整的Buff使用示例

```python
from ClawPet.modules import BuffAdd, BuffThread

# 创建Buff
config = {
    "effect": "hp",
    "value": 5,
    "interval": 10,
    "expiration": 300
}
buff = BuffAdd("apple_buff", config)

# 启动线程
buff_thread = BuffThread()
buff_thread.start()

# 添加Buff
buff_id = buff_thread.add_buff(buff)

# 监听效果
def handle_effect(effect, value):
    if effect == "hp":
        settings.pet_data.HP += value
        if settings.pet_data.HP > 200:
            settings.pet_data.HP = 200

buff.takeEffect.connect(handle_effect)
buff.terminateBuff.connect(lambda name: print(f"{name} expired"))
```

### 片段2: 气泡和动作组合

```python
def feed_pet(item_id):
    # 应用Buff
    item_config = settings.items_data.get_item(item_id)
    if "buff" in item_config:
        buff = BuffAdd(item_id, item_config["buff"])
        buff_thread.add_buff(buff)
    
    # 显示动作
    eat_action = pet_conf.act_dict.get("eat", pet_conf.default)
    pet_widget.show_act(eat_action, duration=2.0)
    
    # 触发气泡
    bubble_manager.trigger_bubble("feed_done")
    
    # 更新库存
    settings.pet_data.items[item_id] -= 1
```

### 片段3: Dashboard信号连接

```python
class MyWindow:
    def __init__(self):
        self.dashboard = DashboardMainWindow()
        
        # 背包 -> 状态 (添加Buff)
        self.dashboard.backpackInterface.addBuff.connect(
            self.dashboard.statusInterface._addBuff
        )
        
        # 状态 -> 背包 (增加硬币)
        self.dashboard.statusInterface.addCoins.connect(
            self.dashboard.backpackInterface.addCoins
        )
        
        # 任务 -> 背包 (奖励)
        self.dashboard.taskInterface.taskPanel.addCoins.connect(
            self.dashboard.backpackInterface.addCoins
        )
```

---

**最后更新**: 2026年3月17日  
**版本**: v0.7.7+  
**适用范围**: 开发、调试、扩展

