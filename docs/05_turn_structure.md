# 5. Turn Structure

本节统一定义一个 Turn 的规则身份、生命周期、Phase 顺序以及 Turn 之间的衔接。

本节主要讨论：

- Turn Player 与 Non-turn Player
- 每名 Player 的 Turn Count
- Turn Start
- Turn 中的 Phase Sequence
- Turn End
- Normal Next Turn
- Additional Turn
- Turn Scheduling
- Player Control 与 Turn Structure 的边界
- Turn Structure 与其他流程系统的接口

本节只确定 Turn 层级的规则语义、命名和流程边界。各 Phase 内部的强制处理与玩家可选操作、Attack Phase 内部结构，以及 Trigger / Resolution 的通用处理逻辑，分别留待后续章节决定。

---

## 5.1 Turn 总体结构

一个 Turn 由当前 Turn Player 按官方规定的 Phase 顺序推进。

```text
确定本次 Turn Player
        ↓
Turn 开始
        ↓
Stand Phase
        ↓
Draw Phase
        ↓
Clock Phase
        ↓
Main Phase
        ↓
Climax Phase
        ↓
Attack Phase
        ↓
End Phase
        ↓
End Phase 满足 Turn 结束条件
        ↓
确定下一 Turn Player
        ↓
下一 Turn
```

其中：

```text
Turn Structure
→ 负责 Turn 身份、生命周期、Phase 顺序和 Turn 之间的衔接

Phase Flow
→ 负责各非攻击 Phase 内部的强制处理、玩家可选操作和结束条件

Attack Phase
→ 负责 Attack Phase 内部的 Attack Sub-Phase、各 Step 与 Encore Step

Trigger / Resolution
→ 负责流程中产生的 Trigger Condition、Ability、Effect、Rule Action、Choice 与结算
```

---

## 5.2 Turn Player 与 Non-turn Player

**官方术语：**

```text
Turn Player
Non-turn Player
```

规范名称：

```python
turn_player_id
```

Turn Player 表示当前 Turn 所属的 Player。

Non-turn Player 表示当前不是 Turn Player 的另一名 Player。当前模拟器为双人游戏，因此可由 `turn_player_id` 唯一推导，不需要额外长期保存 `non_turn_player_id`。

### 5.2.1 Turn Player 是稳定的 Turn 身份

一个 Turn 确立后，`turn_player_id` 在该 Turn 内保持不变。

因此：

```text
Turn Player
≠ Starting Player
≠ Master
≠ 获得 Play Timing 的 Player
≠ 被规则要求作出 Choice 的 Player
≠ 实际提供决定的 Player
```

Play Timing、Choice、Automatic Ability 的处理或 Player Control 本身都不会改变当前 Turn Player。

### 5.2.2 Starting Player 与 Turn Player

`starting_player_id` 在 Game Preparation 中确定并整局保持不变；`turn_player_id` 表示当前 Turn 的规则身份。二者不得合并。

---

## 5.3 Player Turn Count

每名 Player 独立维护自己的 Turn Count。

规范名称：

```python
turn_count
```

定义：

> `turn_count` 表示该 Player 在本局中已经开始过多少个 Turn。

初始：

```text
P1.turn_count = 0
P2.turn_count = 0
```

某名 Player 的一个新 Turn 开始时：

```text
该 Player.turn_count += 1
```

### 5.3.1 Additional Turn 同样计数

Additional Turn 仍然是一个完整 Turn，因此同样使对应 Player 的 `turn_count += 1`。

### 5.3.2 Player Control 不影响 Turn Count

Player Control 不改变 Turn 的归属。P1 控制 P2 的 Turn 时，增加的仍然是 `P2.turn_count`。

### 5.3.3 First Turn 的判断

某 Player 的第一个 Turn 可以由：

```text
该 Player 当前是 Turn Player
+
该 Player.turn_count == 1
```

判断。

因此不需要额外长期保存：

```python
is_first_turn
is_starting_player_first_turn
global_turn_number
```

---

## 5.4 Turn Start

本项目使用 `Turn Start` 描述一个新 Turn 开始的生命周期边界。

Turn Start 不是独立 Phase 或 Step，因此不得建立：

```python
Phase.TURN_START
Step.TURN_START
```

概念流程：

```text
确定本次 Turn Player
        ↓
turn_player_id = 该 Player
        ↓
该 Player.turn_count += 1
        ↓
进入 Stand Phase
```

`turn_count` 必须在该 Turn 开始时相关 Trigger Condition 被处理以前进入正确数值。

