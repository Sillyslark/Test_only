# WS 模拟器 · Pygame

本项目正在开发一个 **Weiß Schwarz（WS）规则模拟器**。

当前目标不是一次性实现全部卡牌效果，而是先建立稳定、可测试、可 Replay 的规则引擎基础，再逐步补全卡牌能力、各阶段操作和完整对局流程。

---

## 运行方式

在 `New_version` 目录运行：

```bash
python main.py
```

主要环境：

- Python 3.11
- Pygame
- Tkinter（目前仅用于 Replay 文件选择）

若缺少依赖：

```bash
python -m pip install -r requirements.txt
```

完整回归测试：

```bash
python -B -m unittest discover -s tests -v
```

开发时应优先运行当前功能对应的专项测试，再运行完整回归。

---

# 当前开发状态

当前已经建立的主要基础包括：

- Card Definition / Card Instance 分离
- Card JSON 加载
- Deck JSON 加载与卡组选择
- 卡组基础合法性验证
- Seed / Shuffle
- Mulligan
- 回合与阶段生命周期基础
- Stand Phase v1
- Draw Phase
- Clock Phase
- Main Phase 基础出牌
- Stage overlap
- Zone movement
- Resolution Zone（处理区）
- Damage Resolution
- Damage Cancel
- Level Up
- Deck Refresh
- Refresh Point
- Damage 中的特殊 Refresh / 败北边界
- Replay
- 状态 Hash
- Pygame UI
- `legal_actions()` 基础体系

尚未完整实现的主要部分：

- 角色 Stand / Rest / Reverse 朝向状态
- 完整 AUTO / Trigger / Pending Effect 系统
- Climax Phase 的实际使用规则
- Attack Phase
- Trigger Step
- Counter
- Stock 的完整规则
- Memory 的完整规则
- Climax 区完整规则
- 非零费用支付
- 完整胜负条件
- 正式玩家 Choice UI
- 完整卡牌能力系统

---

# 总体架构

项目当前逐步采用：

```text
Card / Deck JSON
        ↓
cards.py / deck_loader.py
        ↓
Application
        ↓
Action / legal_actions
        ↓
Session / Engine
        ↓
Rule Resolution
        ↓
GameState
        ↓
Application Snapshot
        ↓
Pygame UI
```

核心原则：

> Card 数据不属于 Engine。  
> Deck 构筑不属于 Engine。  
> UI 不直接修改比赛状态。  
> 玩家行为通过 Action 进入 Engine。  
> Engine 决定当前允许哪些操作。  
> 规则处理与玩家 Action 分离。  
> Replay 必须能够确定性重现比赛。

---

# 回合与阶段生命周期

当前正在将各阶段逐步迁移到统一生命周期。

基本模型为：

```text
Turn Start
↓
Phase Start
↓
处理阶段开始时点
↓
Phase Process
↓
执行该阶段本身的规则处理
↓
处理因此产生的规则 / 效果
↓
Player Action Window
↓
legal_actions()
↓
玩家 Action
↓
Phase End
↓
处理阶段结束时点
↓
Next Phase Start
```

当前已经实际接入的生命周期事件包括：

```text
turn_started
phase_started
phase_processed
action_window_opened
phase_ended
```

这些时点不仅用于当前流程，也为后续 AUTO 效果预留明确的触发位置。

例如未来可以区分：

```text
“你的回合开始时……”
“你的重置阶段开始时……”
“你的抽卡阶段结束时……”
```

它们不应被视为同一个时点。

## 玩家操作窗口

普通阶段操作只应在 Engine 到达稳定的 Player Action Window 后开放。

长期原则为：

```text
若存在尚未处理的强制规则 / AUTO
→ 不开放普通阶段操作

若存在需要玩家决定的效果
→ legal_actions 只开放对应 Choice

全部处理完成
→ 打开普通 Player Action Window
```

当前 AUTO 系统尚未完整实现，但阶段生命周期已经为其预留结构。

---

# 当前阶段实现

## Stand Phase / 重置阶段

当前流程：

```text
Turn Start
↓
Stand Phase Start
↓
Stand Phase Process
↓
Player Action Window
↓
玩家选择“进入抽卡阶段”
↓
Stand Phase End
↓
Draw Phase Start
```

