# 2. 卡片

本节用于统一卡片本身相关概念的命名。

**主要类别：**

- `Card`
- `CardDefinition`
- `CharacterDefinition`
- `EventDefinition`
- `ClimaxDefinition`
- `CardType`
- `CardColor`
- Card Information
- `CardIcon`
- `TriggerIcon`
- `CardOrientation`
- `CardFaceState`

本节确定卡片相关概念、名称、基础数据模型方向和边界。具体代码迁移按本节规范逐步进行。

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

它保存属于卡片本身的基础 / 印刷 Card Information，不应因为卡片在游戏中的移动、方向变化、正反面变化、持续效果、临时效果或结算过程而改变。

三种具体卡片定义统一从 `CardDefinition` 派生：

```text
CardDefinition
├── CharacterDefinition
├── EventDefinition
└── ClimaxDefinition
```

规范结构方向：

```python
@dataclass(frozen=True)
class CardDefinition:
    card_number: str
    name: str
    color: CardColor
    trigger_icons: tuple[TriggerIcon, ...]

    card_type: ClassVar[CardType]
```

具体卡片定义：

```python
@dataclass(frozen=True)
class CharacterDefinition(CardDefinition):
    card_type: ClassVar[CardType] = CardType.CHARACTER

    level: int
    cost: int
    power: int
    soul: int
    traits: tuple[str, ...]
    card_icons: tuple[CardIcon, ...]
```

```python
@dataclass(frozen=True)
class EventDefinition(CardDefinition):
    card_type: ClassVar[CardType] = CardType.EVENT

    level: int
    cost: int
    card_icons: tuple[CardIcon, ...]
```

```python
@dataclass(frozen=True)
class ClimaxDefinition(CardDefinition):
    card_type: ClassVar[CardType] = CardType.CLIMAX
```

这里的 `card_type` 由具体 Definition 类型固定，而不是创建对象时任意传入的普通实例字段。

因此不得出现：

```text
CharacterDefinition
+
card_type = CardType.CLIMAX
```

这样的矛盾状态。

卡片 JSON 中仍然可以保存用于 Loader 判别的卡片种类字段；Loader 根据该字段决定实例化 `CharacterDefinition`、`EventDefinition` 或 `ClimaxDefinition`。实例化完成后，Python 对象的 `card_type` 由其具体类型保证。

当前代码已经存在：

```python
CharacterDefinition
ClimaxDefinition
CardDefinition
AnyCardDefinition
```

其中当前：

```python
CardDefinition = CharacterDefinition
```

只是早期兼容结构，不能代表三种卡片定义的共同概念，应在本轮卡片数据模型整理中迁移。

正式公共 `CardDefinition` 建立后，原则上可以直接用：

```python
definition: CardDefinition
```

表达“任意卡片定义”。因此 `AnyCardDefinition` 不再是长期必要抽象；迁移期间是否临时保留兼容别名，根据现有引用决定。

| 中文概念 | 规范程序名称 | 当前程序名称 | 状态 | 备注 |
| --- | --- | --- | --- | --- |
| 通用卡片定义 | `CardDefinition` | 当前为 `CharacterDefinition` 的兼容别名 | 待迁移 | 成为三种具体 Definition 的共同基类 |
| 角色卡定义 | `CharacterDefinition` | `CharacterDefinition` | 已确认 | 具有角色卡专用信息 |
| 事件卡定义 | `EventDefinition` | 尚未实现 | 待实现 | 本轮卡片模型整理时加入 |
| 高潮卡定义 | `ClimaxDefinition` | `ClimaxDefinition` | 已确认 | — |
| 任意卡片定义 | `CardDefinition` | `AnyCardDefinition` | 待迁移 | 公共基类建立后原则上不再需要 |

命名目标是：

> `CardDefinition` 表示“卡片定义”这一总概念；具体卡片种类拥有各自适用的 Card Information，不应通过给不适用的字段填入 `0`、`None` 或空值来强行统一结构。

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

