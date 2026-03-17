# DyberPet 架构深度分析与技术文档

## Part 1: 详细架构图解

### 1.1 完整系统数据流图

```
┌──────────────────────────────────────────────────────────────────┐
│                    User Interaction Layer                        │
│                                                                  │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────┐         │
│  │ Mouse Event │    │Keyboard Event│    │Touch/Drag   │         │
│  │ (Click)     │    │(Keyboard)    │    │(Movement)   │         │
│  └──────┬──────┘    └────────┬─────┘    └──────┬──────┘         │
│         │                    │                  │                │
│         └────────────────────┼──────────────────┘                │
│                              │                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               │
                               ↓
┌──────────────────────────────────────────────────────────────────┐
│                    PetWidget (Main Window)                       │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Event Handlers                                           │   │
│  │ ├─ mousePressEvent()  ────→ patpat() / drag start      │   │
│  │ ├─ mouseMoveEvent()   ────→ position update             │   │
│  │ ├─ mouseReleaseEvent()────→ drag stop                   │   │
│  │ └─ mouseDoubleClickEvent()─→ custom action              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ Physics Eng  │  │ Collision    │  │ Rendering    │           │
│  │ (Gravity)    │  │ Detection    │  │ (paintEvent) │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│         │                  │                  │                  │
│         └──────────────────┼──────────────────┘                  │
│                            │                                     │
│  ┌──────────────────────────────────┐                           │
│  │ Signal Emission                  │                           │
│  │ ├─ changePet                    │                           │
│  │ ├─ addCoins(amount, source)     │                           │
│  │ ├─ task_over                    │                           │
│  │ ├─ level_up                     │                           │
│  │ └─ state_change(type, value)    │                           │
│  └──────────────────────────────────┘                           │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ↓                   ↓                   ↓
┌─────────────────────┐ ┌──────────────┐ ┌───────────────┐
│ Animation_worker    │ │ BuffThread   │ │ BubbleManager │
│ (独立Thread)       │ │(后台定时器)  │ │(气泡消息)     │
│                     │ │              │ │               │
│ ┌─────────────────┐ │ ├─ BuffAdd    │ ├─ Trigger     │
│ │ random_act()    │ │ ├─ BuffAlt    │ │  bubble()     │
│ ├─ _cal_prob()   │ │ └─ update()    │ ├─ Load config │
│ ├─ hpchange()    │ │                │ └─ manage      │
│ ├─ fvchange()    │ │ Signal:        │   bubbles      │
│ └─ run() loop     │ │ takeEffect     │   types        │
│                   │ │ removeBuff     │                │
│ Emit Signals:     │ │ terminateBuff  │ Signal:        │
│ ├─ sig_setimg     │ │                │ register_      │
│ ├─ sig_move       │ │                │ bubble         │
│ ├─ sig_repaint    │ │                │                │
│ └─ acc_regist     │ │                │                │
└──────────┬────────┘ └────────┬───────┘ └────────┬──────┘
           │                   │                  │
           └───────────────────┼──────────────────┘
                               │
                    Signal回传到PetWidget
                               │
         ┌─────────────────────┼──────────────────┬─────────┐
         │                     │                  │         │
         ↓                     ↓                  ↓         ↓
    更新位置            应用Buff效果          显示气泡    播放动作
    更新动作            变更属性值           触发音效     配件效果
    碰撞处理            UI更新               消息日志


```

### 1.2 Dashboard 信号通信矩阵

