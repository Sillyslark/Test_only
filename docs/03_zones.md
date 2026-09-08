# 3. 场地与区域

本节用于统一游戏区域、舞台位置、指示物区域、区域顺序以及卡片信息访问相关概念的命名。

**主要类别：**

- `Zone`
- `StagePosition`
- `CardFaceState`
- Card Information Access

本节只确定区域相关概念、名称和规则边界，不直接要求修改现有代码。

---

## 3.1 区域总分类

游戏中的 `Card` 在任一时点只有一个**直接所在区域**。

本节使用“直接所在区域”表达 Card 当前实际位于哪里。Card 的移动原则上表现为：

```text
一个直接区域
→ 另一个直接区域
```

例如：

```text
Hand
→ StagePosition.CENTER_LEFT

StagePosition.CENTER_LEFT
→ Waiting Room

Deck
→ Marker Area
```

`StagePosition` 对应的五个具体位置本身视为特殊的 Zone，因此从 Hand 将 Card 放置到 Stage Position，仍然属于 Card 在 Zone 之间的移动。

这里的“特殊 Zone”描述的是**规则概念关系**。`StagePosition` 是用于标识五个舞台位置 Zone 的专用类别；程序实现上不要求 `StagePosition` 继承 `Zone`，也不在本节提前规定两者最终采用何种类型结构。

区域模型可以概括为：

```text
直接区域
│
├─ 常规 Zone
│   ├─ Deck
│   ├─ Hand
│   ├─ Waiting Room
│   ├─ Clock
│   ├─ Level
│   ├─ Stock
│   ├─ Climax Area
│   ├─ Memory
│   └─ Resolution Zone
│
├─ Stage Position Zone
│   ├─ CENTER_LEFT
│   ├─ CENTER_CENTER
│   ├─ CENTER_RIGHT
│   ├─ BACK_LEFT
│   └─ BACK_RIGHT
│
└─ Marker Area Zone
    └─ 每个 Stage Position 分别对应一个独立 Marker Area
```

`Stage`、`Center Stage`、`Back Stage` 不需要作为 Card 的额外直接区域重复保存。

对于位于某个 Stage Position 的 Card，可以根据该 Position 的身份推导：

```text
direct zone = CENTER_LEFT

→ 位于 Stage
→ 位于 Center Stage
→ 位于 CENTER_LEFT
```

因此不采用：

```text
一张 Card 同时保存多个 Zone 归属
```

而采用：

```text
一张 Card
→ 一个 direct zone
→ 其他 Stage / Center Stage / Back Stage 关系由 direct zone 推导
```

这样可以避免移动、Replay、状态哈希以及规则查询中出现重复或互相矛盾的区域状态。

---

## 3.2 常规区域

**类别：`Zone`**

常规区域包括：

- Deck
- Hand
- Waiting Room
- Clock
- Level
- Stock
- Climax Area
- Memory
- Resolution Zone

| 中文概念 | 官方名称 | 规范程序名称 | 当前程序名称 | UI 名称 | 状态 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 卡组 | Deck | `Zone.DECK` / `deck` | `deck` | 卡组 | 已确认 | — |
| 手牌 | Hand | `Zone.HAND` / `hand` | `hand` | 手牌 | 已确认 | — |
| 控制室 | Waiting Room | `Zone.WAITING_ROOM` / `waiting_room` | `waiting_room` | 控制室 | 已确认 | — |
| 计时区 | Clock | `Zone.CLOCK` / `clock` | `clock` | 计时区 | 已确认 | 与 `Phase.CLOCK` 区分 |
| 等级区 | Level | `Zone.LEVEL` / `level` | `level` | 等级区 | 已确认 | 与卡片 `level` 属性区分 |
| 库存区 | Stock | `Zone.STOCK` / `stock` | `stock` | 库存区 | 已确认 | — |
| 高潮区 | Climax Area | `Zone.CLIMAX_AREA` / `climax_area` | 当前主要为 `climax` | 高潮区 | 待迁移 | 与 `CardType.CLIMAX`、`Phase.CLIMAX` 区分 |
| 思出区 | Memory | `Zone.MEMORY` / `memory` | `memory` | 思出区 | 已确认 | — |
| 处理区 | Resolution Zone | `Zone.RESOLUTION_ZONE` / `resolution_zone` | `resolution_zone` | 处理区 | 已确认 | — |

