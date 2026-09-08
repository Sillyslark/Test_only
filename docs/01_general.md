# 1. 命名类别与基本原则

本项目同时包含 WS 官方规则概念，以及为了实现模拟器而建立的程序概念。

命名一个对象、变量、类型或流程前，应先确定它属于哪一类，再决定具体名称。

同一个英文词可能同时出现在不同规则类别中，因此不能仅根据单词本身判断其含义。程序命名应通过明确的类型、限定词或上下文消除歧义。

对于官方规则中已有明确名称的概念，原则上优先采用官方术语。

对于模拟器自行建立的程序概念，应使用能够明确表达其程序职责的名称，并避免与官方规则术语发生冲突。

### 1.1 命名类别总览

本项目中的概念分为七个主要领域：卡片、玩家、场地、游戏流程、能力与结算、玩家操作、模拟器基础设施。

| 领域 | 中文类别 | 官方概念 | 程序规范 | 主要用途 |
| --- | --- | --- | --- | --- |
| 卡片 | 卡片实例 | — | `Card` | 表示本局游戏中实际存在的一张卡 |
| 卡片 | 卡片定义 | Card Information | `CardDefinition` | 保存卡片自身的定义信息 |
| 卡片 | 卡片种类 | Type | `CardType` | 区分角色卡、事件卡和高潮卡 |
| 卡片 | 卡片状态 | State | `CardState` | 表示 Stand、Rest、Reverse 等状态 |
| 玩家 | 玩家 | Player | `Player` / `PlayerState` | 表示玩家及其当前游戏状态 |
| 玩家 | 所有者 | Owner | `owner` / `owner_id` | 表示卡片等对象的所有者 |
| 玩家 | 控制者 | Controller | `controller` / `controller_id` | 表示卡片、能力等对象当前的控制者 |
| 场地 | 区域 | Zone | `Zone` | 表示卡组、手牌、控制室、高潮区等规则区域 |
| 场地 | 舞台位置 | Stage Position | `StagePosition` | 表示五个舞台位置 |
| 游戏流程 | 阶段 | Phase | `Phase` | 表示回合中的主要阶段 |
| 游戏流程 | 子阶段 | Sub-Phase | 专用类型 | 表示阶段内部较大的流程划分 |
| 游戏流程 | 步骤 | Step | `Step` 或专用类型 | 表示阶段或子阶段内部的具体步骤 |
| 游戏流程 | 时点 | Timing | `Timing` 或专用结构 | 表示检查时点、玩家行动时点等 |
| 能力与结算 | 能力种类 | Ability Type | `AbilityType` | 区分【永】【自】【起】等能力 |
| 能力与结算 | 能力 | Ability | `Ability` | 表示卡片具有的一项完整能力 |
| 能力与结算 | 效果 | Effect | `Effect` | 表示能力等产生的实际效果 |
| 能力与结算 | 规则动作 | Rule Action | `RuleAction` | 表示由规则要求执行的处理 |
| 能力与结算 | 待结算项目 | 项目概念 | 待设计 | 表示已经产生但尚未完成结算的项目 |
| 能力与结算 | 后续流程 | 项目概念 | `Continuation` | 表示当前处理完成后继续执行的流程 |
| 玩家操作 | 合法操作 | 项目概念 | `LegalAction` / `Options` | 描述当前允许玩家执行的操作 |
| 玩家操作 | 玩家操作 | 项目概念 | `Action` | 表示提交给规则引擎的操作 |
| 玩家操作 | 选择 | Choice | `Choice` | 表示操作、效果或规则处理中需要作出的选择 |
| 模拟器基础设施 | 游戏状态 | 项目概念 | `GameState` | 保存当前整局游戏的状态 |
| 模拟器基础设施 | 游戏会话 | 项目概念 | `GameSession` | 接收操作并推动规则流程 |
| 模拟器基础设施 | 游戏事件 | 项目概念 | `GameEvent` | 记录游戏中已经发生的事实 |
| 模拟器基础设施 | Replay | 项目概念 | `Replay` | 保存并重放游戏输入或操作记录 |
| 模拟器基础设施 | 稳定标识 | 项目概念 | `..._id` | 跨操作、事件和 Replay 引用具体对象 |
| 模拟器基础设施 | 状态摘要 | 项目概念 | `StateHash` | 验证游戏状态及 Replay 的确定性 |

### 1.2 官方概念与项目概念

官方概念来自 WS 官方规则，例如 Type、Zone、Stage Position、Phase、Step、Ability、Effect、Rule Action 等。对于这些概念，原则上优先使用官方术语。

项目概念是为了实现模拟器而建立的软件抽象，例如 `Card`、`GameState`、`Action`、`Continuation`、`GameEvent`、`Replay` 等。项目概念不要求在官方规则中存在同名术语，但必须保持明确，并避免与官方术语冲突。

