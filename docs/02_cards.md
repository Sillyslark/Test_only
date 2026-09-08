# 2. 卡片

本节用于统一卡片本身相关概念的命名。

**主要类别：**

- `Card`
- `CardDefinition`
- `CardType`
- Card Information
- `CardOrientation`
- `CardFaceState`

本节只确定卡片相关概念、名称和边界，不直接要求修改现有代码。

信息公开范围不在本节定义。它与区域、卡片正反面以及特殊规则共同有关，将在场地区域章节中单独讨论。

---

## 2.1 卡片定义与卡片实例

卡片需要区分“某一种卡的固定定义”和“本局游戏中实际存在的一张卡”。

```text
CardDefinition
        │
        ├── Card #1
        ├── Card #2
        ├── Card #3
        └── Card #4
```

### 2.1.1 卡片定义

**类别：`CardDefinition`**

`CardDefinition` 表示某一种卡自身的固定定义。

它保存属于卡片本身的信息，不应因为卡片在游戏中的移动、方向变化、正反面变化或结算过程而改变。

根据卡片种类不同，`CardDefinition` 可能包含以下 Card Information：

- 卡名
- 卡片种类
- 颜色
- 等级
- 费用
- 力量
- 灵魂
- 特征
- 图标
- 触发图标
- 卡片文本
- 卡片编号

当前代码已经存在：

```python
CharacterDefinition
ClimaxDefinition
CardDefinition
AnyCardDefinition
```

其中当前 `CardDefinition` 实际是 `CharacterDefinition` 的兼容别名，并不能完整代表所有卡片种类，因此这一部分标记为待整理。

| 中文概念 | 规范程序名称 | 当前程序名称 | 状态 | 备注 |
| --- | --- | --- | --- | --- |
| 通用卡片定义 | `CardDefinition` | 当前为 `CharacterDefinition` 的兼容别名 | 待整理 | 最终应表达所有卡片定义的共同概念 |
| 角色卡定义 | `CharacterDefinition` | `CharacterDefinition` | 已确认 | 角色卡具有专用信息 |
| 事件卡定义 | `EventDefinition` | 尚未实现 | 待实现 | 实现事件卡时加入 |
| 高潮卡定义 | `ClimaxDefinition` | `ClimaxDefinition` | 已确认 | — |
| 任意卡片定义 | 待设计 | `AnyCardDefinition` | 待设计 | 最终结构在卡片数据模型整理时决定 |

命名目标是：

> `CardDefinition` 表示“卡片定义”这一总概念；具体卡片种类可以拥有自己的专用定义结构，但不应让 `CardDefinition` 只代表角色卡。

### 2.1.2 卡片实例

**类别：`Card`**

`Card` 表示本局游戏中实际存在的一张卡。

即使两张卡引用同一个 `CardDefinition`，它们仍然是两个不同的 `Card`，可以独立存在于不同区域，并具有不同的运行时状态。

当前代码：

```python
@dataclass(frozen=True)
class Card:
    instance_id: str
    number: int
    definition: AnyCardDefinition
    face_up: bool = True
```

当前 `Card` 这一名称本身没有歧义，可以继续作为卡片实例的规范类型名。

| 中文概念 | 规范程序名称 | 当前程序名称 | 状态 | 备注 |
| --- | --- | --- | --- | --- |
| 卡片实例 | `Card` | `Card` | 已确认 | 表示本局实际存在的一张卡 |
| 引用的卡片定义 | `definition` | `definition` | 已确认 | 指向该卡对应的卡片定义 |
| 卡片稳定标识 | `card_id` | `instance_id` | 待检查 | 是否迁移留到基础设施整理时决定 |
| 调试副本编号 | 待检查 | `number` | 待检查 | 项目调试信息，不属于官方卡片信息 |
| 卡片正反面状态 | `face_state` | `face_up` | 待迁移 | 使用 `CardFaceState` 明确表达 |

---

## 2.2 卡片种类

**类别：`CardType`**

官方规则使用 Type 表示卡片种类。

WS 有三种基本卡片种类：

1. Character
2. Event
3. Climax

程序中统一使用 `CardType` 表示“卡片种类”这一类别，避免使用过于宽泛的 `Type` 或 `kind`。

规范形式：

```python
CardType.CHARACTER
CardType.EVENT
CardType.CLIMAX
```

当前代码主要使用：

```python
kind == "character"
kind == "climax"
```

卡片 JSON 也使用：

```json
{
    "kind": "character"
}
```

因此：