```
                ┌──────────────────────────────────────────────┐
                │        DashboardMainWindow                   │
                │                                              │
                │  Signal Relay & Orchestration Center        │
                └──────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ↓                           ↓                           ↓
  ┌────────────────┐        ┌────────────────┐       ┌────────────────┐
  │statusInterface │        │backpackUI      │       │shopInterface   │
  │                │        │                │       │                │
  │ StatusCard     │◄──────►│ coinWidget     │◄─────►│ coinWidget     │
  │ BuffCard       │  add   │                │       │                │
  │ NoteFlowGroup  │  buff  │ itemTabWidget  │ item  │ itemDisplay    │
  │                │        │                │ num   │                │
  │ addCoins◄──────┼────────┼────coinUpdated─┼──────►│ updateCoin     │
  │                │        │                │       │                │
  │ rmBuffInThread │        │               │       │                │
  │ changeStatus   │        │               │       │                │
  │ addBuff2Thread │        │               │       │                │
  └────────────────┘        └────────────────┘       └────────────────┘
        ▲                            ▲                        ▲
        │                            │                        │
        │  removeBuff         addCoins│ sell / buy         addCoins
        │  addCoins           use_item│ updateCoin         updateCoin
        │                   rmBuff    │                       │
        │                            │                        │
        │                    ┌────────▼────────┐              │
        │                    │  taskInterface  │              │
        │                    │                │              │
        │                    │ focusPanel      │              │
        │                    │ progressPanel   │──────────────┘
        │                    │ taskPanel       │
        │                    │                │
        │                    │ addCoins ─────┬┘
        │                    └────────────────┘
        │                           │
        └───────────────────────────┘
         (Buff removed, coin spent
          from backpack confirmed)
```

### 1.3 数据模型关系图

```
┌─────────────────────────────────────────────────────────────┐
│                   Global Settings (settings.py)             │
│                                                             │
│  ├─ petname: str                    (当前宠物名)         │
│  ├─ pet_data: PetData               (宠物游戏数据)       │
│  ├─ act_data: ActData               (动作全局配置)       │
│  ├─ task_data: TaskData             (任务数据)          │
│  ├─ items_data: ItemData            (物品数据)          │
│  ├─ settings_data: dict             (用户设置)          │
│  ├─ HP_stop / FV_stop: bool         (状态标志)          │
│  ├─ scale_dict: dict{pet: float}    (缩放字典)          │
│  └─ usertag_dict: dict{pet: str}    (用户标签)          │
│                                                             │
└──────────────────────────────────────────────────────────────┘
        ▲
        │ 初始化
        │
    ┌───┴───────────────────────────────────────────────┐
    │                                                   │
    ↓                                                   ↓
┌─────────────────────┐                    ┌──────────────────┐
│  JSON Files         │                    │ PetConfig        │
│                     │                    │                  │
│ pet_data.json ──┐   │                    │ (Per-Pet)        │
│ (多宠物状态)   │◄──►│                    │                  │
│                 │   │                    │ ├─ width/height  │
│ act_data.json ──┤   │                    │ ├─ scale         │
│ (动作定义)     │   │                    │ ├─ refresh       │
│                 ├──►│ init()             │ ├─ act_dict      │
│ settings.json ──┤   │                    │ ├─ random_act    │
│ (用户设置)     │   │                    │ ├─ patpat        │
│                 │   │                    │ └─ accessories   │
│ task_data.json ─┤   │                    │                  │
│ (任务定义)     │   │                    │ From:            │
│                 │   │                    │ res/role/        │
│ role/*/         │   │                    │ {pet}/           │
│ pet_conf.json ──┤   │                    │ pet_conf.json    │
│ act_conf.json   │◄──┘                    │                  │
│ (宠物工作文件)  │                        │                  │
└─────────────────┘                        └──────────────────┘
    ▲                                            ▲
    │                                            │
    └────┬────────────────────────────────────────┘
         │
         └─► PetData(宠物游戏状态)
             ├─ HP: int
             ├─ HP_tier: int (0-3)
             ├─ FV: int
             ├─ FV_lvl: int
             ├─ items: dict
             ├─ coins: int
             ├─ days: int
             └─ last_opened: str

         └─► Act(单个动作)
             ├─ name: str
             ├─ frames: list[QPixmap]
             ├─ frame_interval: int
             ├─ loop: int
             ├─ status_type: [int, int]
             ├─ unlocked: bool
             └─ in_playlist: bool

         └─► ActData(动作全局)
             ├─ allAct_params: dict
             ├─ allAct_unlocked: dict
             └─ animation_file: str

         └─► ItemData
             ├─ all_items: dict
             ├─ item_categories: dict
             └─ item_effects: dict
```

