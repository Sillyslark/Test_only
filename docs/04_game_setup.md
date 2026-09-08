# 4. 游戏开始

本节统一从对局准备到第一个回合开始之间的规则概念和命名。

本节主要讨论：

- Player 的不同身份
- Deck 的开局合法性前置检查
- Shuffle
- Starting Player
- Initial Hand
- Mulligan
- Game Preparation 与第一个 Turn 的衔接

本节只确定规则语义、命名和流程边界。Action、Replay、RNG、状态机及完整 Deck Legality 的具体实现留待相应章节决定。

---

## 4.1 游戏开始流程总览

游戏开始前的流程统一称为 Game Preparation。

本项目按以下规则顺序理解：

```text
确认双方 Player 与 Deck
        ↓
Deck Legality 前置检查
        ↓
双方 Shuffle Deck
        ↓
随机确定 Starting Player
        ├─ P1：50%
        └─ P2：50%
        ↓
双方形成 Initial Hand
        ↓
Mulligan
        ├─ Starting Player
        └─ 另一名 Player
        ↓
Game Preparation 完成
        ↓
Starting Player becomes Turn Player
        ↓
第一个 Turn 开始
```

其中 Deck Legality 是模拟器进入正式 Game Preparation 前的合法性前置条件。

第一个 Turn 开始后的具体流程由第 5 节定义。

---

## 4.2 Player 与玩家身份

**主要官方概念：**

- Player
- Starting Player
- Turn Player
- Non-turn Player
- Play Timing
- Master

项目必须区分玩家的固定身份、显示名称以及规则流程中的临时身份。

### 4.2.1 Player ID

每名玩家在一局游戏中拥有稳定且唯一的内部身份：

```python
PlayerId.P1
PlayerId.P2
```

`P1` 和 `P2` 只表示对局内部的玩家身份，不表示：

```text
先攻 / 后攻
当前回合玩家
玩家用户名
```

因此完全允许：

```text
P1 → 非 Starting Player
P2 → Starting Player
```

`PlayerId` 在整局游戏期间保持稳定。

测试、Replay、Action、状态哈希以及其他内部规则逻辑应使用稳定的 `player_id` 区分玩家，而不能依赖显示名称。

### 4.2.2 Player Name

玩家显示名称使用：

```python
player_name
```

`player_name`：

- 可以由玩家修改；
- 允许两名玩家使用相同名称；
- 主要用于 UI 显示；
- 不承担对局内部唯一身份的职责。

例如：

```text
P1 / Alice
P2 / Alice
```

即使显示名称相同，仍然可以通过 `PlayerId` 唯一区分。

因此：

```text
内部身份判断
→ player_id

UI 显示
→ player_name
```

### 4.2.3 Starting Player

**官方术语：Starting Player**

Starting Player 是 Game Preparation 中随机确定的玩家。

规范名称：

```python
starting_player_id
```

`starting_player_id` 与 `PlayerId.P1 / P2` 没有固定绑定关系。

模拟器为双人游戏，因此官方“随机确定 Starting Player”的要求落实为：

```text
P1 成为 Starting Player：50%
P2 成为 Starting Player：50%
```

随机结果产生后，不再由玩家重新选择谁成为 Starting Player。

`starting_player_id` 是本局确定后保持不变的对局属性。

### 4.2.4 Turn Player 与 Non-turn Player

**官方术语：**

```text
Turn Player
Non-turn Player
```

规范名称：

```python
turn_player_id
```

Turn Player 表示当前是谁的 Turn。

Non-turn Player 是相对于当前 Turn Player 的规则身份。在双人游戏中可以由 `turn_player_id` 唯一推导，因此原则上不需要额外保存一份：

```python
non_turn_player_id
```

Starting Player 与 Turn Player 是不同概念：

```text
starting_player_id
→ Game Preparation 中确定，整局保持不变

turn_player_id
→ 当前 Turn 的 Player，随 Turn 改变
```

### 4.2.5 Play Timing

**官方术语：Play Timing**

Play Timing 表示规则在某一时点给予某名 Player 的行动机会。

它与 Turn Player 不同。

例如：

```text
turn_player_id = P1
```

并不意味着所有规则处理都只能由 P1 执行。

某些流程中，P2 也可能获得 Play Timing，而 P1 仍然是 Turn Player。

因此不建立一个含义过宽的：

```python
acting_player_id
```

来同时表示 Turn Player、获得 Play Timing 的 Player、进行选择的 Player 等不同概念。

Play Timing 最终如何表示，留待后续流程系统确定。

### 4.2.6 Choice 与 Play Timing 的区别

某个规则或效果要求某名 Player 作出选择，不等于该 Player 获得 Play Timing。