规则类别统一使用：

```python
Zone
```

具体区域名称保留官方名称中的差异，不强行把所有区域统一写成 `Area` 或 `Zone` 后缀。

例如：

```python
Zone.DECK
Zone.HAND
Zone.WAITING_ROOM
Zone.CLIMAX_AREA
Zone.RESOLUTION_ZONE
```

---

## 3.3 舞台及其规则分组

**类别：`StagePosition` 及其派生分组**

每名玩家拥有五个可以直接放置舞台卡的 Stage Position。

这五个 Position 共同构成 Stage 的规则范围，但程序中不需要为了表示 `Stage` 再建立一个与五个 Position 重复保存卡片的容器。

结构为：

```text
Stage
│
├─ Center Stage
│   ├─ StagePosition.CENTER_LEFT
│   ├─ StagePosition.CENTER_CENTER
│   └─ StagePosition.CENTER_RIGHT
│
└─ Back Stage
    ├─ StagePosition.BACK_LEFT
    └─ StagePosition.BACK_RIGHT
```

其中真正作为 Card 直接所在区域的是五个 Stage Position。

`Stage`、`Center Stage` 和 `Back Stage` 主要用于规则查询和位置分组，而不是 Card 的具体直接区域。

因此，Card 不能仅以 `Stage`、`Center Stage` 或 `Back Stage` 作为最终直接移动目标。规则要求 Card 移动到舞台时，最终必须确定一个具体的 `StagePosition`。

例如：

```text
完整：
Hand
→ StagePosition.CENTER_LEFT

不能作为最终直接区域：
Hand
→ Stage

Hand
→ Center Stage
```

因此：

```text
Card.direct_zone = StagePosition.CENTER_LEFT
```

可以推导：

```text
Card 位于 Stage
Card 位于 Center Stage
Card 位于 CENTER_LEFT
```

不需要额外保存：

```text
card.zone = STAGE
card.zone = CENTER_STAGE
card.zone = CENTER_LEFT
```

等多个并列区域状态。

为了表示分组，程序可使用类似：

```python
CENTER_STAGE_POSITIONS = (
    StagePosition.CENTER_LEFT,
    StagePosition.CENTER_CENTER,
    StagePosition.CENTER_RIGHT,
)

BACK_STAGE_POSITIONS = (
    StagePosition.BACK_LEFT,
    StagePosition.BACK_RIGHT,
)
```

这里确定的是分组语义，不要求立即采用上述具体实现。

---

## 3.4 舞台位置

**类别：特殊 `Zone`；位置身份由 `StagePosition` 表示**

五个 Stage Position 都是可以作为 Card 直接所在区域的特殊 Zone。

`StagePosition` 用于明确这是五个固定舞台位置中的哪一个。

规范类型：

```python
StagePosition
```

五个规范位置：

```python
StagePosition.CENTER_LEFT
StagePosition.CENTER_CENTER
StagePosition.CENTER_RIGHT
StagePosition.BACK_LEFT
StagePosition.BACK_RIGHT
```

对应的规范序列化值可使用：

```text
center_left
center_center
center_right
back_left
back_right
```

| 中文概念 | 规范程序名称 | 当前程序名称 | UI 名称 | 状态 |
| --- | --- | --- | --- | --- |
| 前列左 | `StagePosition.CENTER_LEFT` / `center_left` | `front_left` | 前列左 | 待迁移 |
| 前列中 | `StagePosition.CENTER_CENTER` / `center_center` | `front_center` | 前列中 | 待迁移 |
| 前列右 | `StagePosition.CENTER_RIGHT` / `center_right` | `front_right` | 前列右 | 待迁移 |
| 后列左 | `StagePosition.BACK_LEFT` / `back_left` | `back_left` | 后列左 | 已确认 |
| 后列右 | `StagePosition.BACK_RIGHT` / `back_right` | `back_right` | 后列右 | 已确认 |