Card 实例还需要能够确定其官方规则意义上的 `Owner`。

规范字段：

```python
owner_id
```

`owner_id` 表示该 Card 在本局中的固定拥有者。它由游戏开始时该 Card 属于哪名 Player 的 Deck 决定，并在该局中保持不变。

因此，即使某张 P1 拥有的 Card 因规则或效果进入 P2 的 Zone：

```text
owner_id
→ 仍然是 P1
```

Card 的 `Master` 不应被当作另一个固定归属字段与 `owner_id` 等同处理。对于位于 Zone 中的 Card，应依据当前所在 Zone 的 Master 规则确定 Card Master。

Ability 与 Effect 的 Master 留到能力与效果章节按官方规则分别定义。

| 中文概念 | 规范程序名称 | 当前程序名称 | 状态 | 备注 |
| --- | --- | --- | --- | --- |
| 卡片实例 | `Card` | `Card` | 已确认 | 表示本局实际存在的一张卡 |
| 引用的卡片定义 | `definition` | `definition` | 已确认 | 指向该卡对应的卡片定义 |
| 卡片稳定标识 | `card_id` | `instance_id` | 待检查 | 是否迁移留到基础设施整理时决定 |
| 卡片所有者 | `owner_id` | 尚未实现 | 待实现 | 本局固定 Owner，不因 Zone、Master 或 Player Control 改变 |
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
| 卡片种类 | Type | `card_type` | `kind` | 待迁移 | 使用 `CardType`，由具体 Definition 类型固定 |
| 颜色 | Color | `color: CardColor` | `color: str` | 待迁移 | 当前支持黄、绿、红、蓝 |
| 特征 | Trait | `traits` | `traits` | 已确认 | 一张 Character 可以有多个特征 |
| 等级 | Level | `level` | `level` | 已确认 | Character / Event |
| 费用 | Cost | `cost` | `cost` | 已确认 | Character / Event |
| 图标 | Icon | `card_icons` | 尚未实现 | 待实现 | `CardIcon.COUNTER` / `CardIcon.CLOCK` |
| 力量 | Power | `power` | `power` | 已确认 | 仅 Character |
| 灵魂 | Soul | `soul` | `soul` | 已确认 | 仅 Character |
| 触发图标 | Trigger Icon | `trigger_icons` | `trigger_marks` | 待迁移 | 可为空、单个、复数或重复 |
| 卡片文本 | Card Text | 由结构化 Ability / Effect 渲染 | 尚未实现 | 待后续实现 | 不作为独立手写规则真相 |
| 卡片编号 | Card Number | `card_number` | `code` | 待迁移 | 保存完整 Card Number |

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

程序模型必须区分：

```text
该 Card Information 不存在
```

与：

```text
该 Card Information 存在，但内容为空或数值为 0
```

例如：

```text
Character.power = 0
→ Character 具有 Power，基础值为 0

Climax
→ 根本没有 Power 这一 Card Information
```

当前规范：

| 卡片信息 | Character | Event | Climax |
| --- | :---: | :---: | :---: |
| `card_number` | ✓ | ✓ | ✓ |
| `name` | ✓ | ✓ | ✓ |
| `card_type` | ✓ | ✓ | ✓ |
| `color` | ✓ | ✓ | ✓ |
| `traits` | ✓ | — | — |
| `level` | ✓ | ✓ | — |
| `cost` | ✓ | ✓ | — |
| `card_icons` | ✓ | ✓ | — |
| `power` | ✓ | — | — |
| `soul` | ✓ | — | — |
| `trigger_icons` | ✓ | ✓ | ✓ |

其中“✓”表示该 Card Type 具有这一类 Card Information，并不表示其内容必须非空。

因此：

```python
character.card_icons == ()
event.card_icons == ()
```

表示 Character / Event 具有 Icon 这一 Card Information，但该卡没有 Counter / Clock Icon。