| 中文概念 | 规范程序名称 | 当前程序名称 | UI 名称 | 状态 |
| --- | --- | --- | --- | --- |
| 卡片种类字段 | `card_type` | `kind` | 卡片种类 | 待迁移 |
| 角色卡 | `CardType.CHARACTER` | `"character"` | 角色卡 | 待迁移 |
| 事件卡 | `CardType.EVENT` | 尚未完整实现 | 事件卡 | 待实现 |
| 高潮卡 | `CardType.CLIMAX` | `"climax"` | 高潮卡 | 待迁移 |

这里的 `Event` 专门表示官方事件卡种类。

模拟器内部“已经发生的游戏事件”使用：

```python
GameEvent
```

不得使用裸 `Event` 与事件卡概念混淆。

---

## 2.3 卡片信息

**类别：Card Information**

卡片定义中保存具有规则意义或识别意义的卡片信息。

| 中文概念 | 官方名称 | 规范字段名 | 当前字段名 | 状态 | 备注 |
| --- | --- | --- | --- | --- | --- |
| 卡名 | Card Name | `name` | `name` | 已确认 | — |
| 卡片种类 | Type | `card_type` | `kind` | 待迁移 | 使用 `CardType` |
| 颜色 | Color | `color` | `color` | 已确认 | — |
| 特征 | Trait | `traits` | `traits` | 已确认 | 一张卡可以有多个特征 |
| 等级 | Level | `level` | `level` | 已确认 | 角色卡和事件卡使用 |
| 费用 | Cost | `cost` | `cost` | 已确认 | 角色卡和事件卡使用 |
| 图标 | Icon | `icons` | 尚未实现 | 待实现 | 使用 `CardIcon` 表示普通卡片图标 |
| 力量 | Power | `power` | `power` | 已确认 | 仅角色卡拥有 |
| 灵魂 | Soul | `soul` | `soul` | 已确认 | 仅角色卡拥有 |
| 触发图标 | Trigger Icon | `trigger_icons` | `trigger_marks` | 待迁移 | 使用独立的 `TriggerIcon` 类型 |
| 卡片文本 | Card Text | `card_text` | 尚未实现 | 待实现 | 卡面记载的规则文本；能力的结构化表示留到能力章节 |
| 卡片编号 | Collection ID | `collection_id` | `code` | 待检查 | 确认真实卡片数据含义后再决定 |

### 2.3.1 特征

官方规则概念使用 Trait。

程序字段使用：

```python
traits
```

而不是：

```python
trait
```

因为一张卡可以同时具有多个特征。

因此：

```text
官方概念：Trait
程序字段：traits
UI 名称：特征
```

### 2.3.2 各卡片种类拥有的信息

不同 `CardType` 并不拥有完全相同的 Card Information。

程序模型应区分“该信息不存在”和“该信息存在但数值为 0”。例如高潮卡并不是 `power = 0`，而是根本没有 Power 这一 Card Information。

下表中的“✓”表示该 Card Type 具有这一类 Card Information，并不表示每一张该种类卡都必须具有非空值；“可能有”表示该类信息只在具有相应标记的卡片上存在。

| 卡片信息 | Character | Event | Climax |
| --- | :---: | :---: | :---: |
| `name` | ✓ | ✓ | ✓ |
| `card_type` | ✓ | ✓ | ✓ |
| `color` | ✓ | ✓ | ✓ |
| `traits` | ✓ | — | — |
| `level` | ✓ | ✓ | — |
| `cost` | ✓ | ✓ | — |
| `icons` | 可能有 | 可能有 | — |
| `power` | ✓ | — | — |
| `soul` | ✓ | — | — |
| `trigger_icons` | 依卡片而定 | 依卡片而定 | 依卡片而定 |
| `card_text` | ✓ | ✓ | ✓ |
| `collection_id` | ✓ | ✓ | ✓ |

具体定义结构不应为了统一字段而给不具有某项信息的卡片填入虚假的 `0`、空值或默认规则值。

### 2.3.3 图标与触发图标

普通 Icon 与 Trigger Icon 是两类不同的 Card Information，应在程序中保持独立。

官方规则名称为 `Icon`。项目程序类型使用限定名称 `CardIcon`，用于与 `TriggerIcon` 以及其他可能出现的界面图标等概念消歧；这属于项目命名限定，不改变官方术语本身。

普通卡片图标使用：

```python
class CardIcon(Enum):
    ...
```

对应字段：

```python
icons: tuple[CardIcon, ...]
```

触发图标使用独立类型：

```python
class TriggerIcon(Enum):
    ...
```

对应字段：

```python
trigger_icons: tuple[TriggerIcon, ...]
```

当前代码使用：

```python
trigger_marks
```

后续应迁移为 `trigger_icons`。

因此命名关系固定为：

