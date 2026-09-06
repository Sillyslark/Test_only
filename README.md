# WS 模拟器 · Pygame v15

在 `New_version` 目录运行：

```bash
python main.py
```

依赖 Python 3.11、Pygame、Tkinter（仅用于 Replay 文件选择）。

若缺少 Pygame：

```bash
python -m pip install -r requirements.txt
```

---

## 项目目标

本项目正在开发一个 WS（Weiß Schwarz）规则模拟器。

当前开发重点是将：

- 游戏状态
- 区域移动
- 回合流程
- 规则处理
- 中断结算
- Replay
- UI

相互分离，使规则层能够独立测试，并为后续卡牌能力、伤害、攻击等复杂结算提供统一基础。

---

## 界面与操作

原始视觉稿 `ui/pygame/pygame_stage_grid_mock_v15.py` 保持原样，新适配器 `ui/pygame/app.py` 复用其中央几何布局。

P2 在上、P1 在下：

```text
P2 后列
P2 前列
P1 前列
P1 后列
```

对应位置对齐。

沿用：

- 150 像素正方形网格
- 15 像素间距
- 107×150 纵向卡框
- 整体随窗口缩放
- 网格边缘不绘制

最右列集中放置操作确认、种子输入、Replay、区域顺序和最近记录。左列保留空白。

当前基本操作：

- 点击种子框，`Ctrl+A` 清空后输入整数，点击按种子开局；也可随机新局。
- 中央手牌可选择，右侧确认换牌。先手、后手依次操作，允许选择 0 张。
- 换牌结束进入先手第 1 回合。
- 右侧按钮推进重置、抽卡、计时、主要、高潮、攻击、结束阶段。
- 结束阶段完成后切换当前玩家。
- 抽卡阶段从 Deck 顶部抽 1 张。
- 计时阶段选择一张己方手牌执行 Clock：该牌进入 Clock 顶部，然后依次抽 2 张。每回合一次，也可跳过。
- 主要阶段选择一张己方手牌，再选择己方 Stage 位置并确认出牌。
- 对已占用 Stage 位置出牌时，旧卡会先通过规则处理进入 Waiting Room。
- 点击部分区域可在右侧查看完整区域顺序。
- 手牌单行最多显示 7 张，通过左右箭头浏览。
- `Esc` 清除手牌及 Stage 目标选择。
- Replay 保存和载入使用系统文件选择窗口。

---

# 数据结构

## Card Definition 与 Card Instance

卡牌的“定义”和一局比赛中的“实例”已经分离。

### Card Definition

描述某一种实际卡牌，例如：

```text
T-001
测试
黄色
0级
0费
500力量
1灵魂
```

卡牌定义不再由 `CardDefinition` 的默认值隐式生成，而是从实际卡牌数据文件加载。

### Card Instance

`Card` 表示比赛中实际存在的一张牌。

每个实例具有：

- `instance_id`
- `number`
- `definition`
- 当前朝向等实例状态

因此即使两张牌都是 T-001，它们仍然是两个不同的比赛实例。

`instance_id` 与卡牌编号 `definition.code` 是不同概念。

---

# 卡牌数据

卡牌静态数据使用 JSON 保存。

当前目录结构：

```text
card/
└─ TEST/
   └─ T-001.json
```

当前测试角色：

```text
编号：T-001
卡名：测试
种类：character
颜色：yellow
等级：0
费用：0
力量：500
灵魂：1
特征：无
触发标记：无
```

Python 规则代码负责读取 JSON，并生成相应的 `CardDefinition`。

因此：

```text
JSON
负责卡牌静态数据

Python
负责数据加载、规则验证和游戏逻辑
```

卡牌定义不应重新硬编码到 Engine 中。

---

# 卡组数据

卡组同样开始与 Engine 分离。

当前目录结构：

```text
deck/
└─ TEST/
   └─ Test_All_T_001.json
```

当前测试卡组：

```text
Test_All_T_001

T-001 × 50
```

`deck_loader.py` 负责：

```text
读取 Deck JSON
↓
读取对应 Card JSON
↓
生成 CardDefinition
↓
生成比赛中的 Card instances
↓
交给 Engine
```

Engine 不负责决定某副卡组包含哪些卡。

也就是说，Engine 只负责：

```text
加载指定 Deck
↓
生成比赛实例
↓
洗牌
↓
开始比赛
```

而不是：

```text
Engine 内部硬编码 50 张 T-001
```

---

# Zone 与区域顺序

当前主要区域统一使用 `Zone` 表示，包括：

- Deck
- Hand
- Waiting Room
- Clock
- Stage
- Level
- Stock
- Memory
- Climax

Stage 使用独立槽位结构。

## Top / Bottom 统一约定

规则层和存储层统一采用：

```text
index 0 = Top
最后一个元素 = Bottom
```

