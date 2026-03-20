# ClawPet 文档导航与索引

> 🎯 **快速开始**: 如果这是你第一次阅读，请先读这份文件的导航部分，然后选择相应的文档。

---

## 📚 文档总览

你的项目现在包含以下设计文档：

| 文档 | 大小 | 目标读者 | 阅读时间 | 用途 |
|------|------|---------|---------|------|
| **DESIGN_DOCUMENT.md** ⭐⭐⭐ | ~8K | 所有人 | 60min | 📖 全面了解系统架构 |
| **ARCHITECTURE_DEEP_DIVE.md** ⭐⭐ | ~5K | 深度开发者 | 45min | 🔬 深度技术分析 |
| **DEVELOPER_CHEATSHEET.md** ⭐ | ~4K | 日常开发 | 15min | ⚡ 快速查询 |
| **README_NAV.md** (本文件) | ~2K | 新手 | 5min | 🗺️ 导航与索引 |

---

## 🎯 根据你的需求选择文档

### 「我想快速上手」

**推荐路径**:
1. 阅读本文件的"项目结构速览"部分
2. 查看 DEVELOPER_CHEATSHEET.md 中的"关键类与方法速查"
3. 运行项目，对照代码和文档理解

**预计时间**: 20 分钟

---

### 「我想完全理解整个系统」

**推荐路径**:
1. 从头开始读 DESIGN_DOCUMENT.md 的第1-4章
2. 理解架构图（第2章）
3. 阅读各个核心模块的详细内容（第3章）
4. 阅读UI设计和交互流程（第4-5章）

**预计时间**: 60-90 分钟

---

### 「我想深度扩展系统」

**推荐路径**:
1. 先阅读 DESIGN_DOCUMENT.md 的第8-9章（扩展点和自定义指南）
2. 学习 ARCHITECTURE_DEEP_DIVE.md 的"扩展与自定义高级指南"（第3章）
3. 对照源码实现你的扩展
4. 参考"完整示例"（Part 6）

**预计时间**: 120 分钟

---

### 「我在开发过程中遇到问题」

**推荐方案**:
1. 使用 DEVELOPER_CHEATSHEET.md 中的"常见问题排查"（第8章）
2. 查找相关的类或方法（使用第二章的速查表）
3. 在 DESIGN_DOCUMENT.md 中找到对应模块的详细说明
4. 参考"调试与维护"章节（DESIGN_DOCUMENT.md 第10章）

---

## 🗺️ 项目结构速览

### 核心模块（必读）

```
ClawPet/
├── ClawPet.py          ⭐ PetWidget 主宠物窗口
│                        📖 → DESIGN_DOCUMENT.md 3.2
│
├── modules.py           ⭐ Animation_worker, Buff系统
│                        📖 → DESIGN_DOCUMENT.md 3.3-3.8
│
├── conf.py              ⭐ PetConfig, Act, PetData等
│                        📖 → DESIGN_DOCUMENT.md 3.4
│
├── settings.py          ⭐ 全局设置
│                        📖 → DESIGN_DOCUMENT.md 3.5
│
├── Accessory.py         配件系统
│                        📖 → DESIGN_DOCUMENT.md 3.7
│
├── bubbleManager.py     气泡消息系统
│                        📖 → DESIGN_DOCUMENT.md 3.6
│
└── Dashboard/           ⭐ 仪表板UI模块
    ├── DashboardUI.py   主窗口
    ├── statusUI.py      状态面板
    ├── inventoryUI.py   背包面板
    ├── shopUI.py        商店面板
    ├── taskUI.py        任务面板
    └── buffModule.py    Buff管理
                         📖 → DESIGN_DOCUMENT.md 4.1
```

### 数据文件结构

```
data/
├── pet_data.json        🔴 宠物游戏存档（最重要）
│                        📖 → DESIGN_DOCUMENT.md 3.4.3
│
├── settings.json        用户设置
├── act_data.json        动作解锁状态
└── task_data.json       任务数据

res/
├── role/{pet}/          宠物资源
│   ├── pet_conf.json    🔴 宠物配置
│   ├── act_conf.json    🔴 动作配置
│   └── action/          动作帧图片
│                        📖 → DESIGN_DOCUMENT.md 4.2

└── icons/
    ├── bubble_conf.json 气泡配置
                         📖 → DESIGN_DOCUMENT.md 3.6
```