### 5.4.1 Turn Start 与 Stand Phase

官方规则中：

```text
「ターンの始めに」
```

与：

```text
「スタンドフェイズの始めに」
```

所表示的 Trigger Condition 在 Stand Phase 开始流程的同一处发生，随后产生 Check Timing。

因此类似：

```text
あなたの第1ターンの始めに
```

这样的 Ability 具有明确规则语义，但不需要建立 `Turn Start Phase` 或 `Turn Start Step`。

程序可以存在类似 `begin_turn(...)` 的状态转换入口，但它表示生命周期操作，而不是新的官方流程层级。

### 5.4.2 Normal Turn 与 Additional Turn 共用同一入口

```text
Normal Turn ───────┐
                   ├→ 统一 Turn Start
Additional Turn ──┘
```

Turn Scheduling 只负责确定下一个 Turn Player，之后统一进入新的 Turn。

---

## 5.5 Phase Sequence

一个 Turn 的官方 Phase 顺序为：

```text
Stand Phase
        ↓
Draw Phase
        ↓
Clock Phase
        ↓
Main Phase
        ↓
Climax Phase
        ↓
Attack Phase
        ↓
End Phase
```

不存在 `Encore Phase`。Encore 是 `Encore Step`，并属于 Attack Phase。

### 5.5.1 Phase、Sub-Phase 与 Step 的层级

Attack Phase 中存在 `Attack Sub-Phase`，其内部包含多个 Step；但 Step 不要求必须从属于 Sub-Phase。

```text
Attack Phase
│
├─ Attack Sub-Phase
│   └─ 各 Attack Step
│
└─ Encore Step
```

Attack Phase 的完整内部结构留到后续 Attack Phase 章节定义。

### 5.5.2 Phase Progression

当前规则下，Phase 按固定顺序推进：

```text
Stand → Draw → Clock → Main → Climax → Attack → End
```

当前没有需要实现的 Phase Skip 规则。

实现时不应让某个 Phase 直接硬编码调用具体的下一 Phase，而应通过统一的 Phase progression 决定后继，以保留未来改变 Phase 顺序或跳过 Phase 的扩展能力。

本节不提前建立 `skip_phase`、`skipped_phases`、`phase_queue` 等状态结构。

---

## 5.6 Turn End

End Phase 与 Turn End 必须严格区分：

```text
End Phase
→ 官方 Phase

Turn End
→ 当前 Turn 生命周期结束的规则边界
```

因此：

```text
Phase.END
≠ Turn End
```

并且不得建立 `Phase.TURN_END`。

### 5.6.1 End Phase 完成后才能结束 Turn

```text
Attack Phase 完成
        ↓
End Phase
        ↓
执行 End Phase 官方流程
        ↓
满足 Turn 结束条件？
        ├─ 否 → 按官方规则继续 / 重新进行 End Phase 处理
        └─ 是 → 允许结束当前 Turn
```

Turn Structure 不负责 End Phase 内部具体处理。第 6 节负责完成其官方流程，并在满足结束条件后允许 Turn Structure 继续 Turn transition。

### 5.6.2 Turn End 与下一 Turn 是连续转换

```text
End Phase 满足结束条件
        ↓
确定 Actual Next Turn Player
        ↓
当前 Turn 完成
        ↓
开始下一 Turn
```

Additional Turn 对下一 Turn Player 的影响发生在这一衔接过程中。

---

## 5.7 Normal Next Turn

没有特殊规则改变下一 Turn Player 时：

```text
当前 Turn Player 的对手
→ 成为下一 Turn Player
```

本项目将这一默认结果称为 `Normal Next Turn Player`。

它是项目概念，不需要作为长期 Game State 保存。在当前双人规则下可由：

```python
other_player(turn_player_id)
```

推导。

### 5.7.1 Normal Next 与 Actual Next

必须区分：

```text
Normal Next Turn Player
→ 默认候选

Actual Next Turn Player
→ 应用 Additional Turn 等规则后的最终结果
```

因此不应假定：

```python
next_turn_player_id = other_player(turn_player_id)
```

永远成立。

Starting Player 不参与正常后继 Turn 的计算。

---

## 5.8 Additional Turn 与 Turn Scheduling

**官方概念：Additional Turn**

本项目统一使用 `Additional Turn` 表示 Card Ability / Effect 产生的追加 Turn。此前暂用的 `Extra Turn` 不再作为规则层规范名称。

### 5.8.1 Additional Turn 改变下一 Turn Player