重置阶段本身未来应执行：

```text
当前玩家舞台上的横置角色
↓
变为竖置
```

但目前尚未建立完整的 Stand / Rest / Reverse 卡牌朝向状态，因此 `_resolve_stand_phase()` 当前保留为空实现。

### Stand 的合法操作

当前只有：

```text
AdvancePhaseAction
→ 进入 Draw Phase
```

---

## Draw Phase / 抽卡阶段

当前流程：

```text
Draw Phase Start
↓
规则抽 1 张
↓
必要时处理中断规则
↓
Draw Phase Process 完成
↓
Player Action Window
↓
玩家选择“进入计时阶段”
↓
Draw Phase End
↓
Clock Phase Start
```

规则抽牌通过统一抽牌逻辑执行，因此如果抽牌过程中 Deck 为空，会正常接入 Refresh / Level Up 等中断处理。

已经测试的重要边界包括：

```text
Deck = 0
Waiting Room > 0
↓
先 Refresh
↓
再完成规则抽牌
```

以及：

```text
Clock = 6
Deck = 1
Waiting Room = 8
↓
抽最后 1 张
↓
Deck 为空
↓
Refresh
↓
Refresh Point → Clock
↓
Clock = 7
↓
Level Up
↓
完成后才进入 Draw Action Window
```

---

## Clock Phase / 计时阶段

计时阶段当前有两个规则选择：

```text
A. 跳过计时
   → 进入主要阶段

B. 选择当前玩家 1 张手牌
   → 该牌进入 Clock 顶部
   → 依次抽 2 张
```

第二种操作中的两次抽牌不是一个不可分割的批量动作。

实际结构为：

```text
手牌 → Clock
↓
Interrupt Checkpoint
↓
抽第 1 张
↓
Interrupt Checkpoint
↓
抽第 2 张
↓
Interrupt Checkpoint
```

因此 Level Up / Refresh 可以在这些原子步骤之间正常介入。

已经测试的复杂边界之一：

```text
初始：
Clock = 6
Deck = 1
Waiting Room = 8
Hand = 1

执行 ClockAction
↓
Hand → Clock
↓
Clock = 7
↓
Level Up
↓
抽第 1 张（原 Deck 最后一张）
↓
Deck 为空
↓
Refresh
↓
Refresh Point → Clock
↓
抽第 2 张
↓
ClockAction 完成
```

### ClockOptions

Clock Phase 使用 `ClockOptions` 描述当前玩家的操作空间：

```text
player_id
selectable_card_ids
can_skip
```

UI 因此能够知道：

- 当前哪些手牌可以作为 Clock 的选择对象
- 当前允许跳过 Clock
- “Clock 并抽 2 张”属于当前阶段的操作，即使玩家尚未选牌

---

# legal_actions

Engine 开始通过：

```python
session.legal_actions(player_id)
```

向 Application / UI 描述当前允许的玩家操作。

当前已经使用的 Options 包括：

```text
MulliganOptions
ClockOptions
```

以及具体 Action，例如：

```text
AdvancePhaseAction
MulliganAction
ClockAction
PlayCardAction
```

## Options 与 Action

两者职责不同。

例如 Mulligan：

```text
MulliganOptions
→ 告诉 UI：
   哪些手牌可以选择
   最少选择几张
   最多选择几张

MulliganAction
→ 玩家完成选择后真正提交给 Engine
```

Clock 同理：

```text
ClockOptions
→ 告诉 UI：
   当前合法手牌集合
   是否允许跳过

ClockAction
→ 玩家选定具体手牌后提交
```

这种结构避免 UI 自己重新实现规则判断。

---

# UI 与操作

当前正式 UI 为 Pygame UI。

旧 UI 已归档，不再作为当前规则开发的主要界面。

P2 在上、P1 在下：

```text
P2 后列
P2 前列
P1 前列
P1 后列
```

当前主要操作：