而：

```text
ClimaxDefinition
→ 不存在 card_icons
```

表示 Climax 根本不具有这一 Card Information。

同理：

```python
definition.trigger_icons == ()
```

表示三种 Card Type 都具有 Trigger Icon 这一 Card Information，但该卡基础定义中没有任何 Trigger Icon。

具体定义结构不得为了统一字段而给不具有某项 Card Information 的 Card Type 填入虚假的 `0`、`None`、空 tuple 或其他默认规则值。


### 2.3.3 图标与触发图标

普通 Icon 与 Trigger Icon 是两类不同的 Card Information，应在程序中保持独立。

官方规则中的普通 Icon 目前需要支持：

```text
Counter Icon
Clock Icon
```

项目程序类型使用：

```python
class CardIcon(Enum):
    COUNTER = "counter"
    CLOCK = "clock"
```

字段统一使用：

```python
card_icons: tuple[CardIcon, ...]
```

而不是较模糊的：

```python
icons
```

`card_icons` 可以为空、单个或复数：

```python
()
(CardIcon.COUNTER,)
(CardIcon.CLOCK,)
(CardIcon.COUNTER, CardIcon.CLOCK)
```

使用 tuple 而不是 set，数据结构本身不自动去重。

Character 与 Event 具有 `card_icons`；Climax 不具有这一 Card Information。

Trigger Icon 使用独立类型：

```python
class TriggerIcon(Enum):
    ...
```

对应字段：

```python
trigger_icons: tuple[TriggerIcon, ...]
```

`trigger_icons` 可以为空、单个、复数，也允许保存重复 Trigger Icon：

```python
()
(TriggerIcon.SOUL,)
(TriggerIcon.SOUL, TriggerIcon.SHOT)
(TriggerIcon.SOUL, TriggerIcon.SOUL)
```

因此：

- 不使用 `set`；
- 不自动去重；
- 不使用 `TriggerIcon.NONE` 表示无 Trigger Icon；
- 空 tuple 表示“具有 Trigger Icon 这一 Card Information，但基础定义中当前数量为 0”。

三种 Card Type 均具有 Trigger Icon 这一 Card Information，因此 `trigger_icons` 属于公共 `CardDefinition`。

当前代码使用：

```python
trigger_marks
```

后续应迁移为：

```python
trigger_icons
```

#### 基础 Trigger Icons 与 Current Trigger Icons

`CardDefinition.trigger_icons` 表示基础 / 印刷 Trigger Icons。

游戏中的 Ability 或 Effect 可以为 Card 增加或移除 Trigger Icon，但不得直接修改 `CardDefinition`。

概念关系：

```text
CardDefinition.trigger_icons
        ↓
Current Effects / Rule Modifiers
        ↓
Current Trigger Icons
```

Current Trigger Icons 由后续规则查询层计算。

Trigger Check 还存在进一步的规则快照：

```text
Current Trigger Icons
        ↓
Card 进入 Resolution Zone 的规定时点
        ↓
Trigger Check Icon Snapshot
        ↓
本次 Trigger Check 按 Snapshot 处理
```

当 Snapshot 中存在多个 Trigger Icons 时，具体执行顺序与结算规则留到 Attack Phase / Trigger Check 章节定义。

不得使用裸 `trigger` 表示触发图标，因为 `trigger` 后续还可能用于 Trigger Step、Trigger Condition 以及 Ability Trigger 等概念。

### 2.3.4 卡片文本

Card Text 是供玩家阅读的自然语言规则文本。

本项目不把手写：

```python
card_text: str
```

作为规则逻辑的独立真相来源。

规则真相原则上来自结构化 Ability / Effect 定义：

```text
Structured Ability / Effect Definition
        │
        ├──→ Resolution Engine
        │     → 执行规则
        │
        └──→ Card Text Renderer
              → 生成供玩家阅读的 Card Text
```

例如一项概念上的结构：