这个约定适用于所有有顺序的区域。

例如：

```python
zone[0]
```

始终表示该区域顶部。

UI 可以根据实际视觉需求反向显示，但：

> **UI 的显示方向不得改变规则层和存储层的 Top / Bottom 定义。**

例如 Hand 可以在 UI 中显示为：

```text
最早获得 → 最晚获得
左                右
```

即使 UI 进行了反向排列，底层数据顺序仍遵守统一的 Top-first 规则。

---

# 卡牌移动

区域间移动统一通过：

```python
_move_card()
```

处理。

它负责：

- 来源区域验证
- 目标区域验证
- 指定卡牌查找
- 顺序维护
- Stage slot
- 移动原子性
- `card_moved` Event

非法移动必须在改变游戏状态之前失败。

## 多张牌移动

原则上，多张牌的区域移动拆成：

```text
移动第 1 张
移动第 2 张
移动第 3 张
...
```

而不是直接对区域 list 进行批量修改。

这样可以保证：

- 每张牌移动都有明确事件
- 中断规则可以在规定的检查点介入
- 后续能力系统可以监听移动时点
- Replay 更容易保持确定性

但“逐张移动”不等于“每移动一张都一定立即处理中断”。

是否产生 Rule Checkpoint 由上层规则决定。

---

# Resolution

规则处理目前区分：

```text
中断型规则处理
Resolution Point / 结算型规则处理
```

## Resolution Point

Stage overlap 已接入 Resolution Point 模型。

例如：

```text
角色进入已有角色的 Stage slot
↓
原子移动完成
↓
Resolution Point
↓
处理 Stage overlap
↓
旧角色进入 Waiting Room
↓
收集同一时点产生的 Trigger
↓
处理 Pending Effects
↓
原动作继续
```

Trigger / Ability 系统目前只有基础结构和占位接口，完整卡牌能力尚未实现。

---

# 中断型规则

中断规则会暂停当前动作。

当前已经实现：

```text
Level Up
Refresh
```

中断规则统一通过中断检查循环处理。

基本结构：

```text
到达 Interrupt Checkpoint
↓
收集当前所有成立的中断规则
↓
没有
    → 返回原动作

只有一个
    → 自动处理

多个同优先级规则
    → 玩家选择
↓
处理一个中断规则
↓
重新扫描当前游戏状态
↓
直到没有需要处理的中断规则
↓
恢复原动作
```

不能在第一次检查时缓存所有规则然后依次执行。

因为处理一个规则可能改变其他规则是否仍然成立，也可能产生新的中断规则。

---

# Level Up

当：

```text
Clock >= 7
```

时触发 Level Up。

候选牌固定为：

```text
Clock Bottom 起的 7 张
```

玩家从这 7 张中选择 1 张进入 Level。

其余 6 张进入 Waiting Room。

测试环境中当前默认选择：

```text
从 Bottom 起第 1 张
```

但 Engine 已保留玩家选择接口。

如果 Level Up 完成后：

```text
Clock >= 7
```

仍然成立，则重新触发 Level Up。

因此 Clock 中存在 14 张及以上卡牌时可以连续升级。

---

# Deck Refresh

当 Deck 为空且 Waiting Room 中存在卡牌时触发 Refresh。

流程：

```text
Deck 为空
↓
中断当前流程
↓
Waiting Room → Deck
逐张移动
↓
Shuffle
↓
Deck Top → Clock
作为 Refresh Point
↓
重新进行中断规则检查
```

刷新使用比赛自身的 RNG 时间线。

洗牌前恢复当前 `rng_state`，洗牌完成后保存新的 `rng_state`，保证 Replay 可以确定性重现。

---

# 同时发生的中断规则

Level Up 与 Refresh 当前属于同一优先级。

例如：

```text
Deck = 1
Clock = 6
Waiting Room > 0
```

执行：

```text
Deck Top → Clock
```

后：

```text
Deck = 0
Clock = 7
```

此时同时成立：

```text
Level Up
Refresh
```

不能由 Engine 写死处理顺序。

Engine 会调用中断规则选择接口，由玩家决定先处理哪一个。

测试环境默认：

```text
Refresh first
```

但测试也已经确认：

```text
Level Up first
```

同样能够正确执行。

每处理完一个中断规则后必须重新扫描当前状态。

---

# 原子步骤与 Interrupt Checkpoint

连续动作应拆成明确的原子步骤。

例如 Clock 阶段的“抽 2”：

```text
抽第 1 张
↓
Interrupt Checkpoint
↓
若需要：
Refresh
Level Up
其他中断规则
↓
全部处理中断
↓
抽第 2 张
```

因此：

```text
draw 2
```

在实现上不是不可分割的批量操作。

这也是后续 Damage、能力效果和其他多张牌移动的基础。