```text
CardIcon
→ 普通卡片图标的类别

icons
→ 一张卡拥有的普通卡片图标

TriggerIcon
→ 触发图标的类别

trigger_icons
→ 一张卡拥有的触发图标
```

虽然两者名称中都包含 `Icon`，但类型名和字段名均有明确限定，不应在审计时将 `CardIcon` 与 `TriggerIcon` 视为同一概念。

不得使用裸 `trigger` 表示触发图标，因为 `trigger` 后续还可能用于触发步骤、触发条件以及能力触发等概念。

### 2.3.4 卡片文本

Card Text 是卡片上记载的规则文本，主要供玩家阅读。

规范字段：

```python
card_text
```

可以把它理解为卡面上的自然语言规则描述，但不应把 `card_text` 本身等同于程序中的 Ability 或 Effect。

概念边界为：

```text
Card Text
→ 卡片上写了什么

Ability
→ 规则引擎如何结构化表示卡片能力

Effect
→ 能力在规则处理中产生或要求执行的效果
```

因此未来的数据模型可能同时存在：

```text
CardDefinition
├── card_text
└── 结构化能力数据
```

但结构化能力数据最终使用什么类型和字段名，本节不决定，留到能力与效果章节统一设计。

当前已经存在的 `TriggeredEffect` 是结算时点基础设施中的临时占位结构，也不应与 `card_text` 混为同一概念。

### 2.3.5 卡片编号

卡片定义上的识别编号与本局中的卡片稳定标识必须区分。

规范候选：

```python
collection_id
```

当前代码：

```python
code
```

是否正式迁移，需要先确认项目未来导入真实卡片数据时，该字段是否完全对应官方 Collection ID。

因此当前状态为“待检查”。

---

## 2.4 卡片方向

**类别：`CardOrientation`**

卡片方向用于表示舞台上的角色卡处于何种方向。

规范类型：

```python
class CardOrientation(Enum):
    STAND = "stand"
    REST = "rest"
    REVERSE = "reverse"
```

规范值：

```python
CardOrientation.STAND
CardOrientation.REST
CardOrientation.REVERSE
```

| 中文概念 | 规范程序名称 | UI 名称 | 状态 |
| --- | --- | --- | --- |
| 竖置 | `CardOrientation.STAND` | 竖置 | 待实现 |
| 横置 | `CardOrientation.REST` | 横置 | 待实现 |
| 倒置 | `CardOrientation.REVERSE` | 倒置 | 待实现 |

实例字段规范为：

```python
orientation
```

`CardOrientation` 是适用于 Stage 上 Character 的规则状态。当前规则下，其他区域中的 Card 不具有该状态。

这里的方向属于处于 Stage Position 上的 Character，而不是 Stage Position 自身的属性。

其他区域中的卡片不应为了数据结构统一而被强行赋予 Stand、Rest 或 Reverse。

规范字段语义使用：

```python
orientation
```

概念上允许：

```python
orientation: CardOrientation | None
```

这里确定的是字段的命名与语义，并不提前规定运行时状态必须直接存储在当前 `Card` dataclass 中。具体状态存储结构留到实现相关规则时决定。

其中：

```text
舞台上的角色卡
→ STAND / REST / REVERSE

其他不适用方向规则的卡片
→ None
```

`CardOrientation` 只回答：

> 这张卡当前处于 Stand、Rest 还是 Reverse？

它不表示卡片正面或背面朝上。

---

## 2.5 卡片正反面状态

**类别：`CardFaceState`**

卡片正反面状态与 `CardOrientation` 是两个独立概念。

规范类型：

```python
class CardFaceState(Enum):
    FACE_UP = "face_up"
    FACE_DOWN = "face_down"
```

规范值：

```python
CardFaceState.FACE_UP
CardFaceState.FACE_DOWN
```

规范字段语义为：

```python
face_state
```

这里确定的是字段的命名与语义，并不提前规定运行时状态必须直接存储在当前 `Card` dataclass 中。具体状态存储结构留到实现相关规则时决定。

因此：

```python
card.face_state == CardFaceState.FACE_UP
card.face_state == CardFaceState.FACE_DOWN
```

比当前：

```python
face_up: bool
```

更明确，也避免 `not card.face_up` 一类不够直观的表达。

| 中文概念 | 规范程序名称 | 当前程序名称 | 状态 |
| --- | --- | --- | --- |
| 卡片正反面状态 | `CardFaceState` | `face_up: bool` | 待迁移 |
| 正面朝上 | `CardFaceState.FACE_UP` | `face_up == True` | 待迁移 |
| 背面朝上 | `CardFaceState.FACE_DOWN` | `face_up == False` | 待迁移 |
| 实例字段 | `face_state` | `face_up` | 待迁移 |