```text
Ability
├─ type = AUTO
├─ trigger = THIS_CARD_ENTERS_STAGE
└─ effect
    └─ DRAW
        ├─ player = MASTER
        └─ count = 1
```

可以由 Renderer 生成类似：

```text
[自] 登场时抽1张。
```

规则引擎直接读取结构化 Ability / Effect，不应：

```text
生成自然语言
→ 再解析自然语言
→ 执行
```

因此：

```text
Card Text
→ 结构化规则数据的人类可读表示

Ability
→ 规则引擎中的结构化能力定义

Effect
→ Ability / Rule 在处理中产生或要求执行的规则效果
```

具体 Ability AST / IR、Card Text Renderer、多语言实现、是否保存官方原文副本以及缓存策略，留到 Ability / Effect 章节决定。

在这些结构建立以前，第一轮 `CardDefinition` 重构不要求提前加入 `card_text: str` 字段。

### 2.3.5 卡片编号

官方英文名称为：

```text
Card Number
```

规范字段：

```python
card_number: str
```

例如：

```text
MK/SJ01-012J
T-001
T-002
T-003
```

当前代码 / JSON 中的：

```python
code
```

后续迁移为：

```python
card_number
```

`Card Number` 与 `Title Code` 是不同概念，不应混用。

`card_number` 保存完整编号，不自行截断尾缀，也不在这一字段中表达“规则上是否属于同一种卡”的额外等价关系。

必须区分：

```text
CardDefinition.card_number
→ 回答“这是什么卡？”

Card 的稳定实例标识
→ 回答“这是本局中的哪一张具体卡？”
```


---

## 2.4 Card Color

颜色属于规则值，不使用任意字符串作为最终规则状态。

规范类型：

```python
class CardColor(Enum):
    YELLOW = "yellow"
    GREEN = "green"
    RED = "red"
    BLUE = "blue"
```

当前先支持：

```text
YELLOW
GREEN
RED
BLUE
```

以后确认存在需要支持的新颜色时，再扩展 `CardColor`。

当前不预留：

```text
OTHER
UNKNOWN
CUSTOM
```

等兜底值。

未知或尚未支持的颜色应在数据加载 / 验证阶段明确失败，而不是静默进入规则对象。

`CardDefinition.color` 表示基础 / 印刷 Color。若未来 Ability / Effect 改变某张 Card 的当前 Color，同样由规则查询层计算 Current Color，不修改 Definition。

---

## 2.5 基础 Card Information 与 Current Card Information

`CardDefinition` 保存基础 / 印刷 Card Information，并保持不可变。

运行时 Ability、Effect 或其他规则修正不得直接修改 `CardDefinition`。

例如：

```text
CharacterDefinition.power = 5000
```

某 Effect 令该 Card 当前 Power +2000 时：

```text
Definition Power
→ 5000

Current Power
→ 7000
```

不得通过修改：

```python
card.definition.power
```

实现。

### 2.5.1 Card 保持轻量

`Card` 表示本局中的具体实体及其必要运行时状态。

不应把所有 Current Card Information 的规则计算逐步塞入 `Card` 本身，例如：

```python
card.current_power(...)
card.current_level(...)
card.current_color(...)
card.current_traits(...)
card.current_trigger_icons(...)
```

Current Card Information 可能依赖：

- `CardDefinition`
- Card 当前所在 Zone / Position
- 当前 Game State
- 其他 Card
- Continuous Ability
- 临时 Effect
- 当前 Turn / Phase
- 其他规则修正

因此 Current Card Information 属于独立规则查询职责。

### 2.5.2 Query System

项目建立独立的只读 Query 层。

概念关系：

```text
CardDefinition
+
Card Runtime State
+
Game State
+
Current Effects
        ↓
Query System
        ↓
Current Card Information
```

Query System 还可以用于规则合法性查询，例如：

```text
当前 Card 是否可以使用？
当前 Player 有哪些 Legal Actions？
某个 Choice 有哪些合法选项？
```