因此未来处理时应区分：

```text
某 Player 获得 Play Timing
```

与：

```text
某 Player 被规则或效果要求进行 Choice
```

二者不能统一解释为“当前行动玩家”。

### 4.2.7 Master

**官方术语：Master**

Master 是 Card、Ability、Zone 等规则关系中的独立概念。

它不能与：

```text
PlayerId
Starting Player
Turn Player
获得 Play Timing 的 Player
```

混为一谈。

规范候选：

```python
master_id
```

具体哪些对象保存或能够查询 Master，由后续相关章节确定。

---

## 4.3 游戏初始状态与 Deck Legality 前置检查

进入 Game Preparation 的后续流程以前，双方用于本局游戏的 Deck 必须通过合法性检查。

当前至少确认以下最低条件：

```text
Deck 必须恰好包含 50 张 Card
Climax Card 不得超过 8 张
```

任一 Deck 未通过合法性检查：

```text
Game Preparation 不继续
```

双方 Deck 均合法后，才进入后续 Shuffle 流程。

本节只规定：

> Game Setup 在何时要求 Deck 通过合法性检查。

完整的 Deck Legality，包括其他构筑限制、特殊规则以及合法性检查结果的数据结构，不在本节展开，后续单独建立相关章节。

Deck Legality 与运行中的 Game State 合法性检查也属于不同概念，不应合并。

---

## 4.4 Shuffle

**官方术语：Shuffle**

`Shuffle` 是对一个合法目标 Zone 中 Card 顺序进行随机重排的通用规则操作。

因此规则概念不限定为：

```python
shuffle_deck()
```

Game Preparation 中 Shuffle 的目标是双方各自的 Deck：

```text
P1 Deck → Shuffle
P2 Deck → Shuffle
```

其他规则或 Card Effect 也可能要求对其他合法 Zone，例如 Stock，执行 Shuffle。

因此：

```text
Shuffle
≠ 只能作用于 Deck
```

同时：

```text
Ordered Zone
≠ 一定可以合法执行 Shuffle
```

一个 Zone 是否能够成为某次 Shuffle 的合法目标，应由规则和当前处理上下文决定。

长期通用接口可以考虑：

```python
shuffle_zone(...)
```

但本节不锁定最终函数签名。

### 4.4.1 Game Preparation 中的 Shuffle

双方 Deck 通过合法性检查后，对双方 Deck 执行 Shuffle。

完成后继续随机确定 Starting Player。

```text
Deck Legality
        ↓
Shuffle
        ↓
Determine Starting Player
```

实体游戏中为了保证随机性而存在的玩家之间再次洗切等物理操作，不需要在模拟器中机械复制；模拟器需要保证 Shuffle 本身满足规则要求的随机重排语义。

### 4.4.2 Shuffle 与 RNG

Shuffle 的规则语义与 RNG 的具体实现分开。

本节只要求：

```text
Shuffle
→ 合法地随机重排目标 Zone 中 Card 的顺序
```

具体：

- RNG 类型；
- seed；
- 随机数调用顺序；
- Replay 的确定性重现；

留待相应基础设施章节确定。

---

## 4.5 Initial Hand

**官方术语：Initial Hand**

每名 Player 从自己的 Deck 抽取 5 张 Card，这些 Card 形成该玩家的 Initial Hand。

规则语义：

```text
Deck Top
   │
   │ Draw × 5
   ▼
Hand
```

因此：

```text
Initial Hand
≠ 独立 Zone
```

它是 Game Preparation 中，对首次抽取 5 张 Card 后 Hand 状态的规则称呼。

本节不规定双方形成 Initial Hand 时必须具有一个人为指定的先后执行顺序；如果 Replay 或实现确定性需要固定内部执行顺序，应将其视为实现规则，而不是擅自解释为官方流程顺序。

### 4.5.1 Initial Hand 不作为长期重复状态

正式游戏开始后，不需要在 Player State 中额外长期保存：

```python
initial_hand
```

当前实际手牌仍然由：

```text
Hand
```

表示。

但 Initial Hand 的形成过程必须具备可追溯性。

因此未来 Replay、日志、调试、统计或规则接口需要查询 Initial Hand 时，应能够通过历史记录或 Replay 恢复相关信息。

本节不决定未来是否建立：

```python
get_initial_hand(player_id)
```

以及该接口最终通过 Replay、事件记录还是缓存实现。

---

## 4.6 Mulligan

**官方术语：Mulligan**

Initial Hand 形成后，每名玩家各有一次 Mulligan 处理。

执行顺序：

```text
Starting Player
        ↓
另一名 Player
```

每名 Player 的处理：