### 2.5.1 与卡片方向的关系

`CardOrientation` 与 `CardFaceState` 必须保持独立。

例如舞台上的角色卡可以表示为：

```text
FACE_UP + STAND
FACE_UP + REST
FACE_UP + REVERSE
```

这里：

```text
CardOrientation
→ 描述卡片方向

CardFaceState
→ 描述卡片哪一面朝上
```

不得使用一个统一的 `CardState` 同时表示这两个概念。

### 2.5.2 与区域规则的关系

`CardFaceState` 保存的是具体卡片当前实际的正反面状态。

某个区域通常以哪一面放置卡片，属于区域规则，而不是 `CardFaceState` 类型本身的定义。

例如当前已经明确会存在：

```text
通常正面朝上的区域
通常背面朝上的区域
允许因规则或效果改变正反面的区域
```

这些默认规则将在场地区域章节中定义。

同样，玩家是否有权查看一张卡的信息，也不由 `CardFaceState` 单独决定。

因此本节不建立 `Visibility` 或 `InformationVisibility` 类型。

---

## 2.6 卡片稳定身份

**类别：稳定标识**

对局中每一张 `Card` 必须能够被稳定引用。

该标识会用于：

- Action
- Choice
- GameEvent
- Replay
- 状态比较
- 调试

第一节规定稳定标识原则上使用：

```python
..._id
```

因此卡片稳定标识的规范候选为：

```python
card_id
```

当前代码使用：

```python
instance_id
```

这里暂时不立即决定迁移，因为 `instance_id` 已经广泛参与现有操作、测试和 Replay。

必须区分：

```text
card_id
→ 本局中的某一张具体卡

collection_id
→ 卡片定义上的卡片编号
```

例如：

```text
CardDefinition.collection_id = "T-001"

Card.card_id = "P1-T001-03"
```

前者回答“这是什么卡”，后者回答“这是本局里的哪一张卡”。

---

## 2.7 当前命名审计摘要

| 当前名称 | 规范候选 | 类别 | 状态 | 原因 |
| --- | --- | --- | --- | --- |
| `kind` | `card_type` | `CardType` | 待迁移 | 使用明确类别名 |
| `"character"` | `CardType.CHARACTER` | `CardType` | 待迁移 | 避免裸字符串 |
| `"climax"` | `CardType.CLIMAX` | `CardType` | 待迁移 | 与高潮区、高潮阶段消歧 |
| `trigger_marks` | `trigger_icons` | `TriggerIcon` | 待迁移 | 使用 Trigger Icon |
| `code` | `collection_id` | Card Information | 待检查 | 先确认真实数据语义 |
| `instance_id` | `card_id` | 稳定标识 | 待检查 | Replay 影响较大 |
| `number` | 待检查 | 项目调试信息 | 待检查 | 不属于官方卡片信息 |
| `face_up` | `face_state` | `CardFaceState` | 待迁移 | 明确表达正反面状态 |
| `CardDefinition = CharacterDefinition` | 重新整理通用 `CardDefinition` | 卡片定义 | 待整理 | 当前兼容别名不能代表全部卡片种类 |
| `AnyCardDefinition` | 待设计 | 卡片定义 | 待设计 | 等统一定义模型确定后处理 |

---

## 2.8 本节暂不决定的内容

以下内容暂不提前锁死：

1. `CardDefinition` 最终采用何种数据结构。
2. `AnyCardDefinition` 是否继续保留。
3. `instance_id` 是否迁移为 `card_id`。
4. `code` 是否迁移为 `collection_id`。
5. 卡片能力（Ability）与效果（Effect）的数据结构。
6. Card Text 与结构化能力数据之间的映射或解析方式。
7. Event 卡的具体定义结构。
8. 区域的信息公开规则。
9. 特殊效果造成的信息公开变化。
10. 完整卡片数据库中的非核心规则字段。

---

## 2.9 本节命名结论

当前可以确定的规范方向：

```python
Card
CardDefinition
CharacterDefinition
EventDefinition
ClimaxDefinition

CardType.CHARACTER
CardType.EVENT
CardType.CLIMAX

CardIcon
TriggerIcon

name
card_type
color
traits
level
cost
icons
power
soul
trigger_icons
card_text

CardOrientation.STAND
CardOrientation.REST
CardOrientation.REVERSE
orientation          # 规范字段语义，存储位置待实现时决定

CardFaceState.FACE_UP
CardFaceState.FACE_DOWN
face_state           # 规范字段语义，存储位置待实现时决定
```

以下名称保持待检查：

```python
card_id
collection_id
```

信息公开范围以及各区域默认的正反面规则，留到场地区域章节统一定义。