---

# Replay

Replay 记录：

- Seed
- Config
- Mulligan
- Phase
- Clock
- Play
- 其他玩家 Action
- 逐步状态 Hash

规则处理，例如：

```text
Level Up
Refresh
Stage overlap
```

不会伪装成玩家 Action 写入 Action Log。

它们由原始 Action 重新执行时确定性产生。

Refresh 已进行专门 Replay 测试：

```text
触发 Refresh
↓
保存 Replay
↓
重新执行 Replay
↓
Deck 顺序一致
rng_state 一致
Events 一致
GameState 一致
```

并且恢复后的比赛继续执行多个 Action，原局与 Replay 局仍保持一致。

因此 Refresh 使用的随机过程属于比赛确定性状态的一部分。

---

# 当前测试重点

当前自动测试已经覆盖：

- 开局
- Seed 与 Shuffle
- Mulligan
- 回合推进
- Draw
- Clock
- Play
- Stage overlap
- Zone movement
- Card conservation
- Move atomicity
- Level Up
- 连续 Level Up
- Refresh
- Refresh Point
- Level Up + Refresh 同时成立
- 中断规则选择
- 中断重新扫描
- 非法中断选择原子性
- 中断边界
- Replay
- Refresh Replay
- Replay 后继续执行的确定性
- Application boundary

开发过程中修改规则层后应优先运行相关测试，再运行：

```bash
python -B -m unittest discover -v
```

进行完整回归。

---

# UI 与规则层边界

UI 只持有独立快照。

所有比赛操作仍应通过：

```text
Application
↓
Action
↓
Session / Engine
```

完成。

UI 不应直接修改：

- Deck
- Hand
- Clock
- Waiting Room
- Stage
- Level
- Stock
- Memory
- Climax

等规则状态。

当前玩家选择接口，例如：

```text
Level Up 选牌
多个中断规则选择
```

在测试环境中使用确定性默认选择。

未来接入正式 UI 后，应逐步发展为：

```text
Engine 请求 Choice
↓
进入 Waiting for Choice 状态
↓
UI 展示选择
↓
玩家提交 Choice
↓
Engine 恢复 Resolution
```

而不是让规则层直接依赖 Pygame 弹窗。

---

# 尚未完成

目前尚未完整实现：

- 卡牌能力系统
- Trigger / Pending Effect 的完整结算
- 攻击流程
- Trigger Step
- Counter
- Damage Resolution
- Damage Cancel
- Climax 卡完整规则
- Stock 规则
- Memory 规则
- Climax 区规则
- 非零费用支付
- Level 4 / 败北处理
- 胜负判定
- 正式玩家选择 UI

---

# 下一步计划

## Climax 卡

计划增加：

```text
card/TEST/T-002.json
```

定义：

```text
编号：T-002
卡名：测试CX
种类：climax
颜色：yellow
触发标记：无
```

Climax 卡与 Character 卡具有不同的数据结构。

高潮卡本身只需要：

- 卡名
- 卡牌编号
- 颜色
- 触发标记

不应为了兼容 Character 而人为添加：

```text
level
cost
power
soul
traits
```

等角色专属属性。

## 测试卡组

随后建立新的测试 Deck：

```text
T-001 × 42
T-002 × 8
```

并开始实现 Deck 合法性验证。

当前已经确定的第一批合法性规则：

```text
Deck 总数必须 = 50
Climax 数量不得超过 8
```

暂不擅自加入尚未确定的其他构筑限制。

## Damage Resolution

完成 Climax 类型后开始实现 Damage。

Damage 将用于进一步验证：

```text
逐张移动
Interrupt Checkpoint
Refresh
Level Up
Climax / Damage Cancel
Resolution
Replay
```

之间的组合行为。

---

# 项目目录原则

当前逐步采用：

```text
card/
    卡牌静态定义

deck/
    卡组定义

cards.py
    Python 卡牌数据结构与 Card JSON 加载

deck_loader.py
    Deck JSON 加载、验证和 Card instance 构建

zones.py
    区域定义与区域访问

engine.py
    比赛状态与主要流程

rule_resolution.py
    规则处理

resolution.py
    Resolution / Interrupt 等结算基础设施

actions.py
    玩家 Action

application.py
    应用层边界

ui/
    UI
```

核心原则：

> Card 数据不属于 Engine。  
> Deck 构筑不属于 Engine。  
> UI 不直接修改比赛状态。  
> 所有区域顺序在规则/存储层统一采用 Top-first。  
> 多张移动原则上逐张执行。  
> 中断规则在明确的 Interrupt Checkpoint 处理。  
> 每处理一个中断规则后重新扫描游戏状态。  
> Replay 必须能够确定性重现规则处理和随机过程。

---

所有开发文件位于 `New_version`。

`Old_version` 仅供参考。