Additional Turn 的特殊性在于 Turn transition 时改变实际成为下一 Turn Player 的 Player。

Additional Turn 本身仍然是普通完整 Turn，因此目前没有理由建立：

```python
TurnType.NORMAL
TurnType.ADDITIONAL
```

新的 Turn 一旦确立，都进入同一个 Turn Start 流程。

### 5.8.2 多个 Additional Turn

多个 Additional Turn Effect 同时存在时，不能简单建模为普通 FIFO Turn Queue。

官方规则会根据 Additional Turn Effect 的发生关系以及 Turn Player 的选择决定本次应用哪个 Effect；未在本次应用的相关 Additional Turn Effect 可能继续带到下一 Turn。

因此不得直接假定：

```python
additional_turn_queue.append(player_id)
next_player = additional_turn_queue.pop(0)
```

就是完整规则实现。

Additional Turn Effect 的具体存储、发生顺序、Choice 与生命周期由后续 Effect / Resolution 系统定义。

### 5.8.3 Turn Scheduling

本项目将确定实际下一 Turn Player 的通用过程暂称为：

```text
Turn Scheduling
```

它是项目概念，不是官方规则术语。

```text
End Phase 满足结束条件
        ↓
计算 Normal Next Turn Player
        ↓
检查 Additional Turn 等改变下一 Turn 的规则
        ↓
确定 Actual Next Turn Player
        ↓
统一开始新的 Turn
```

因此：

```text
Additional Turn
≠ 特殊 TurnType
≠ 简单 FIFO Turn Queue
≠ Player Control
```

---

## 5.9 Player Control 与 Turn Structure

Player Control 不改变 Turn 的规则归属。

例如：

```text
P1 在 P2 的一个 Turn 中控制 P2
```

仍然：

```text
Turn Player     = P2
Non-turn Player = P1
P2.turn_count 正常增加
```

因此：

```text
Player Control
≠ Turn ownership
```

### 5.9.1 Player Control 只改变决定的提供者

当规则要求 P2 作出 Choice 时，规则主体仍然是 P2；随后由 Player Control 关系决定谁实际代表 P2 提供决定。

```text
Rule identity
        ↓
P2 must choose
        ↓
Decision routing
        ↓
P1 supplies P2's decision
```

Player Control 不改变：

```text
PlayerId
Starting Player
Turn Player
Non-turn Player
turn_count
Owner
Master
Zone 所属玩家
```

### 5.9.2 Player Control 与 Information Visibility

Player Control 不应直接修改 Zone 的基础 `information_visibility`。

控制另一名 Player 时需要的额外信息访问，应理解为为了代表该 Player 作出决定而获得必要访问能力，而不是改变 Zone 本身的信息公开规则。

### 5.9.3 Player Control 的持续范围

Turn Structure 不根据当前 Turn Player 是否相同，自行推断 Player Control 是否继续。

即使：

```text
P2 Turn
        ↓
P2 Additional Turn
```

Player Control 是否延续，也必须由产生该关系的 Effect 的持续范围决定。

---

## 5.10 Turn 与其他系统的接口

### 5.10.1 与 Phase Flow 的接口

```text
Turn Structure
→ 进入某个 Phase

Phase Flow
→ 执行该 Phase 的官方流程

Phase Flow 完成
→ 报告该 Phase 可以结束

Turn Structure
→ 推进到下一 Phase
```

第 6 节负责各非攻击 Phase 中强制做什么、玩家可选做什么以及什么时候完成。

### 5.10.2 与 Attack Phase 的接口

Turn Structure 只识别 `Attack Phase` 这一 Phase 层级，不依赖其内部 Attack Sub-Phase、各 Attack Step 与 Encore Step。

### 5.10.3 与 Trigger / Resolution 的接口

```text
Turn / Phase / Attack Flow
        ↓
产生规则时点或执行规定动作
        ↓
Trigger / Resolution
        ↓
处理完成
        ↓
返回原 Flow
```

流程系统不自行实现另一套 Ability / Effect 结算逻辑。

### 5.10.4 与 Player Control 的接口

规则流程首先确定按规则由哪名 Player 作出决定；Player Control 系统再确定该决定实际由谁提供。

Turn Structure 不把 `controlling_player_id` 保存为 Turn 固有属性。

### 5.10.5 与 Replay 的接口

Turn Structure 中影响 Game State 的变化必须能够被未来 Replay 重现，例如 Turn Player 改变、`turn_count` 增加以及 Additional Turn 改变 Actual Next Turn Player。