---

## Part 2: 核心系统详解

### 2.1 HP系统详细流程

```
HP初始值: 200 (满血)
每个生命周期:
  ├─ 存储: pet_data.json 的 HP field
  ├─ 显示: PetWidget 中的 DP_HpBar
  └─ 处理: modules.py 的 Animation_worker

时间轴:
┌──────────────────────────────────────────────────────────┐
│ t = 0                                                    │
│ HP: 200  HP_tier: 3                                     │
└──────────────────────────────────────────────────────────┘
         │
         │ 每 HP_INTERVAL(2s) 秒
         ↓ if not HP_stop:
┌──────────────────────────────────────────────────────────┐
│ t = 2s                                                   │
│ HP -= 1  → HP: 199                                       │
│ Check tier change:                                       │
│   └─ if HP < 50: tier = 0                              │
│   └─ elif HP < 80: tier = 1                             │
│   └─ elif HP < 100: tier = 2                            │
│   └─ elif HP >= 100: tier = 3                           │
│ Signal: hptier_changed(tierLevel, tierName)             │
│ Connected to:                                            │
│   ├─ Animation_worker.hpchange(tier, direction)         │
│   │   ├─ update_prob()                                 │
│   │   └─ recalc_cumulative_prob                        │
│   ├─ BubbleManager.trigger_bubble()                    │
│   │   ├─ if HP==0: "hp_zero"                          │
│   │   └─ if HP<50: "hp_low"                           │
│   └─ Dashboard statusUI update                         │
└──────────────────────────────────────────────────────────┘
         │
         │ ... (每2秒重复)
         ↓
┌──────────────────────────────────────────────────────────┐
│ t = 400s (HP下降到0)                                    │
│ HP: 0  HP_tier: 0 (Starving)                            │
│ Pet enters "Starving" mode                              │
│   ├─ Only hp_tier==0 actions playable                 │
│   ├─ "hp_zero" & "feed_required" bubbles shown         │
│   └─ No new action triggers until fed                  │
└──────────────────────────────────────────────────────────┘

用户喂食:
  │
  └─► 使用消耗品 (food item)
      ├─ BuffAdd 创建: effect="hp", value=50
      ├─ BuffThread 启动
      ├─ 每5秒应用一次 +5 HP
      ├─ 持续300秒 (10x5秒)
      │  HP: 0 → 50 (总共+50)
      │  HP_tier: 0 → 1
      └─ Buff过期后移除
```

### 2.2 动作概率计算的数学模型