### 3.4.1 Stage Position 的容量

在合法的稳定游戏状态下：

```text
一个 StagePosition
→ 0..1 张舞台卡
```

即每个 Position 至多承载一张舞台卡。

规则处理过程中可能暂时出现为了处理重叠、替换或其他规则过程而使用的中间状态；这些临时实现不改变 Stage Position 在稳定状态下“至多一张”的基本语义。

因此规范概念更接近：

```python
stage[position] -> Card | None
```

而不是把 Stage Position 本身定义成一个可以长期容纳多张舞台卡的普通列表区域。

这里描述的是规则语义，不要求立即改变当前存储结构。

### 3.4.2 舞台位置的派生属性

一个 Stage Position 的其他位置关系应从其 `StagePosition` 身份推导，不重复保存互相重叠的布尔状态。

例如：

```text
StagePosition.CENTER_LEFT
```

天然可以推导：

```text
属于 Stage
属于 Center Stage
位于 Left
```

不建议同时独立保存：

```text
is_stage = True
is_center = True
is_center_left = True
```

以免产生互相矛盾的状态。

### 3.4.3 舞台位置与换位

舞台换位针对的是两个 Stage Position 上的规则内容，而不是简单地把两个 Character 对象互换。

因此程序语义应明确为：

```text
交换两个 StagePosition 上需要随位置一起处理的相关内容
```

具体哪些内容随换位处理，由换位规则决定。

尤其需要结合与各 Stage Position 一一对应的 Marker Area 处理，不能仅通过交换两张 Character 来替代完整规则过程。

与舞台位置相关的程序命名原则上使用：

```python
STAGE_POSITIONS

position
source_position
target_position
destination_position
first_position
second_position
selected_stage_positions
```

当前代码中的：

```python
STAGE_SLOTS

slot
source_slot
target_slot
destination_slot
first_slot
second_slot
selected_stage_slots
```

属于待迁移或待核对名称。

实际迁移前必须检查其是否参与：

- Replay
- Action 序列化
- 状态哈希
- 测试数据
- UI 位置映射

---

## 3.5 指示物区域

**类别：`Zone`，并与 `StagePosition` 一一对应**

每名玩家拥有五个独立的 Marker Area。

每个 Marker Area 分别与一个 Stage Position 一一对应：

```text
StagePosition.CENTER_LEFT
        ↕ 一一对应
Marker Area for CENTER_LEFT
```

两者都是 Card 可以直接位于的具体区域，但它们不是同一个 Zone，也不存在“Marker Area 属于 Character”的对象所有权关系。

核心关系：

```text
StagePosition
├─ 稳定状态下：0..1 张舞台卡
│
└─ 一一对应
    ↓
Marker Area
└─ 0..N 张 Card，具有顺序
```

因此可以概念化为两套通过同一个 `StagePosition` 身份关联的数据：

```python
player.stage[position]
player.marker_areas[position]
```

这里的 `position` 用于说明二者对应的是舞台上的同一位置关系，不表示 Marker Area 是 Stage Position 内部的第二个卡槽。

在单个玩家的状态内部，`position` 足以从 `marker_areas` 中定位对应 Marker Area；在整局游戏范围内，一个具体 Marker Area 的身份还必须包含所属玩家。

因此：

```text
P1 + CENTER_LEFT
→ P1 对应的 CENTER_LEFT Marker Area

P2 + CENTER_LEFT
→ P2 对应的 CENTER_LEFT Marker Area
```

二者是不同的 Zone。

未来如果建立统一的具体区域引用结构，需要能够表达：

```text
所属玩家
+ 区域类别
+ StagePosition（该区域需要时）
```

这里的“所属玩家”也是后续确定 Zone Master 的必要信息。

对于属于某名 Player 的 Zone，应能够由具体 Zone 引用确定其官方规则意义上的 `Master`。位于该 Zone 中的 Card，再按官方规则由 Zone Master 确定 Card Master。

因此：