```text
从 Hand 中选择任意数量 Card
        ↓
所选 Card → Waiting Room
        ↓
从 Deck 抽取相同数量 Card
        ↓
该 Player 的 Mulligan 完成
```

### 4.6.1 选择数量

玩家可以选择：

```text
0 .. 当前 Hand 中的 Card 数量
```

因此选择 0 张也是合法结果。

选择 0 张不表示 Mulligan 尚未处理；该玩家的这一次 Mulligan 机会仍然完成。

### 4.6.2 每名玩家只能进行一次

每名 Player 在 Game Preparation 中只能进行一次该 Mulligan 处理。

因此是否完成 Mulligan 不能仅通过：

```python
len(selected_cards) > 0
```

判断。

项目需要能够表达：

```text
该 Player 的 Mulligan 是否已经完成
```

具体状态结构本节暂不锁定。

### 4.6.3 区域移动顺序

Mulligan 的顺序必须保持：

```text
Hand
→ Waiting Room
→ 然后 Draw 相同数量
```

不能改成：

```text
先 Draw
→ 再将旧 Card 放入 Waiting Room
```

被选择的 Card 进入 Waiting Room 后，不存在一个自动将这些 Card 洗回 Deck 的 Mulligan 步骤。

### 4.6.4 程序命名候选

当前可以保留或考虑：

```python
MulliganAction
MulliganOptions

mulligan_player_id
mulligan_completed
selected_card_ids
```

其中官方规则语义已经确定，但最终 Action 与状态结构留待 Action 系统统一设计。

---

## 4.7 Game Preparation 完成

当双方都完成 Mulligan 后，Game Preparation 的准备流程结束。

这一边界表示：

```text
双方完成 Mulligan
        ↓
Game Preparation 完成
        ↓
准备进入正式 Turn Flow
```

本节不因为这个边界而提前要求建立：

```python
setup_complete: bool
game_started: bool
```

如果未来状态机本身能够唯一表达当前是否仍处于 Game Preparation，就不应重复保存能够推导出的布尔状态。

---

## 4.8 游戏开始与第一个 Turn

Game Preparation 完成后：

```text
Starting Player
→ becomes Turn Player
```

因此：

```python
turn_player_id = starting_player_id
```

随后开始该 Player 的第一个 Turn。

```text
Game Preparation Complete
        ↓
turn_player_id = starting_player_id
        ↓
Starting Player 的第 1 个 Turn
        ↓
进入第 5 节 Turn Flow
```

`starting_player_id` 不因为第一个 Turn 开始而删除或改写。

二者具有不同生命周期：

```text
starting_player_id
→ 本局固定属性

turn_player_id
→ 当前流程状态
```

第一回合中存在的特殊规则不在本节展开，应由 Turn Flow 或具体 Phase 的章节定义。

### 4.8.1 玩家自己的 Turn Count

规则层优先表达：

```text
P1 的第 X 个 Turn
P2 的第 Y 个 Turn
```

而不是把“整局第几个 Turn”作为主要规则状态。

每名 Player 独立具有自己的 Turn Count。

概念方向：

```python
players[player_id].turn_count
```

初始：

```text
P1.turn_count = 0
P2.turn_count = 0
```

某名 Player 的 Turn 开始时：

```text
该 Player 的 turn_count += 1
```

例如 P2 是 Starting Player：

```text
游戏准备完成：
P1 = 0
P2 = 0

P2 第 1 个 Turn：
P1 = 0
P2 = 1

P1 第 1 个 Turn：
P1 = 1
P2 = 1

P2 第 2 个 Turn：
P1 = 1
P2 = 2
```

因此当前 Turn 是该玩家的第几个 Turn，可以由：

```python
players[turn_player_id].turn_count
```

得到。

UI 如果需要显示全局回合编号或其他形式，可以根据底层规则状态和历史信息计算，不要求规则层为了 UI 单独保存一个全局 `turn_number`。

`turn_count` 的最终存储位置留到第 5 节 Turn Flow 决定。

---

## 4.9 本节命名结论