```
设：
  h = 当前 HP_tier (0-3)
  f = 当前 FV_lvl (0-200+)
  a = 动作配置中的 {name, prob, status_type, unlocked, in_playlist}

动作可用性检查:
  if not a.unlocked:
    prob[i] = 0  /* 动作未解锁，概率为0 */
  
  elif h == 0 and a.status_type[0] != 0:
    prob[i] = 0  /* HP=0时只能播放特定动作 */
  
  elif f < a.status_type[1]:
    prob[i] = 0  /* FV等级不足，动作未解锁 */
  
  elif a.status_type[0] == 0:
    /* 不受HP等级限制的动作 */
    prob[i] = a.prob * (h == 0 ? 1 : 0)
    /* 仅在h==0时高概率 */
  
  else:
    /* 正常动作 */
    /* 距离函数：距离当前状态越近，概率越高 */
    distance = |a.status_type[0] - h|
    state_factor = (1/4)^distance
    
    prob[i] = a.prob * state_factor * (a.in_playlist ? 1 : 0)

归一化:
  sum_prob = sum(prob[0:n])
  if sum_prob != 0:
    prob_norm[i] = prob[i] / sum_prob
  else:
    prob_norm[i] = 0  /* 无可用动作 */

累积分布函数 (CDF):
  cumulative[0] = prob_norm[0]
  cumulative[i] = cumulative[i-1] + prob_norm[i]
  cumulative[-1] = 1.0  /* 确保最后一个是1.0 */

随机选择:
  r = random(0, 1)
  for i in range(len(cumulative)):
    if r <= cumulative[i]:
      selected_action = actions[i]
      break

例子:
───────
配置:
  HP_tier = 1 (Hungry)
  FV_lvl = 50
  
  动作A: prob=0.5, status_type=[0, 0], unlocked=true, in_playlist=true
  动作B: prob=1.0, status_type=[1, 0], unlocked=true, in_playlist=true  
  动作C: prob=0.5, status_type=[2, 50], unlocked=true, in_playlist=false
  动作D: prob=1.0, status_type=[2, 100], unlocked=false, in_playlist=true

计算:
  A: status_type[0]=0 → prob = 0.5 * (1==0 ? 1 : 0) = 0
  B: h=1, |1-1|=0 → prob = 1.0 * (1/4)^0 * 1 = 1.0
  C: h=1, |2-1|=1 → prob = 0.5 * (1/4)^1 * 0 = 0 (不在列表)
  D: unlocked=false → prob = 0

  sum = 1.0
  prob_norm = [0, 1.0, 0, 0]
  cumulative = [0, 1.0, 1.0, 1.0]
  
  结果: 100% 选择动作B
```

### 2.3 Buff系统执行流程

```
物品使用:
  ↓
itemTabWidget.onItemClicked(item)
  ├─ 获取item配置
  ├─ 检查 item.buff (如果存在)
  └─ Signal: use_item_inven(item_id)
     ↓
     backpackInterface._on_item_used()
     │
     ├─ if item.consumable:
     │  └─> 创建 BuffAdd:
     │      {
     │        "effect": item.buff.effect,
     │        "value": item.buff.value,
     │        "interval": item.buff.interval,
     │        "expiration": item.buff.expiration
     │      }
     │
     ├─ if item.drop:
     │  └─> 创建 QItemDrop 配件
     │
     └─ Signal: addBuff(buff_config)
        ↓
        statusInterface._addBuff()
        │
        ├─ buffThread.add_buff(buff_obj)
        │  └─ 返回 buff_id
        │
        └─ BuffCard.add_buff_widget(buff_obj)
           ├─ 显示Buff信息
           └─ 连接移除按钮

BuffThread 后台循环 (每秒):
  │
  ├─ for each buff in active_buffs:
  │  │
  │  ├─ BuffAdd.update()
  │  │  ├─ 每项 (interval, expiration) 递减1
  │  │  ├─ if interval == 0:
  │  │  │  ├─ trigger() → takeEffect.emit(effect, value)
  │  │  │  └─ interval = 原interval (重置)
  │  │  ├─ if expiration == 0:
  │  │  │  ├─ endone(idx) → removeBuff.emit(name, idx)
  │  │  │  └─ 移除该层
  │  │  └─ if 所有层都过期:
  │  │     └─ terminate() → terminateBuff.emit(name)
  │  │
  │  └─ BuffAlt.update()
  │     └─ 检查 expiration，到期时移除
  │
  └─ Signal: takeEffect(effect, value)
     ↓
     PetWidget / statusInterface 接收
     │
     ├─ if effect == "hp":
     │  ├─ pet_data.HP += value
     │  ├─ 检查 HP_tier 变化
     │  └─ Signal: hptier_changed
     │
     ├─ if effect == "fv":
     │  ├─ pet_data.FV += value
     │  ├─ 检查 FV_lvl 升级
     │  └─ Signal: fv_lvlup
     │
     ├─ if effect == "coin":
     │  ├─ pet_data.coins += value
     │  └─ Signal: coinUpdated
     │
     ├─ if effect == "HP_stop":
     │  ├─ settings.HP_stop = True
     │  └─ HP不再自动下降
     │
     └─ if effect == "FV_stop":
        ├─ settings.FV_stop = True
        └─ FV不再自动增加

Buff移除:
  Signal: removeBuff(name, idx) / terminateBuff(name)
     ↓
     BuffCard.remove_buff_widget(buff_id)
        ├─ 移除UI显示
        └─ 发送 rmBuff 信号
           ↓
           backpackInterface 更新物品数量
           statusInterface 更新Buff列表
```