- 输入 Seed 开局，或随机新局
- Mulligan 中选择 0 至当前允许上限的手牌并确认
- Stand 中进入 Draw
- Draw 完成规则抽牌后进入 Clock
- Clock 可跳过，或选择 1 张手牌置入 Clock 后抽 2 张
- Main 中选择手牌和己方 Stage 位置进行出牌
- 点击部分区域查看完整区域顺序
- Replay 保存 / 载入
- `Esc` 清除当前选择

## UI 操作显示原则

当前采用：

```text
不属于当前阶段的操作
→ 隐藏

属于当前阶段，但尚缺少必要输入
→ 可以显示为 disabled

已经满足执行条件
→ 正常可用
```

例如 Clock Phase 始终显示：

```text
[跳过计时 → 主要阶段]

[将所选手牌置入计时区 → 抽 2 张]
```

未选择合法手牌时，第二个按钮为灰色不可用。

选择一张合法手牌后，该按钮变为可用。

这样玩家既能看到当前阶段有哪些规则选择，又不会提交非法 Action。

---

# Card Definition 与 Card Instance

卡牌的静态定义与比赛实例已经分离。

## Card Definition

描述一种实际卡牌的固定信息。

例如 Character 可以包含：

```text
编号
卡名
种类
颜色
等级
费用
力量
灵魂
特征
触发标记
```

Climax 与 Character 使用不同的数据结构，不为了兼容 Character 而人为添加角色专属字段。

## Card Instance

`Card` 表示一局比赛中实际存在的一张牌。

每个实例具有：

- `instance_id`
- `number`
- `definition`
- 未来的实例状态

因此即使多张牌具有同一个 `definition.code`，它们仍然是不同的比赛实例。

---

# 卡牌数据

卡牌静态数据使用 JSON 保存。

当前测试卡已经包括 Character 与 Climax 类型，例如：

```text
card/
└─ TEST/
   ├─ T-001.json
   └─ T-002.json
```

其中：

```text
T-001
→ Character 测试卡

T-002
→ Climax 测试卡
```

Python 代码负责：

```text
读取 JSON
↓
验证数据
↓
生成对应 CardDefinition
```

卡牌定义不重新硬编码进 Engine。

---

# 卡组数据

Deck 数据同样与 Engine 分离。

`deck_loader.py` 负责：

```text
读取 Deck JSON
↓
读取对应 Card JSON
↓
验证 Deck
↓
生成 CardDefinition
↓
生成 Card instances
↓
交给 Engine
```

当前已经建立纯 T-001 卡组以及包含 T-001 / T-002 的测试卡组，用于验证 Character / Climax 混合加载和后续伤害测试。

当前已经实现的基础 Deck 合法性包括：

```text
Deck 总数必须 = 50
Climax 数量不得超过 8
```

Engine 不负责决定一副 Deck 应包含哪些卡。

---

# Zone 与区域顺序

主要区域统一通过 `Zone` 表示，包括：

- Deck
- Hand
- Waiting Room
- Clock
- Stage
- Level
- Stock
- Memory
- Climax
- Resolution Zone

Stage 使用独立槽位结构。

## Resolution Zone / 处理区

Damage Resolution 已使用独立处理区。

处理区中的卡牌在伤害结算完成前不直接进入 Clock 或 Waiting Room。

这对于 Damage Cancel、Refresh 和特殊败北边界非常重要。

## Top / Bottom 统一约定

规则层和存储层统一采用：

```text
index 0 = Top
最后一个元素 = Bottom
```

这个约定适用于所有具有顺序意义的区域。

UI 可以为了视觉需求反向显示，但不能改变规则层的 Top / Bottom 定义。

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

多张移动原则上拆为：

```text
移动第 1 张
移动第 2 张
移动第 3 张
...
```

这样可以：

- 为每张牌产生明确事件
- 在规定的 Checkpoint 处理中断规则
- 让未来能力系统监听移动
- 保持 Replay 的确定性

但：

> 逐张移动不等于每移动一张都必须立即进行 Rule Check。

Checkpoint 由执行该动作的规则决定。

---

# Resolution 与规则处理

当前规则处理区分：

```text
Interrupt / 中断型规则
Resolution Point / 结算型规则
```

Stage overlap 已接入 Resolution Point。

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

Trigger / Ability 当前仍主要是基础结构和占位接口。

---

# Interrupt / 中断型规则

