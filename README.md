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
- Card JSON、Deck JSON 加载与卡组选择
- 卡组基础合法性验证
- Seed / Shuffle
- Mulligan
- 回合与阶段生命周期基础
- Stand / Draw / Clock Phase
- Main Phase 生命周期与 Action Window
- Main Phase 基础角色出牌
- Main Phase 舞台格交换
- Stage Marker 区域
- Stage overlap
- Zone movement
- Resolution Zone（处理区）
- Resolution Point 基础设施
- Trigger / Pending Effect 基础骨架
- Main Phase Start / End 时点接入 Resolution / Trigger
- Damage Resolution / Damage Cancel
- Level Up / Deck Refresh / Refresh Point
- Damage 中的特殊 Refresh / 败北边界
- Replay / 状态 Hash
- Pygame UI
- `legal_actions()` 基础体系

尚未完整实现的主要部分：

- 角色 Stand / Rest / Reverse 朝向状态
- 真正的 AUTO / Trigger / Pending Effect 选择与结算
- Main Phase Event 卡
- 角色【起】效果
- Climax Phase 的实际使用规则
- Attack Phase / Trigger Step / Counter
- Stock / Memory / Climax 区完整规则
- 非零费用支付
- 完整胜负条件
- 正式玩家 Choice UI
- 完整卡牌能力系统

---

# 总体架构

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
Rule Resolution / Resolution Point
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
> Engine 决定当前允许哪些操作，并在 dispatch 时再次验证。  
> 规则处理与玩家 Action 分离。  
> Replay 必须能够确定性重现比赛。

---

# 回合与阶段生命周期

统一目标：

```text
Turn Start
↓
Phase Start
↓
处理阶段开始时点
↓
Phase Process
↓
处理阶段规则
↓
Player Action Window
↓
legal_actions()
↓
玩家 Action
↓
Resolution Point
↓
若无 Pending Effect → 重新开放 Action Window
↓
Phase End
↓
处理阶段结束时点
↓
Next Phase Start
```

当前生命周期事件包括：

```text
turn_started
phase_started
phase_processed
action_window_opened
phase_ended
```

## Main Phase

Main Phase 已经进一步接入 Resolution / Trigger 时点：

```text
Clock Phase End
↓
Main Phase Start
↓
Resolution Point
↓
收集 Main Start Trigger
↓
若有 Pending Effect → 暂停后续流程
↓
Main Phase Process
↓
Main Action Window
```

普通 Main Action 执行后：

```text
Main Action
↓
Resolution Point
↓
规则处理 / Trigger 收集
↓
Pending Effect ?
├─ 有 → 不开放普通操作
└─ 无 → 重新开放 Main Action Window
```

玩家选择结束 Main：

```text
Main Phase End
↓
Resolution Point
↓
收集 Main End Trigger
↓
若有 Pending Effect → 暂停进入 Climax
↓
Pending 清空后继续
↓
Climax Phase Start
```

为此 Engine 已预留 `pending_resolution_context` 与 continuation 机制。当前真正的效果选择/结算 Action 尚未完成。

### Main Action 的双重合法性边界

`legal_actions()` 负责告诉 UI / AI 当前可以做什么；Engine 的执行入口仍会再次验证。

因此即使绕过 UI 直接 `dispatch()`：

```text
Pending Effect 存在
↓
PlayCard / Swap / AdvancePhase
↓
Engine 拒绝
```

不能依赖 UI 隐藏按钮来保证规则合法性。

---

# 当前 Main Phase 操作

目前已实现：

```text
1. 使用手牌中的角色卡
2. 交换己方两个舞台格
3. 进入高潮阶段
```

计划中的固定规则入口：

```text
使用角色或事件卡
交换舞台位置
使用【起】效果
进入高潮阶段
```

Event 与【起】目前尚未实现。

## 舞台交换

交换对象是两个 Stage slot 的完整内容，而不是单独移动角色。

当前一个 Stage slot 在规则状态上包含：

```text
Stage character area
+
Marker list
```