```text
Card Owner
→ 不因 Card 进入另一名 Player 的 Zone 而改变

Card direct zone
→ 指向某名 Player 的具体 Zone

Zone Master
→ 由该具体 Zone 的规则归属确定

Card Master
→ 按当前 direct zone 的 Zone Master 确定
```

例如：

```text
P1 拥有的 Card
→ 进入 P2 的某个 Zone

Owner
→ 仍然是 P1

Master
→ 按该 Zone 的 Master 规则确定，可成为 P2
```

具体类型结构本节暂不决定。

Marker Area 是独立 Zone。

### 3.5.1 Marker 与 Character 的关系

Marker 本身仍然是实际存在的 `Card`，不是新的 `CardType`。

Marker Area 与 Stage Position 一一对应，而不是由当前位于该 Position 的 Character 对象拥有。

因此当 Character：

- 离开 Stage Position；
- 与其他 Position 换位；
- 被其他 Character 替换；

对应 Marker 应如何处理，属于规则处理问题，不能通过对象从属关系自动推导。

| 中文概念 | 官方名称 | 规范程序名称 | 当前程序名称 | UI 名称 | 状态 |
| --- | --- | --- | --- | --- | --- |
| 指示物 | Marker | `marker` | `marker` | 指示物 | 已确认 |
| 指示物区域 | Marker Area | `marker_area` | 当前主要通过 `markers[position]` 表示 | 指示物区 | 已确认 |
| 指示物区域集合 | — | `marker_areas` | `markers` | — | 待迁移 |

长期命名方向：

```python
player.marker_areas[position]
```

比：

```python
player.markers[position]
```

更能表达“通过 Stage Position 身份定位对应的 Marker Area”。

### 3.5.2 指示物区域顺序

Marker Area 中的卡片具有顺序。

新放入的 Marker 通常置于该区域顶部；移除时按具体规则处理。

因此 Marker Area 必须使用能够保存顺序的数据结构，不应使用无序集合。

### 3.5.3 指示物正反面

Marker Area 中的卡片通常背面朝上，但规则或效果可以要求某张 Marker 正面朝上。

因此：

```text
Marker Area 的默认放置规则
≠
Marker 当前实际的 CardFaceState
```

具体卡片当前使用：

```python
CardFaceState.FACE_UP
CardFaceState.FACE_DOWN
```

区域规则只定义默认行为，不替代卡片自身的实际状态。

---

## 3.6 卡片信息的访问与规则引用

本节需要区分两个完全不同的问题：

1. 某个玩家是否有权查看一张卡的实际 Card Information。
2. 当前规则处理是否认为这张卡具有某项 Card Information。

这两个概念必须分开。

---

### 3.6.1 卡片信息访问权限

**概念：Card Information Access**

卡片信息访问权限回答：

> 指定玩家是否有权查看指定 Card 的实际 Card Information？

这是一个与玩家相关的查询结果，不应作为 `Card` 自身的固定字段。

规范查询方向：

```python
can_access_card_information(
    card_id,
    viewer_id,
) -> bool
```

实际结果依赖：

```text
Card
+ Zone
+ CardFaceState
+ Viewer
+ 特殊规则或效果
```

例如：

```text
自己手牌中的卡
→ 自己可以查看
→ 对手不能查看

等级区中的正面卡
→ 双方可以查看

等级区中的背面卡
→ 该区域所属玩家可以查看
→ 对手不能查看
```

因此不使用裸 `Visibility` 作为卡片固有属性。

---

### 3.6.2 规则引用中的卡片信息

玩家能够查看一张卡，不代表规则当前允许引用该卡的 Card Information。

例如一张红色 Level 2 卡在等级区背面朝上：

```text
该玩家本人
→ 可以查看这张卡实际是什么

规则引用
→ 该卡被视为没有 Color
→ 该卡被视为没有 Level
→ 该卡被视为没有 Name
→ 其他通常的 Card Information 同样不参与规则判定
```

因此：

```text
玩家知道它实际是红色
≠
规则认为它当前具有红色
```

典型影响包括：

```text
颜色条件
→ 背面 Level 卡不贡献颜色

等级合计条件
→ 背面 Level 卡的等级不计入合计

卡名条件
→ 背面卡通常不提供卡名信息
```