Replay 的最终记录格式不在本节决定。

---

## 5.11 本节命名结论

| 中文概念 | 官方术语 | 规范程序名称 | 性质 / 状态 |
| --- | --- | --- | --- |
| 回合 | Turn | `Turn` / 具体状态结构待定 | 官方概念 |
| 回合玩家 | Turn Player | `turn_player_id` | 官方概念 |
| 非回合玩家 | Non-turn Player | 由 `turn_player_id` 推导 | 官方概念 |
| 玩家回合计数 | — | `turn_count` | 项目规范 |
| 回合开始 | — / 规则边界 | `Turn Start` / `begin_turn(...)` 候选 | 项目生命周期概念，不是 Phase / Step |
| 阶段 | Phase | `Phase` | 官方概念 |
| 回合结束 | — / 规则边界 | `Turn End` | 项目生命周期概念，不是 Phase / Step |
| 正常下一回合玩家 | — | `Normal Next Turn Player` / 查询接口待定 | 项目概念，可推导 |
| 追加回合 | Additional Turn | `additional_turn` / 具体结构待定 | 官方概念 |
| 回合调度 | — | `Turn Scheduling` | 项目概念 |
| 实际下一回合玩家 | — | `Actual Next Turn Player` / 临时结果 | 项目概念 |
| 玩家控制关系 | — | `PlayerControl`（候选） | 项目概念，不属于 Turn 身份 |

本节明确：

```text
不得建立：
Phase.TURN_START
Phase.TURN_END

不得把：
Additional Turn
→ 建模为另一种 TurnType

不得假定：
Actual Next Turn Player
→ 永远等于 other_player(turn_player_id)

不得把：
Player Control
→ 实现为修改 turn_player_id
```

并明确：

```text
Encore
→ Encore Step
→ 属于 Attack Phase
→ 不是 Encore Phase

Step
→ 不要求必须从属于 Sub-Phase
```

---

## 5.12 本节暂不决定的内容

### 5.12.1 各 Phase 的内部流程

各 Phase 中强制做什么、玩家可选做什么、什么时候完成，留到第 6 节 Phase Flow 定义。

### 5.12.2 Attack Phase 的内部结构

Attack Sub-Phase、Attack Declaration Step、Trigger Step、Counter Step、Damage Step、Battle Step、Encore Step 及其完整推进规则，留到后续 Attack Phase 章节。

### 5.12.3 Trigger / Resolution 的通用机制

Trigger Condition、Automatic Ability、Check Timing、Rule Action、多个 Ability 的处理顺序、Choice 与 Effect Resolution，统一留到 Trigger / Resolution 章节。

### 5.12.4 End Phase 的完整内部处理

End Phase 的完整处理顺序、重复执行、「ターンの終わり」相关 Trigger Condition、Check Timing、Effect 到期及最终结束判定，留到第 6 节与 Trigger / Resolution 系统。

### 5.12.5 Additional Turn Effect 的具体数据结构

暂不决定 Additional Turn Effect 的存储层、发生顺序、未应用 Effect 的持越方式、多个 Effect 的 Choice，以及是否建立专门 Pending Additional Turn 结构。

### 5.12.6 Turn Scheduling 的最终实现

职责已经确定，但 `determine_next_turn_player(...)`、`get_normal_next_turn_player(...)` 等最终函数名、类结构和模块位置暂不锁定。

### 5.12.7 Player Control 的具体实现

暂不决定 `PlayerControl` 的最终数据结构、`get_decision_maker(...)` 的最终接口，以及 Player Control 的建立、持续、嵌套与解除方式。

### 5.12.8 Player Control 下的信息访问

已经确认 Player Control 不直接修改基础 `information_visibility`。控制另一名 Player 时如何获得完成 Choice 所需的信息访问能力，留到 Information Access / Choice 系统。

### 5.12.9 Phase Skip

当前没有需要实现的 Phase Skip 规则。

只要求 Phase progression 不将具体后继 Phase 硬编码在各 Phase 自身内部。暂不建立 `skip_phase`、`skipped_phases`、`phase_queue`、`phase_override` 等状态。

### 5.12.10 Replay 中的 Turn 表示

Turn Start、`turn_player_id`、`turn_count`、Additional Turn 与 Turn transition 的 Replay 记录格式留到 Replay 章节。

### 5.12.11 UI 中的 Turn 显示

规则层以“某 Player 的第 X 个 Turn”为主要语义。全局 Turn 编号、Additional Turn 标记等 UI 表示不属于 Turn Structure。