---

## Part 3: 扩展与自定义高级指南

### 3.1 创建自定义Buff类型

```python
# 在 modules.py 中添加新类型

class BuffCustom(QObject):
    """自定义Buff: 改变宠物行为"""
    takeEffect = Signal(str, name="takeEffect")
    terminateBuff = Signal(str, name="terminateBuff")
    
    def __init__(self, name, config):
        super().__init__()
        self.name = name
        self.effect = config['effect']  # "speed_boost", "scale_change", etc
        self.value = config['value']
        self.expiration = config.get('expiration', None)
        self.timer = config['expiration']
    
    def update(self):
        if self.timer:
            self.timer -= 1
            if self.timer <= 0:
                self.terminate()
    
    def trigger(self):
        if self.effect == "speed_boost":
            # 增加宠物移动速度
            self.takeEffect.emit(self.effect, self.value)
        elif self.effect == "scale_change":
            # 改变宠物大小
            self.takeEffect.emit(self.effect, self.value)
    
    def terminate(self):
        self.terminateBuff.emit(self.name)

# 注册到 BuffThread

class BuffThread(QObject):
    def add_custom_buff(self, buff_config):
        buff = BuffCustom(buff_config['name'], buff_config)
        self.active_buffs.append(buff)
        buff.takeEffect.connect(self._handle_custom_effect)
        buff.terminateBuff.connect(self._handle_buff_end)
        return id(buff)
    
    def _handle_custom_effect(self, effect, value):
        if effect == "speed_boost":
            settings.pet_data.speed_boost = value
        elif effect == "scale_change":
            settings.scale_dict[settings.petname] = value
```

### 3.2 添加新的Dashboard面板

```python
# DyberPet/Dashboard/customUI.py

from qfluentwidgets import ScrollArea, ExpandLayout

class customInterface(ScrollArea):
    """自定义面板"""
    
    def __init__(self, sizeHintdb: tuple[int, int], parent=None):
        super().__init__(parent=parent)
        
        self.setObjectName("customInterface")
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)
        
        # 添加自定义组件
        self.customCard = CustomCard(self.scrollWidget)
        self.expandLayout.addWidget(self.customCard)
        
        self.__initWidget()
    
    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

# 在 DashboardUI.py 中注册

class DashboardMainWindow(FluentWindow):
    def initNavigation(self):
        # ... 现有代码
        
        self.customInterface = customInterface(...)
        self.addSubInterface(self.customInterface,
                           QIcon(...),
                           self.tr('Custom'))
```

### 3.3 创建新的宠物子种类 (SubPet)

```json
// res/role/{pet_name}/pet_conf.json

{
  "subpet": {
    "small_version": {
      "width": 64,
      "height": 72,
      "scale": 0.5,
      "follow_main_x": true,
      "follow_main_y": false,
      "anchor_to_main": [-50, 20],
      "fv_lock": 50
    }
  },
  "default": "default",
  "drag": "drag_action",
  ...
}
```