这一层暂不建立一个整体的 `AVAILABLE / UNAVAILABLE` 状态枚举。

原因是某些规则可能只让特定信息或特定能力继续有效，因此更适合逐项通过规则查询接口取得当前可引用的信息。

未来规则查询方向例如：

```python
get_card_name(...)
get_card_color(...)
get_card_level(...)
get_card_traits(...)
```

这些接口应先考虑：

```text
当前区域
CardFaceState
特殊规则或效果
```

再决定返回实际信息或“不存在”。

规则代码不应在需要规则判定时直接绕过查询层读取：

```python
card.definition.color
card.definition.level
card.definition.name
```

---

### 3.6.3 信息访问与规则引用相互独立

典型示例：

```text
P1 等级区
└── 一张背面红色 Level 2 Card
```

结果：

```text
P1 是否可以查看？
→ 可以

P2 是否可以查看？
→ 不可以

规则是否把它视为红色？
→ 不会

规则是否把它视为 Level 2？
→ 不会
```

因此第三节正式区分：

```text
Card Information Access
→ 谁可以查看真实信息

Card Information in Rule References
→ 规则当前认为这张卡具有哪些信息
```

不将二者合并成一个 `Visibility`、`Availability` 或 `State` 字段。

---

## 3.7 有序区域的存储顺序

有顺序的区域统一采用 **top-first** 存储。

`top-first` 仅适用于规则上具有顺序语义的 Zone。没有顺序语义的 Zone 不使用 `Top` / `Bottom` 概念。

例如，Deck、Clock、Stock、Resolution Zone、Marker Area 等需要按其规则保存顺序；单个 Stage Position 不因为底层可能使用某种容器，就自动获得 `Top` / `Bottom` 语义。

规范：

```text
第一个元素
→ Top

最后一个元素
→ Bottom
```

例如：

```text
Deck

Top
↓
[0] card_a
[1] card_b
[2] card_c
[3] card_d
↑
Bottom
```

Python 中：

```python
zone[0]
```

表示第一个元素，也就是 Top。

```python
zone[-1]
```

可以访问最后一个元素，也就是 Bottom。

这里的 `-1` 只是 Python 的访问语法，不是区域中的实际位置编号。

### 3.7.1 统一方向

所有有顺序的区域都应采用同一方向解释。

例如：

```text
Deck
Waiting Room
Clock
Stock
Resolution Zone
Marker Area
```

不得出现某一区域使用：

```text
index 0 = Top
```

而另一区域又使用：

```text
index 0 = Bottom
```

的局部特例。

### 3.7.2 规则语义与内部索引分离

规则层不应依赖开发者记忆 Python 索引。

因此规则/API 层应使用明确的顶部、底部语义，而不是通过：

```python
0
-1
```

表达规则含义。

规范候选：

```python
ZonePlacement.TOP
ZonePlacement.BOTTOM
```

例如：

```python
move_card(
    card_id,
    destination=Zone.DECK,
    placement=ZonePlacement.TOP,
)
```

以及：

```python
move_card(
    card_id,
    destination=Zone.DECK,
    placement=ZonePlacement.BOTTOM,
)
```

底层仍然可以继续使用当前 `list[Card]` 数据结构。

实现映射：

```text
ZonePlacement.TOP
→ 插入第一个位置

ZonePlacement.BOTTOM
→ 追加到最后一个位置
```

例如：

```python
if placement == ZonePlacement.TOP:
    zone.insert(0, card)

elif placement == ZonePlacement.BOTTOM:
    zone.append(card)
```

不要使用：

```python
zone.insert(-1, card)
```

表达 Bottom，因为 Python 的 `insert(-1, ...)` 并不等同于追加到最后。

### 3.7.3 数据结构不需要因此改变

本节只规定顺序语义，不要求修改当前区域的存储结构。

当前可以继续：

```python
deck: list[Card]
waiting_room: list[Card]
clock: list[Card]
```

规则层通过明确的 TOP / BOTTOM 语义隔离底层实现。

这样以后即使内部容器从 `list` 更换为其他结构，规则层调用方式也不需要改变。