---

## 📖 文档内容索引

### DESIGN_DOCUMENT.md 目录

| 章节 | 内容 | 适合 |
|------|------|------|
| 第1章 | 项目概述 | 所有人 |
| 第2章 | 整体架构 | 架构师、高级开发 |
| 第3章 | 核心模块设计 | 核心功能开发 |
| 第4章 | UI/UX设计 | UI开发、设计师 |
| 第5章 | 数据流与交互 | 业务逻辑开发 |
| 第6章 | 系统配置与常数 | 配置优化、平衡 |
| 第7章 | 关键特性深入 | 理解游戏机制 |
| 第8章 | 扩展点与自定义 | 新功能开发 |
| 第9章 | 性能与优化 | 性能优化 |
| 第10章 | 调试与维护 | 问题排查 |
| 第11章 | 打包与部署 | 发布流程 |

---

### ARCHITECTURE_DEEP_DIVE.md 目录

| Part | 内容 | 深度 |
|------|------|------|
| Part 1 | 詳細架構圖解 | ⭐⭐⭐ |
| Part 2 | 核心系統詳解 | ⭐⭐⭐ |
| Part 3 | 擴展與自定義 | ⭐⭐ |
| Part 4 | 性能優化技巧 | ⭐⭐ |
| Part 5 | 調試與分析工具 | ⭐⭐ |
| Part 6 | 完整示例：新功能 | ⭐ |

---

### DEVELOPER_CHEATSHEET.md 目录

| 章节 | 内容 | 查询速度 |
|------|------|--------|
| 第1章 | 项目结构速查 | ⚡⚡⚡ |
| 第2章 | 关键类与方法 | ⚡⚡⚡ |
| 第3章 | 全局设置速查 | ⚡⚡⚡ |
| 第4章 | JSON配置格式 | ⚡⚡⚡ |
| 第5章 | 常用操作速查 | ⚡⚡⚡ |
| 第6章 | 特殊函数速查 | ⚡⚡ |
| 第7章 | Dashboard速查 | ⚡⚡ |
| 第8章 | Q&A排查表 | ⚡⚡ |
| 第9章 | 开发工作流 | ⚡ |
| 第10章 | 代码片段库 | ⚡ |

---

## 🔍 按主题查找

### 我想学习...

<details>
<summary><b>宠物动画系统</b></summary>

- **基础**: DESIGN_DOCUMENT.md 3.3 + 3.4.2
- **深度**: ARCHITECTURE_DEEP_DIVE.md Part 2.4
- **实践**: DEVELOPER_CHEATSHEET.md 5.5

#### 核心问题:
- 如何播放动作? → sec 5.5
- 动作概率如何计算? → ARCHITECTURE_DEEP_DIVE.md section 2.2
- 如何添加新动作? → DESIGN_DOCUMENT.md 8.1 + DEVELOPER_CHEATSHEET.md 9.1

</details>

<details>
<summary><b>Buff增益系统</b></summary>

- **基础**: DESIGN_DOCUMENT.md 3.3.2, 3.8 + 3.1.2 (DP_HpBar)
- **深度**: ARCHITECTURE_DEEP_DIVE.md Part 2.3
- **实践**: DEVELOPER_CHEATSHEET.md 5.3, 6.1

#### 核心问题:
- Buff如何工作? → DESIGN_DOCUMENT.md 3.3.2
- 如何创建自定义Buff? → ARCHITECTURE_DEEP_DIVE.md 3.1
- Buff代码示例? → DEVELOPER_CHEATSHEET.md 快速代码片段库

</details>

<details>
<summary><b>HP与好感度系统</b></summary>

- **基础**: DESIGN_DOCUMENT.md 3.4.3 + 7.1-7.2
- **深度**: ARCHITECTURE_DEEP_DIVE.md Part 2.1-2.2
- **实践**: DEVELOPER_CHEATSHEET.md 5.2, 5.7

#### 核心问题:
- HP如何自动下降? → DESIGN_DOCUMENT.md 7.5
- FV等级如何升级? → DESIGN_DOCUMENT.md 7.5
- HP分级的含义? → sec 3.2

</details>

<details>
<summary><b>UI与Dashboard系统</b></summary>

- **基础**: DESIGN_DOCUMENT.md 4.1-4.3
- **深度**: ARCHITECTURE_DEEP_DIVE.md Part 1.2
- **实践**: DEVELOPER_CHEATSHEET.md 7 + 9.2