当项目概念与官方术语同名时，官方术语优先保留，项目概念增加限定词。例如：

```text
Event
→ 官方规则中的事件卡概念

GameEvent
→ 模拟器中已经发生的游戏事件
```

### 1.3 类别优先原则

命名时先确定所属类别，再确定具体名称。

例如 `climax`：

| 含义 | 所属类别 | 规范表达 |
| --- | --- | --- |
| 高潮卡这一卡片种类 | `CardType` | `CardType.CLIMAX` |
| 高潮区 | `Zone` | `Zone.CLIMAX_AREA` |
| 高潮阶段 | `Phase` | `Phase.CLIMAX` |
| 某一张具体高潮卡 | `Card` | `climax_card` |

### 1.4 定义与实例

程序中必须区分对象的定义与实际实例。

```text
CardDefinition
        │
        ├── Card #1
        ├── Card #2
        ├── Card #3
        └── Card #4
```

`CardDefinition` 描述“这是什么卡”；`Card` 表示“本局中的这一张实际卡”。

### 1.5 稳定标识

需要跨规则处理、操作、游戏事件、Replay 或序列化引用的具体对象，应具有稳定标识，原则上使用：

```python
..._id
```

例如：

```python
player_id
card_id
ability_id
```

现有 `instance_id` 是否迁移，留到对应章节单独审计。

### 1.6 操作、选择与游戏事件

应明确区分“当前能做什么”“实际提交了什么”“需要选择什么”“已经发生了什么”。

```text
LegalAction / Options
        ↓
      Action
        ↓
    规则引擎
        ↓
      Choice
        ↓
    GameEvent
```

`LegalAction` / `Options` 描述当前允许执行的操作；`Action` 是实际提交给 Engine 的操作；`Choice` 是执行过程中的玩家选择；`GameEvent` 是游戏中已经发生的事实。

`GameEvent` 不使用裸 `Event`，因为 Event 已经是 WS 官方卡片种类。

### 1.7 同名概念消歧原则

| 名称 | 含义一 | 含义二或其他含义 | 规范示例 |
| --- | --- | --- | --- |
| Event | 事件卡 | 游戏事件 | `CardType.EVENT` / `GameEvent` |
| Climax | 高潮卡 | 高潮区、高潮阶段 | `CardType.CLIMAX` / `Zone.CLIMAX_AREA` / `Phase.CLIMAX` |
| Clock | 计时区 | 计时阶段 | `Zone.CLOCK` / `Phase.CLOCK` |
| Level | 卡片等级 | 等级区 | `definition.level` / `Zone.LEVEL` |
| Stand | 竖置状态 | 重置阶段 | `CardState.STAND` / `Phase.STAND` |
| Trigger | 触发图标 | 触发步骤、能力触发等 | `TriggerIcon` / `AttackStep.TRIGGER` / `AbilityTrigger` |
| Damage | 伤害步骤 | 伤害处理 | `AttackStep.DAMAGE` / `damage_resolution` |
| State | 卡片状态 | 游戏状态、玩家状态 | `CardState` / `GameState` / `PlayerState` |
| Type | 卡片种类 | 能力种类等 | `CardType` / `AbilityType` |
| Action | 玩家操作 | 规则动作 | `Action` / `RuleAction` |
| Encore | 再演步骤 | 再演相关能力或处理 | 使用所属流程或能力类别明确区分 |

应尽量避免定义过于宽泛的裸类型名称，例如 `Type`、`State`、`Event`、`Trigger`、`Step`。

优先使用 `CardType`、`AbilityType`、`CardState`、`GameState`、`GameEvent`、`TriggerIcon`、`AbilityTrigger`、`AttackStep` 等能直接表达所属领域的名称。

### 1.8 官方术语优先原则

当项目概念与官方规则术语发生名称冲突时：

> 官方规则术语优先保留，项目概念增加限定词消除歧义。

例如官方使用 Event 表示事件卡，因此模拟器中的游戏事件使用 `GameEvent`。

### 1.9 后续章节的使用方式

后续各章节应先注明主要涉及的类别。例如：

```text
场地区域
规则类别：Zone、StagePosition
```

```text
卡片属性
规则类别：CardType、Card Information、CardState
```

```text
游戏流程
规则类别：Phase、Sub-Phase、Step、Timing
```

```text
能力与结算
规则类别：AbilityType、Ability、Effect、RuleAction
```

具体术语表再记录中文概念、官方英文名称、所属类别、规范程序名称、当前程序名称、UI 名称、状态和备注。

本节只负责建立分类体系与命名原则；具体迁移在后续章节逐项确定。