---

## 3.8 区域默认放置规则与卡片实际状态

区域通常具有默认的卡片放置方式，但默认规则与卡片当前实际状态必须分开。

例如：

```text
某区域通常要求 CardFaceState.FACE_DOWN
```

并不代表区域自身拥有一个 `face_down = True` 状态。

正确关系是：

```text
Zone Rule
→ 决定卡片进入该区域时通常采用什么 CardFaceState

Card
→ 保存或表现当前实际 CardFaceState
```

部分规则或效果可以覆盖区域的默认放置方式。

因此第三节只定义区域默认规则的语义，不在这里决定具体存储结构。

---

## 3.9 当前命名审计方向

本节目前已经能够确定的主要命名方向包括：

| 当前名称 | 规范候选 | 类别 | 状态 | 原因 |
| --- | --- | --- | --- | --- |
| `front_left` | `center_left` | `StagePosition` | 待迁移 | 官方使用 Center Stage |
| `front_center` | `center_center` | `StagePosition` | 待迁移 | 官方使用 Center Stage |
| `front_right` | `center_right` | `StagePosition` | 待迁移 | 官方使用 Center Stage |
| `STAGE_SLOTS` | `STAGE_POSITIONS` | `StagePosition` | 待迁移 | 使用官方 Position 概念 |
| `slot` 系列变量 | `position` 系列变量 | `StagePosition` | 待迁移 | 与官方 Position 对齐 |
| `climax`（区域语义） | `climax_area` | `Zone` | 待迁移 | 与 CardType / Phase 消歧 |
| `markers`（区域集合语义） | `marker_areas` | `Zone` | 待迁移 | 表达五个独立 Marker Area |

这里的迁移只针对对应规则语义，不进行裸字符串全局替换。

例如：

```text
climax
```

可能同时表示：

```text
CardType.CLIMAX
Phase.CLIMAX
Zone.CLIMAX_AREA
局部变量中的某张高潮卡
```

必须按类别分别处理。

---

## 3.10 本节暂不决定的内容

以下内容不在本节提前锁死：

1. `_move_card()` 最终 API 的完整签名。
2. `ZonePlacement` 是否立即实现为 Enum。
3. 区域容器是否从 `list` 更换为其他数据结构。
4. Card Information Access 是否需要更复杂的权限结果类型。
5. 规则查询接口最终统一放在哪个模块。
6. 特殊效果导致的信息公开变化。
7. 特殊效果导致的区域默认放置规则覆盖。
8. 能力导致的区域移动替换。
9. Replay 中区域和 StagePosition 的迁移方案。
10. Zone 与 StagePosition 最终枚举的数据结构。
11. `direct zone` 在运行时最终使用何种统一引用结构表示。
12. Zone Master 的最终查询接口，以及 Card Master 是否完全采用动态推导或在特定规则处理中使用快照。

这些内容在相应基础设施或规则系统实现时再决定。

---

## 3.11 本节命名结论

当前可以确定的规范方向：

```python
Zone

Zone.DECK
Zone.HAND
Zone.WAITING_ROOM
Zone.CLOCK
Zone.LEVEL
Zone.STOCK
Zone.CLIMAX_AREA
Zone.MEMORY
Zone.RESOLUTION_ZONE

StagePosition

StagePosition.CENTER_LEFT
StagePosition.CENTER_CENTER
StagePosition.CENTER_RIGHT
StagePosition.BACK_LEFT
StagePosition.BACK_RIGHT

STAGE_POSITIONS

center_left
center_center
center_right
back_left
back_right

marker_area
marker_areas

# 每个 Marker Area 通过对应的 StagePosition 身份区分

can_access_card_information(...)

ZonePlacement.TOP
ZonePlacement.BOTTOM
```

其中 `ZonePlacement` 当前作为规范候选存在，不要求立即实现。

区域内部有序存储继续统一采用：

```text
top-first
```

即：

```text
第一个元素 = Top
最后一个元素 = Bottom
```

规则代码应通过明确的 TOP / BOTTOM 语义访问和放置卡片，而不是依赖魔法索引。