UI 不自行重新实现规则判断。

例如：

```text
玩家点击 Card
        ↓
Query System
        ↓
返回当前 Card Information
        ↓
UI 显示
```

或者：

```text
玩家点击 Hand 中的 Card
        ↓
Query System
        ↓
查询是否存在合法使用方式
        ↓
合法
→ UI 启用对应按钮

不合法
→ UI 禁用对应按钮
```

### 2.5.3 Query 不执行操作

Query System 必须保持只读。

它只能：

```text
读取当前规则状态
→ 计算
→ 返回结果
```

不得在查询过程中：

- 移动 Card；
- 支付 Cost；
- 改变 Game State；
- 触发 Ability；
- 执行 Effect。

真正的 Action / Command 在执行前仍必须重新进行权威合法性验证。

Query 与 Action Validation 应共享同一套底层规则判断逻辑，避免 UI 查询规则和实际执行规则形成两套实现。

---

## 2.6 卡片方向

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

## 2.7 卡片正反面状态

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

### 2.7.1 与卡片方向的关系

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

### 2.7.2 与区域规则的关系

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

## 2.8 卡片稳定身份

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

card_number
→ CardDefinition 上的 Card Number
```

例如：

```text
CardDefinition.card_number = "T-001"

Card.card_id = "P1-T001-03"
```

前者回答“这是什么卡”，后者回答“这是本局里的哪一张卡”。

---

## 2.9 第 2 章测试规范

卡片系统建立与本章对应的独立测试目录。

规范方向：

```text
tests/
└─ test_02_cards/
   ├─ test_card_definition.py
   ├─ test_card_information_boundaries.py
   ├─ test_trigger_icons.py
   ├─ test_card_icons.py
   ├─ test_card_color.py
   ├─ test_card_loader.py
   ├─ test_card_identity.py
   └─ test_card_instance.py
```

现有测试可以继续保留作为旧回归测试，不要求一次性迁移或删除。

### 2.9.1 测试卡数据来源

以后自动化测试使用的卡片 fixture / card data 只从：

```text
card/TEST/
```

读取。

正式卡片目录不得作为自动化测试的数据来源。

当前测试卡：

```text
T-001
→ Character

T-002
→ Climax

T-003
→ Event
```

`T-003` 只用于卡片系统测试，暂时不加入现有卡组测试。

### 2.9.2 第一批 Card Definition 测试

第一批优先建立：

```text
test_card_definition.py
test_card_information_boundaries.py
test_trigger_icons.py
test_card_icons.py
test_card_color.py
test_card_loader.py
```

重点验证：

```text
CardDefinition
→ 是三种具体 Definition 的共同基类

CharacterDefinition
→ 具有 Character 专属 Card Information

EventDefinition
→ 具有 Event 专属 Card Information

ClimaxDefinition
→ 不具有不适用于 Climax 的 Card Information
```

Card Information 边界至少覆盖：

```text
                 Character  Event  Climax
level                ✓       ✓      —
cost                 ✓       ✓      —
power                ✓       —      —
soul                 ✓       —      —
traits               ✓       —      —
card_icons           ✓       ✓      —
trigger_icons        ✓       ✓      ✓
```

还应验证：

```text
trigger_icons
→ 可为空、单个、复数、重复
→ 保持顺序
→ 不自动去重

card_icons
→ 可为空、单个、复数
→ 不使用 set 自动去重

CardColor
→ 当前只接受已定义规则颜色

Loader
→ 未知 card_type / color / icon 等非法输入明确失败
→ 不静默接受或忽略不属于该 Card Type 的 Card Information
```

### 2.9.3 测试与规范的关系

以后修改某一规范章节时，应同时检查：

> 该规则是否需要对应的自动化测试？

目标关系：

```text
docs/02_cards.md
        ↓
Card 实现
        ↓