```python
# 在 Accessory.py 中

class SubPet(QWidget):
    """子宠物类"""
    setup_acc = Signal(dict, name='setup_acc')
    
    def __init__(self, acc_id, pet_name, pos_x, pos_y):
        super().__init__()
        self.acc_id = acc_id
        self.pet_name = pet_name
        self.position = QPoint(pos_x, pos_y)
        self.pet_config = PetConfig.init_config(pet_name, pic_dict)
        self.animation_worker = Animation_worker(self.pet_config)
        
        # 独立线程绘制
        self.thread = QThread()
        self.animation_worker.moveToThread(self.thread)
        self.thread.started.connect(self.animation_worker.run)
        self.thread.start()
```

### 3.4 自定义动作效果触发

```python
# 在 Act 类中添加自定义效果

class Act:
    def __init__(self, name, ...):
        self.name = name
        self.custom_effects = {}  # {time_offset: effect_func}
    
    def register_effect(self, frame_idx, effect_func):
        """在特定帧触发自定义效果"""
        self.custom_effects[frame_idx] = effect_func

# 在 PetWidget 中应用

def show_act(self, act_obj, duration):
    for frame_idx in range(len(act_obj.act_frames)):
        # ... 绘制帧
        
        if frame_idx in act_obj.custom_effects:
            effect_func = act_obj.custom_effects[frame_idx]
            effect_func(self)  # 触发效果，传递PetWidget实例

# 例: 敲脑门掉硬币

def add_coin_effect(pet_widget):
    coin_count = random.randint(5, 15)
    pet_widget.drop_item("coin", coin_count)

act_patpat = Act("patpat", ...)
act_patpat.register_effect(5, add_coin_effect)
```

---

## Part 4: 性能优化技巧

### 4.1 图片缓存策略

```python
# 在 PetWidget.setup_pet() 中

class ImageCache:
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size
        self.access_count = defaultdict(int)
    
    def get(self, key):
        if key in self.cache:
            self.access_count[key] += 1
            return self.cache[key]
        return None
    
    def put(self, key, pixmap):
        if len(self.cache) >= self.max_size:
            # LRU: 移除访问次数最少的
            least_used = min(self.access_count, key=self.access_count.get)
            del self.cache[least_used]
            del self.access_count[least_used]
        
        self.cache[key] = pixmap
        self.access_count[key] = 1

# 使用
cache = ImageCache()
pixmap = cache.get(frame_path)
if pixmap is None:
    pixmap = QPixmap(frame_path)
    cache.put(frame_path, pixmap)
```

### 4.2 动画帧优化

```python
# 预加载关键帧而非所有帧

class Act:
    def __init__(self, name, frame_paths, ...):
        self.name = name
        self.frame_paths = frame_paths  # 保存路径
        self.loaded_frames = {}  # 缓存加载的帧
    
    def get_frame(self, idx):
        if idx not in self.loaded_frames:
            # 延迟加载
            pixmap = QPixmap(self.frame_paths[idx])
            self.loaded_frames[idx] = pixmap.scaledToWidth(
                int(self.width * self.scale),
                Qt.SmoothTransformation
            )
        return self.loaded_frames[idx]
    
    def preload_frames(self, start, end):
        """预加载帧范围"""
        for i in range(start, min(end, len(self.frame_paths))):
            self.get_frame(i)
```

### 4.3 线程池优化

```python
# 使用QThreadPool而非单个QThread

from PySide6.QtCore import QThreadPool, QRunnable

class AnimationRunnable(QRunnable):
    def __init__(self, pet_conf):
        super().__init__()
        self.pet_conf = pet_conf
    
    def run(self):
        # Animation工作代码
        pass

pool = QThreadPool.globalInstance()
pool.setMaxThreadCount(4)

runnable = AnimationRunnable(pet_conf)
pool.start(runnable)
```

### 4.4 UI刷新优化

```python
# 使用脏矩形而非全屏重绘

class PetWidget(QWidget):
    def update_region(self, rect):
        """仅更新指定区域"""
        self.update(rect)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 仅绘制需要更新的区域
        region = event.region()
        
        for rect in region.rects():
            # 在 rect 内进行绘制
            self._draw_in_rect(painter, rect)
```