中断规则会暂停当前动作。

当前主要包括：

```text
Level Up
Refresh
```

基本结构：

```text
到达 Interrupt Checkpoint
↓
重新扫描当前成立的中断规则
↓
没有
    → 返回原动作

只有一个
    → 自动处理

多个同优先级
    → 玩家选择
↓
处理其中一个
↓
重新扫描当前状态
↓
直到没有中断规则
↓
恢复原动作
```

不能在第一次检查时缓存所有中断规则再依次执行。

因为一个中断规则的处理可能：

- 使另一个规则不再成立
- 使新的规则成立
- 改变后续处理顺序

---

# Level Up

当：

```text
Clock >= 7
```

时触发 Level Up。

候选范围为：

```text
Clock Bottom 起的 7 张
```

玩家从中选择 1 张进入 Level，其余 6 张进入 Waiting Room。

测试环境当前使用确定性默认选择，但 Engine 已为未来玩家 Choice 留出接口。

如果 Level Up 后：

```text
Clock >= 7
```

仍成立，则重新进行中断规则检查，因此可以连续升级。

---

# Deck Refresh

当：

```text
Deck 为空
Waiting Room 中存在卡牌
```

时触发 Refresh。

通常流程：

```text
Deck 为空
↓
中断当前流程
↓
Waiting Room → Deck
↓
Shuffle
↓
Deck Top → Clock
作为 Refresh Point
↓
重新进行中断规则检查
```

Refresh 使用比赛自身 RNG 时间线，保证 Replay 可以确定性重现洗牌结果。

---

# 同时成立的中断规则

Level Up 与 Refresh 可能同时成立。

例如：

```text
Deck = 0
Clock >= 7
Waiting Room > 0
```

Engine 不应简单把所有成立规则缓存后固定执行。

每处理一个中断规则后，都必须重新扫描当前状态。

当前测试已经覆盖不同处理顺序及其重新扫描行为。

---

# Damage Resolution

Damage 已经建立独立的 Resolution Zone 流程。

基本模型：

```text
受到 N 点伤害
↓
Deck Top 逐张 → Resolution Zone
↓
每张牌移动后处理必要的中断规则
↓
检查是否出现 Climax
```

如果没有 Climax：

```text
Damage Hit
↓
Resolution Zone 中的牌
按原顺序进入 Clock
```

如果出现 Climax：

```text
Damage Cancel
↓
完成当前伤害取消处理
↓
Resolution Zone → Waiting Room
```

## Resolution Zone 顺序

处理区本身具有顺序。

例如处理区从 Bottom → Top 为：

```text
1 2 3
```

原 Clock 为：

```text
4 5 6
```

Damage Hit 后应保持原伤害牌顺序，形成：

```text
4 5 6 1 2 3
```

而不是把处理区牌逆序加入 Clock。

---

# Damage 中的 Refresh

Damage 过程中 Deck 可能耗尽。

例如：

```text
Deck：
2 张非 Climax

Waiting Room：
8 张

Damage：
3
```

流程为：

```text
第 1 张 → Resolution
第 2 张 → Resolution
↓
Deck 为空
↓
Refresh
↓
Refresh Point → Clock
↓
继续原 Damage
↓
再取第 3 张 → Resolution
↓
继续 Damage Cancel / Hit 判定
```

也就是说：

> Refresh 会中断 Damage，但不会丢失尚未完成的 Damage 进度。

---

# Damage 中 Deck 与 Waiting Room 同时为空

已经针对规则书 9.2.2.1 对应的特殊边界进行了实现和测试。

核心区别在于：

```text
Deck 为空
Waiting Room 为空
```

发生时：

- 是否正在进行 Damage Resolution
- Resolution Zone 中是否存在 Climax

这些条件会影响 Refresh 是否结束、Damage 是否继续以及是否立即败北。

当前测试已经覆盖：