#### 核心问题:
- Dashboard如何连接各个面板? → DESIGN_DOCUMENT.md 4.1.1
- 如何添加新Dashboard面板? → ARCHITECTURE_DEEP_DIVE.md 3.2

</details>

<details>
<summary><b>宠物配置与初始化</b></summary>

- **基础**: DESIGN_DOCUMENT.md 3.4.1 + 5.1
- **实践**: DEVELOPER_CHEATSHEET.md 4.1-4.3

#### 核心问题:
- 如何创建新宠物? → DESIGN_DOCUMENT.md 8.1
- pet_conf.json如何写? → DEVELOPER_CHEATSHEET.md 4.1

</details>

<details>
<summary><b>物品与消耗品系统</b></summary>

- **基础**: DESIGN_DOCUMENT.md 5.3
- **实践**: DEVELOPER_CHEATSHEET.md 5.6

#### 核心问题:
- 如何添加新物品? → DEVELOPER_CHEATSHEET.md 9.2

</details>

<details>
<summary><b>气泡消息系统</b></summary>

- **基础**: DESIGN_DOCUMENT.md 3.6
- **实践**: DEVELOPER_CHEATSHEET.md 5.4

#### 核心问题:
- 如何触发气泡? → DESIGN_DOCUMENT.md 3.6.1
- bubble_conf.json格式? → DEVELOPER_CHEATSHEET.md 4.4

</details>

<details>
<summary><b>信号与事件系统</b></summary>

- **基础**: DESIGN_DOCUMENT.md 2.1-2.3 + 5.2-5.5
- **参考**: DEVELOPER_CHEATSHEET.md 快速代码片段库 part 3

#### 核心问题:
- 信号如何连接? → DESIGN_DOCUMENT.md 4.1.1
- 所有信号列表? → DEVELOPER_CHEATSHEET.md 第6章

</details>

<details>
<summary><b>性能优化</b></summary>

- **基础**: DESIGN_DOCUMENT.md 9
- **深度**: ARCHITECTURE_DEEP_DIVE.md Part 4-5

#### 核心问题:
- 如何优化性能? → ARCHITECTURE_DEEP_DIVE.md 4.1-4.4
- 性能指标目标? → DESIGN_DOCUMENT.md 9.4

</details>

---

## 🚀 快速查询指南

### 我想查询...

<details>
<summary><b>某个类的完整API</b></summary>

例：PetWidget 类

1. 打开 DESIGN_DOCUMENT.md 3.2
2. 查看"关键方法"表格
3. 在 DEVELOPER_CHEATSHEET.md 2.1 中查询信号列表
4. 对照源码 `ClawPet/ClawPet.py` 查看实现

</details>

<details>
<summary><b>某个JSON配置的格式</b></summary>

1. 打开 DEVELOPER_CHEATSHEET.md 第4章
2. 查找相应的"模板"子章节
3. 对照 `res/` 中的实际文件示例

</details>

<details>
<summary><b>某个功能如何实现</b></summary>

例：如何让宠物移动

1. 在 DEVELOPER_CHEATSHEET.md 8 Q&A 搜索关键词
2. 找不到→ 查 DESIGN_DOCUMENT.md 按章节查找
3. 查找函数实现→ 对照源码文件

</details>

<details>
<summary><b>某个配置参数的含义</b></summary>

例：pet_conf.json 中的 interact_speed

1. 打开 DESIGN_DOCUMENT.md 3.4.1
2. 查看 PetConfig 的"核心属性"表格
3. 找到 interact_speed 的描述

</details>

<details>
<summary><b>某个Bug如何排查</b></summary>

1. 打开 DEVELOPER_CHEATSHEET.md 第8章 Q&A 表
2. 查找相似问题
3. 按照"解决方案"列的步骤操作
4. 仍未解决→ 参考 DESIGN_DOCUMENT.md 第10章

</details>

---

## 🎓 学习路径建议

### 初级开发者（第一次接触项目）

**周期**: 1 周

- Day 1: 读 DEVELOPER_CHEATSHEET.md 快速上手
- Day 2: 运行项目，修改简单参数（scale、colors等）
- Day 3: 读 DESIGN_DOCUMENT.md 第1-2章
- Day 4: 在 DEVELOPER_CHEATSHEET.md 中查找相关操作
- Day 5: 完成第一个小功能修改（如改变HP初始值）
- Day 6-7: 读 DESIGN_DOCUMENT.md 第3-4章，理解深度