交换时角色与该格对应的 Marker 整体交换。

`stage_slots_swapped` 是一次原子的舞台交换事件，不通过临时空位模拟，因此不会错误触发 Stage overlap。

交换对应的 `ResolutionContext` 在交换事件产生前建立，因此：

```text
stage_slots_swapped
```

位于本次 Resolution Point 的捕获范围内，可供未来“角色移动到其他舞台位置时”等 Trigger 使用。

---

# Marker

每个 Stage slot 已具有独立 Marker 区域：

```text
stage[slot]
markers[slot]
```

Marker 是实际 Card Instance，不是角色对象上的布尔标记或计数器。

因此一张原本存在于 Deck / Hand / Waiting Room 等区域中的实际卡，可以在规则允许时移动到某个角色下方作为 Marker。

设计原则：

```text
Stage slot
├─ Character：当前最多 1 张
└─ Markers：可以 0..N 张
```

将卡放入 Marker 区不会触发“角色重叠”。

Marker 已进入持久化比赛状态、state hash 与当前 Replay 兼容体系。

---

# legal_actions 与 Action Window

Engine 通过：

```python
session.legal_actions(player_id)
```

描述当前允许的操作。

当前包括 Mulligan / Clock / Main 等阶段的 Options 或 Action。

重要原则：

```text
legal_actions()
→ 描述当前合法操作空间

dispatch(Action)
→ 最终验证并执行操作
```

两者不能互相替代。

当存在 Pending Effect 时：

```text
普通 legal_actions
→ 不开放

直接提交普通 Main Action
→ Engine 同样拒绝
```

未来真正的 Pending Effect Choice 实现后，此时应只开放对应的 Effect Choice Action。

---

# Resolution 与 Pending Effect

当前区分：

```text
Interrupt / 中断型规则
Resolution Point / 结算型规则
```

Interrupt 当前主要处理：

```text
Level Up
Refresh
```

Resolution Point 用于：

```text
Stage overlap
玩家 Main Action 后的规则处理
Trigger 收集
阶段 Start / End Trigger
Pending Effect
```

`ResolutionContext` 保存：

```text
turn_player
non_turn_player
event_cursor
events
turn_player_pool
non_turn_player_pool
```

其中 `event_cursor` 用于保证一个 Resolution Point 只捕获属于当前时点的新事件。

当前 `collect_triggers()` 仍是占位实现，因此真实卡牌 AUTO 尚不会自动加入效果池；但 Engine 已经能够识别“存在 Pending Effect”这一状态并暂停普通 Main 操作。

---

# Stand / Draw / Clock Phase

## Stand

```text
Turn Start
→ Stand Start
→ Stand Process
→ Action Window
→ Advance
→ Stand End
→ Draw Start
```

角色朝向尚未实现，因此 Stand Process 当前为空实现。

## Draw

```text
Draw Start
→ 规则抽 1 张
→ 必要的 Interrupt
→ Draw Process
→ Action Window
→ Draw End
→ Clock Start
```

抽牌可正确触发 Refresh / Level Up 等中断边界。

## Clock

合法选择：

```text
A. 跳过计时 → Main
B. 选择 1 张手牌 → Clock → 抽 2 张
```

两次抽牌之间存在中断检查点，因此 Refresh / Level Up 可以在原子步骤之间介入。

---

# Zone 与移动

主要区域：

- Deck
- Hand
- Waiting Room
- Clock
- Stage
- Marker
- Level
- Stock
- Memory
- Climax
- Resolution Zone

统一约定：

```text
index 0 = Top
最后一个元素 = Bottom
```

区域移动统一通过 `_move_card()` 完成，负责验证、顺序、Stage/Marker slot、原子性和 `card_moved` Event。

---

# Damage / Level Up / Refresh

Damage 使用独立 Resolution Zone：

```text
Deck Top → Resolution Zone
↓
检查 Climax
├─ Hit → Resolution → Clock
└─ Cancel → Resolution → Waiting Room
```