tests/test_02_cards/
```

测试作为规范的可执行验证，但不替代规范文档本身。

---

## 2.10 当前命名审计摘要

| 当前名称 | 规范名称 | 类别 | 状态 | 原因 |
| --- | --- | --- | --- | --- |
| `kind` | `card_type` | `CardType` | 待迁移 | 使用明确类别名 |
| `"character"` | `CardType.CHARACTER` | `CardType` | 待迁移 | 避免规则层裸字符串 |
| `"climax"` | `CardType.CLIMAX` | `CardType` | 待迁移 | 与高潮区、高潮阶段消歧 |
| `trigger_marks` | `trigger_icons` | `TriggerIcon` | 待迁移 | 使用官方 Trigger Icon 概念 |
| `icons` | `card_icons` | `CardIcon` | 待迁移 / 待实现 | 与 Trigger Icon 明确区分 |
| `color: str` | `color: CardColor` | Card Information | 待迁移 | 使用可维护规则 Enum |
| `code` | `card_number` | Card Information | 待迁移 | 官方名称为 Card Number |
| `instance_id` | `card_id` | 稳定标识 | 待检查 | Replay 影响较大 |
| `number` | 待检查 | 项目调试信息 | 待检查 | 不属于官方 Card Information |
| `face_up` | `face_state` | `CardFaceState` | 待迁移 | 明确表达正反面状态 |
| `CardDefinition = CharacterDefinition` | 正式 `CardDefinition` 基类 | 卡片定义 | 待迁移 | 当前兼容别名不能代表全部卡片种类 |
| `AnyCardDefinition` | `CardDefinition` | 卡片定义 | 待迁移 | 公共基类建立后原则上不再需要 |


---

## 2.11 本节暂不决定的内容

以下内容暂不提前锁死：

1. `instance_id` 是否迁移为 `card_id`。
2. 当前 `number` 调试字段是否继续保留。
3. Ability、Effect 的最终 AST / IR 与数据结构。
4. Card Text Renderer 的最终接口与多语言实现。
5. 是否保存官方 Card Text 原文副本，以及缓存策略。
6. Current Card Information Query 的最终模块、类名与函数名。
7. Action Legality Query 与 Action Validation 的最终接口。
8. 区域的信息公开规则。
9. 特殊效果造成的信息公开变化。
10. 完整卡片数据库中的非核心规则字段。
11. Card Master 的最终查询接口，以及是否需要在特定规则处理中保存 Master 快照。
12. Card runtime state 的最终存储位置与结构。


---

## 2.12 本节命名结论

当前确定的规范方向：

```python
Card

CardDefinition
CharacterDefinition
EventDefinition
ClimaxDefinition

CardType.CHARACTER
CardType.EVENT
CardType.CLIMAX

CardColor.YELLOW
CardColor.GREEN
CardColor.RED
CardColor.BLUE

CardIcon.COUNTER
CardIcon.CLOCK

TriggerIcon

card_number
name
card_type
color
traits
level
cost
card_icons
power
soul
trigger_icons

CardOrientation.STAND
CardOrientation.REST
CardOrientation.REVERSE
orientation          # 规范字段语义，存储位置待实现时决定

CardFaceState.FACE_UP
CardFaceState.FACE_DOWN
face_state           # 规范字段语义，存储位置待实现时决定

owner_id             # Card 的固定 Owner；具体存储位置待实现时决定
```

并明确：

```text
CardDefinition
→ 保存基础 / 印刷 Card Information
→ 不被运行时 Ability / Effect 修改

Card
→ 表示本局中的具体卡片实体
→ 不负责计算 Current Card Information

Query System
→ 只读查询 Current Card Information 与规则合法性
→ 不执行 Action

Card Text
→ 原则上由结构化 Ability / Effect 数据渲染生成
→ 不作为独立手写的规则真相来源
```

以下名称仍保持待检查：

```python
card_id
instance_id
number
```

信息公开范围以及各区域默认的正反面规则，留到场地区域章节统一定义。