---

### 中级开发者（需要添加新功能）

**周期**: 2-3 周

- Week 1: 快速阅读全部文档（获得全景图）
- Week 2: 深入学习你要修改的模块，对照源码
- Week 2-3: 实现功能，遇到问题查文档或源码

**学习重点**:
- DESIGN_DOCUMENT.md 第8-9章
- ARCHITECTURE_DEEP_DIVE.md Part 3-4
- DEVELOPER_CHEATSHEET.md 快速参考

----

### 高级开发者（系统级优化和架构调整）

**周期**: 1 周集中 + 持续学习

- Day 1-2: 深入阅读 ARCHITECTURE_DEEP_DIVE.md 全部内容
- Day 2-3: 对照源码理解关键的 Signal 连接
- Day 3-4: 分析性能瓶颈（DESIGN_DOCUMENT.md 9 + ARCHITECTURE 4-5）
- Day 5+: 实施优化和架构改进

---

## 📋 常用查询表

### 信号连接速查

```python
# 问: 如何让某个操作触发某个效果？
# 答: 查看 DEVELOPER_CHEATSHEET.md 第6章的 Signal 表
# 或参考 DESIGN_DOCUMENT.md 5 中的数据流图

# 例: 物品使用
backpackInterface.use_item_inven → 触发物品效果
statusInterface.addBuff → 应用Buff
```

### 代码位置速查

| 功能 | 文件 | 类 |
|------|------|-----|
| 宠物显示 | ClawPet.py | PetWidget |
| 动画管理 | modules.py | Animation_worker |
| Buff系统 | modules.py | BuffAdd, BuffAlt, BuffThread |
| 气泡消息 | bubbleManager.py | BubbleManager |
| 仪表板 | Dashboard/DashboardUI.py | DashboardMainWindow |
| 状态面板 | Dashboard/statusUI.py | statusInterface |
| 背包面板 | Dashboard/inventoryUI.py | backpackInterface |

---

## 🎯 推荐阅读顺序

### 情景1：我要快速修改一个参数

```
DEVELOPER_CHEATSHEET.md (第3章)
        ↓
settings.py 查看默认值
        ↓
修改并运行测试
```
**时间**: 5-10分钟

---

### 情景2：我要添加一个新动作

```
DEVELOPER_CHEATSHEET.md 9.1 (工作流)
        ↓
DESIGN_DOCUMENT.md 8.1 (详细步骤)
        ↓
准备帧文件 + 编辑JSON
        ↓
运行并测试
```
**时间**: 30分钟

---

### 情景3：我要创建一个新Buff

```
DESIGN_DOCUMENT.md 3.3.2 (基础)
        ↓
ARCHITECTURE_DEEP_DIVE.md 3.1 (实现)
        ↓
DEVELOPER_CHEATSHEET.md 快速代码片段 (示例)
        ↓
编码 + 测试
```
**时间**: 1-2小时

---

### 情景4：我要优化某个系统

```
DESIGN_DOCUMENT.md 9 (性能考虑)
        ↓
ARCHITECTURE_DEEP_DIVE.md 4 (优化技巧)
        ↓
分析、优化、测试、验证性能改进
```
**时间**: 4-8小时

---

## 📞 文档问题反馈

如果你发现文档中有：
- ❌ 错误信息
- ❓ 不清楚的描述
- 🔗 断掉的连接
- 💭 缺少的内容

请在项目中记录，以便下次更新时修正。

---

## ✅ 文档完整性检查清单

确保文档涵盖了项目的所有方面：

- ✅ 项目概述和版本信息
- ✅ 完整的系统架构图
- ✅ 所有核心模块的详细说明
- ✅ UI/UX 设计文档
- ✅ 数据流和交互流程
- ✅ JSON 配置文件格式
- ✅ 扩展和定制指南
- ✅ 性能优化建议
- ✅ 调试和维护指南
- ✅ 常见问题排查表
- ✅ 代码片段示例
- ✅ 快速参考表
- ✅ 学习路径建议
- ✅ 文档导航索引

---

**最后更新**: 2026年3月17日  
**文档版本**: v1.0  
**适用项目版本**: ClawPet v0.7.7+