Damage 中 Deck 耗尽时可中断并执行 Refresh，然后继续尚未完成的 Damage。

针对规则书 9.2.2.1 的特殊边界已经测试，包括：

- Damage 中 Deck / Waiting Room 同时为空且无 Climax 的特殊败北
- 已出现 Climax 时完成 Damage Cancel 后再处理后续 Refresh
- 特殊败北后不继续产生 Damage / Refresh / Level Up 修改
- 败北时 Resolution Zone 状态保留
- Replay / state hash 一致性

Level Up 与 Refresh 采用可重新扫描的 Interrupt 模型，每处理一个中断规则后重新判断当前成立条件。

---

# Replay

当前 Replay 记录玩家 Action、Seed、Deck Config 与逐步 state hash。

内部规则处理不会伪装成玩家 Action；Replay 时由原始 Action 确定性重新产生。

当前版本已经包含 Stage Marker 与 Stage Swap 等状态/Action 演进，并继续保留旧版本兼容逻辑。

运行态的 Pending Resolution / continuation 当前尚未作为可中途保存的 Replay 状态；真正实现“等待玩家选择效果并保存/恢复”时需要重新评估 Replay 边界。

---

# UI

正式 UI 为 Pygame UI，旧 UI 已归档。

当前原则：

```text
不属于当前阶段的操作
→ 隐藏

属于当前阶段但缺少必要选择
→ 显示为 disabled

满足条件
→ 正常可用
```

Main Phase 当前 UI 已支持舞台位置选择与交换；舞台选择允许同时选择两个格子，继续选择第三个时取消最早选择的格子，点击已选格可取消选择。

UI 不直接修改 GameState，所有操作仍经 Application → Action → Session / Engine。

---

# 测试体系

测试统一位于：

```text
tests/
```

目前重点覆盖：

- 开局 / Seed / Shuffle / Mulligan
- Deck / Card Definition
- Stand / Draw / Clock / Main 生命周期
- Main Action Window
- Main Start / End Resolution timing
- Pending Effect 对普通 Main Action 的阻断
- Play / Stage overlap
- Stage Swap / Marker
- Zone movement / Card conservation / Atomicity
- Damage / Cancel / Resolution Zone
- Level Up / Refresh / Interrupt
- Replay / Application boundary

Main Phase 使用：

```text
tests/test_turn_main_phase.py
```

专项验证：

```text
Main Start
→ Resolution
→ Main Process
→ Action Window
→ Main Action
→ Resolution
→ Action Window
→ Main End
→ Resolution
→ Climax Start
```

其中 Pending Effect 测试会人工构造 TriggeredEffect，因为真实 `collect_triggers()` 尚未实现。

---

# 下一步方向

当前建议暂时停在 Main Phase 生命周期与 Trigger timing 基础完成的位置。

后续优先方向：

```text
1. Pending Effect 的真实玩家选择与继续结算
2. collect_triggers() 与实际 AUTO 能力
3. CharacterPlayOptions 等 Main legal_actions 完整化
4. 【起】效果
5. Event
6. Climax Phase
7. Attack Phase
```

Pending Effect 完成后，目标流程应为：

```text
Trigger 产生
↓
加入对应玩家 Pending Pool
↓
等待玩家选择 / 强制处理
↓
效果结算
↓
重新收集新 Trigger
↓
直到 Pool 为空
↓
执行 pending continuation
↓
恢复阶段流程或 Action Window
```

---

# 项目目录原则

```text
card/               卡牌静态定义
deck/               卡组定义
tests/              自动测试

cards.py            Card Definition / Instance
deck_loader.py      Deck 加载与验证
zones.py            Zone 定义
engine.py           GameState、Session、阶段与主要流程
rule_resolution.py  规则处理
resolution.py       Resolution / Trigger / Interrupt 基础设施
actions.py          Options 与玩家 Action
application.py      应用层边界
ui/                 当前 UI 与归档 UI
```

所有当前开发文件位于 `New_version`。

`Old_version` 仅供参考。