| 中文概念 | 官方术语 | 规范程序名称 | 性质 / 状态 |
| --- | --- | --- | --- |
| 玩家 | Player | `Player` / `player_id` | 官方概念 |
| 玩家内部身份 | — | `PlayerId` | 项目规范 |
| 玩家 1 | — | `PlayerId.P1` | 项目稳定标识 |
| 玩家 2 | — | `PlayerId.P2` | 项目稳定标识 |
| 玩家显示名称 | — | `player_name` | 项目规范，可修改、可重复 |
| 开始游戏的玩家 | Starting Player | `starting_player_id` | 官方概念，对局中保持不变 |
| 回合玩家 | Turn Player | `turn_player_id` | 官方概念 |
| 非回合玩家 | Non-turn Player | 由 `turn_player_id` 推导 | 官方概念 |
| 行动时点 | Play Timing | `PlayTiming` / 具体实现待定 | 官方概念 |
| 主控方 | Master | `master_id` | 官方概念，具体实现待定 |
| 洗牌 | Shuffle | 通用 `shuffle` / `shuffle_zone(...)` 候选 | 官方概念，接口待定 |
| 初始手牌 | Initial Hand | 不建立长期状态字段 | 官方概念，可通过历史追溯 |
| 初始手牌交换 | Mulligan | `MulliganAction` | 官方术语，结构待统一 |
| 当前换牌玩家 | — | `mulligan_player_id` | 项目候选 |
| 换牌完成状态 | — | `mulligan_completed` | 项目候选 |
| Mulligan 所选卡片 | — | `selected_card_ids` | 项目候选 |
| 玩家回合计数 | — | `turn_count` | 项目规范，具体存储待第 5 节确定 |

本节明确不建立含义过宽的：

```python
acting_player_id
```

来替代 Turn Player、Play Timing、Choice、Master 等不同规则概念。

---

## 4.10 本节暂不决定的内容

### 4.10.1 Player 的最终数据结构

本节已经确定：

```text
PlayerId.P1 / PlayerId.P2
→ 对局内部稳定且唯一

player_name
→ 显示名称，可修改、允许重复
```

但暂不决定：

```python
Player
PlayerState
PlayerId
```

最终采用 Enum、dataclass 还是其他结构。

---

### 4.10.2 Play Timing 的具体状态表示

已经确认 Play Timing 不等同于 Turn Player。

但暂不决定是否需要：

```python
play_timing_player_id
```

这样的持久字段，以及 Play Timing 最终如何进入状态机。

---

### 4.10.3 Master 的具体实现

本节只确认 Master 是独立官方规则概念。

`master_id` 最终保存在哪里、哪些对象具有 Master，以及如何查询，留到相关章节决定。

---

### 4.10.4 Deck Legality 的完整规则

Game Preparation 只规定：

```text
Deck 必须先通过合法性检查
→ 才能继续
```

当前最低条件：

```text
Deck = 50 Cards
Climax ≤ 8 Cards
```

完整构筑合法性、特殊构筑限制以及：

```text
DeckLegality
ValidationResult
ValidationError
```

等结构以后单独处理。

---

### 4.10.5 Shuffle 的具体接口与合法性系统

已经确定 Shuffle 是通用 Zone 操作，而不是 Deck 专用概念。

暂不决定：

- 通用 Shuffle 最终函数名和签名；
- 哪些 Zone 默认可以 Shuffle；
- Card Effect 如何使某个 Zone 成为合法 Shuffle 目标；
- 是否建立 `can_shuffle_zone(...)`；
- Shuffle 合法性检查最终位于哪一层。

同时保留：

```text
Ordered Zone
≠
Shufflable Zone
```

这一原则。

---

### 4.10.6 RNG 与 Seed

本节只确定：

```text
Starting Player
→ P1 / P2 等概率，各 50%

Shuffle
→ 合法随机重排
```

暂不决定：

- RNG 类型；
- seed；
- 随机调用顺序；
- RNG 状态保存；
- Replay 如何保证确定性重现。

---

### 4.10.7 Initial Hand 的历史接口

Initial Hand 不作为 Player State 中的长期重复状态保存，但其形成过程必须能够通过 Replay / History 追溯。

暂不决定未来是否建立：

```python
get_initial_hand(player_id)
```

以及查询采用 Replay 重建、事件查询还是缓存。

---

### 4.10.8 Mulligan 的最终 Action / 状态结构

Mulligan 的规则语义已经确定。

暂不锁定：

```python
MulliganAction
MulliganOptions
mulligan_player_id
mulligan_completed
selected_card_ids
```

最终的数据结构和所属模块。

---

### 4.10.9 `turn_count` 的具体存储位置

已经确定使用“某 Player 的第几个 Turn”作为主要规则语义。

建议方向：

```python
players[player_id].turn_count
```

但最终属于 `PlayerState`、Turn State 还是其他结构，由第 5 节决定。

---

### 4.10.10 Game Preparation 与正式游戏之间的状态机实现

规则边界已经确定：

```text
Game Preparation
        ↓
双方完成 Mulligan
        ↓
Starting Player becomes Turn Player
        ↓
第一个 Turn 开始
```

但不提前锁定：

```python
game_started
setup_complete
```

等状态字段。

如果未来状态机能够唯一表达该流程状态，就不重复保存能够推导出的信息。