- Damage 中无 Climax 时的特殊败北
- Climax 已进入 Resolution Zone 时先完成取消
- Damage 结束后再次遇到无法 Refresh 时的败北
- 特殊败北后不再继续产生后续 Damage / Refresh / Level Up 状态修改
- 特殊败北时 Resolution Zone 保留状态
- Replay / state hash 对 Resolution Zone 的一致性

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
Damage 内部处理
```

不会伪装成玩家 Action 写入 Action Log。

它们应由原始 Action 重新执行时确定性产生。

Replay 已覆盖：

```text
规则处理
随机 Refresh
Resolution Zone
状态 Hash
Replay 后继续游戏
```

等一致性问题。

`resolution_zone` 已纳入当前状态，并为旧 Replay / hash 版本保留兼容处理。

---

# 测试体系

测试统一放在：

```text
tests/
```

规则测试不应依赖已经归档的旧 UI。

当前测试重点包括：

- 开局
- Seed / Shuffle
- Mulligan
- Deck Loader
- Deck Choice
- Card Definition
- Turn
- Stand Phase
- Draw Phase
- Clock Phase
- Play
- Stage overlap
- Zone movement
- Card conservation
- Move atomicity
- Damage
- Damage Cancel
- Resolution Zone
- Level Up
- 连续 Level Up
- Refresh
- Refresh Point
- Level Up + Refresh
- Interrupt 选择与重新扫描
- Replay
- Application boundary

## 阶段专项测试原则

阶段逐步使用独立专项测试。

例如：

```text
test_turn_stand_phase.py

Turn Start
↓
Stand Start
↓
Stand Process
↓
Stand Action Window
↓
Stand End
↓
Draw Start
```

测试到下一阶段的 **Start 边界** 即停止，不测试下一阶段内部规则。

同理：

```text
test_turn_draw_phase.py

Draw Start
↓
规则抽牌
↓
Draw Action Window
↓
Draw End
↓
Clock Start
```

以及：

```text
test_turn_clock_phase.py

Clock Start
↓
Clock Action Window
↓
Skip / ClockAction
↓
Clock End
↓
Main Start
```

这种划分避免一个测试文件同时承担多个阶段的规则责任。

---

# UI 与规则层边界

UI 持有 Application 提供的独立快照。

所有比赛操作仍通过：

```text
Application
↓
Action
↓
Session / Engine
```

完成。

UI 不直接修改：

- Deck
- Hand
- Clock
- Waiting Room
- Stage
- Level
- Stock
- Memory
- Climax
- Resolution Zone

当前正在进一步将 UI 的按钮显示和可选对象迁移到 `legal_actions()`。

未来玩家 Choice 预计采用：

```text
Engine 请求 Choice
↓
Waiting for Choice
↓
legal_actions / choice options
↓
UI 展示
↓
玩家提交 Choice
↓
Engine 恢复 Resolution
```

而不是让 Engine 直接依赖 Pygame 弹窗。

---

# 下一步方向

当前 Stand → Draw → Clock 已经开始使用统一阶段生命周期和合法操作体系。

接下来可以继续沿两个方向推进：

## 阶段与 Action 系统

继续整理：

```text
Main Phase
Climax Phase
Attack Phase
End Phase
```

使各阶段逐步统一为：

```text
Phase Start
→ Phase Process
→ Action Window
→ legal_actions
→ Phase End
```

## AUTO / Trigger 系统

在阶段生命周期稳定后，将已有 Trigger / Pending Effect 基础结构逐步扩展为真正的能力结算系统。

需要支持：

```text
回合开始时
阶段开始时
阶段处理中
阶段结束时
卡牌移动时
伤害取消时
伤害命中时
```

等触发时点，并区分：

```text
强制执行
玩家选择是否执行
玩家选择对象
多个效果的处理顺序
```

---

# 项目目录原则

主要结构：

```text
card/
    卡牌静态定义

deck/
    卡组定义

tests/
    自动测试

cards.py
    卡牌数据结构与 Card JSON 加载

deck_loader.py
    Deck JSON 加载、验证和 Card instance 构建

zones.py
    区域定义与区域访问

engine.py
    GameState、Session 与主要流程

rule_resolution.py
    规则处理

resolution.py
    Resolution / Interrupt 等结算基础设施

actions.py
    Options 与玩家 Action

application.py
    应用层边界

ui/
    当前 UI 与归档 UI
```

所有开发文件位于 `New_version`。

`Old_version` 仅供参考。