---

## Part 5: 调试与分析工具

### 5.1 性能分析

```python
# 添加性能监测

import time
from contextlib import contextmanager

@contextmanager
def timer(name):
    start = time.time()
    try:
        yield
    finally:
        elapsed = (time.time() - start) * 1000
        print(f"{name}: {elapsed:.2f}ms")

# 使用
with timer("animation frame"):
    render_frame()

# 输出: animation frame: 12.34ms
```

### 5.2 内存分析

```python
import tracemalloc

# 启用内存追踪
tracemalloc.start()

# ... 运行代码 ...

current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.1f} MB")
print(f"Peak: {peak / 1024 / 1024:.1f} MB")
tracemalloc.stop()
```

### 5.3 信号追踪

```python
# 添加信号拦截进行调试

original_emit = Signal.emit

def debug_emit(self, *args):
    print(f"Signal: {self} emitted with {args}")
    original_emit(self, *args)

Signal.emit = debug_emit
```

---

## Part 6: 完整示例：创建新功能

### 6.1 示例：宠物心情系统

**需求**：
- 宠物有不同心情：开心、生气、难过
- 心情影响动作选择和气泡内容
- 用户互动可改变心情

**实现步骤**：

1. **扩展 PetData**
```python
class PetData:
    def __init__(self):
        # ... 现有字段 ...
        self.mood = "happy"  # happy, angry, sad
        self.mood_points = 100  # 0-255
```

2. **扩展 conf.py**
```python
# 在 pet_conf.json 中添加
{
  "mood_config": {
    "happy": {
      "action_prob_mult": 1.5,      // 欢乐动作概率提升50%
      "move_speed_mult": 1.2        // 移动速度提升20%
    },
    "angry": {
      "action_prob_mult": 0.8,
      "move_speed_mult": 0.9
    },
    "sad": {
      "action_prob_mult": 0.5,
      "move_speed_mult": 0.7
    }
  }
}
```

3. **修改 Animation_worker**
```python
def _cal_prob(self, current_status):
    # ... 原有计算 ...
    
    # 应用心情倍数
    mood_mult = get_mood_multiplier(settings.pet_data.mood)
    new_prob = [p * mood_mult for p in new_prob]
    
    # ... 继续计算 ...
```

4. **添加心情气泡**
```python
# bubble_conf.json
{
  "mood_happy": {
    "message": "Life is beautiful! ♪",
    "icon": "favorite"
  },
  "mood_sad": {
    "message": "I'm feeling down...",
    "icon": "sad_face"
  }
}
```

5. **用户交互**
```python
class PetWidget(QWidget):
    def patpat(self):
        # ... 原有逻辑 ...
        
        # 改变心情
        settings.pet_data.mood_points += 10
        if settings.pet_data.mood_points > 200:
            new_mood = "happy"
        elif settings.pet_data.mood_points < 50:
            new_mood = "sad"
        else:
            new_mood = "normal"
        
        if settings.pet_data.mood != new_mood:
            settings.pet_data.mood = new_mood
            # 触发心情气泡
            bubble_manager.trigger_bubble(f"mood_{new_mood}")
```

6. **在 Dashboard 中显示**
```python
# statusUI.py
class MoodCard(SimpleCardWidget):
    def __init__(self):
        super().__init__()
        self.mood_label = QLabel()
        self.mood_bar = QProgressBar()
    
    def update_mood(self):
        mood = settings.pet_data.mood
        points = settings.pet_data.mood_points
        
        mood_text = {
            "happy": "😊 Happy",
            "normal": "😐 Normal",
            "sad": "😢 Sad"
        }
        
        self.mood_label.setText(mood_text[mood])
        self.mood_bar.setValue(points)
```

---

**文档版本**: v1.0-extended  
**最后更新**: 2026年3月17日  
适用于深度开发和扩展场景

