### 1.1 命名类别总览

<!-- SECTION_NAV_START -->
← 上一节 | [返回本章目录](README.md) | [下一节 →](02_official_and_project_concepts.md)
<!-- SECTION_NAV_END -->
本项目中的概念分为七个主要领域：卡片、玩家、场地、游戏流程、能力与结算、玩家操作、模拟器基础设施。

| 领域 | 中文类别 | 官方概念 | 程序规范 | 主要用途 |
| --- | --- | --- | --- | --- |
| 卡片 | 卡片实例 | — | `Card` | 表示本局游戏中实际存在的一张卡 |
| 卡片 | 卡片定义 | Card Information | `CardDefinition` | 保存卡片自身的定义信息 |
| 卡片 | 卡片种类 | Type | `CardType` | 区分角色卡、事件卡和高潮卡 |
| 卡片 | 卡片状态 | State | `CardState` | 表示 Stand、Rest、Reverse 等状态 |
| 玩家 | 玩家 | Player | `Player` / `PlayerState` | 表示玩家及其当前游戏状态 |
| 玩家 | 所有者 | Owner | `owner` / `owner_id` | 表示 Card 的固定拥有者；由游戏开始时该 Card 属于哪名 Player 的 Deck 决定 |
| 玩家 | 主控方 | Master | `master` / `master_id` | 表示 Card、Ability、Effect 等对象按官方规则确定的当前 Master |
| 玩家 | 玩家控制关系 | 项目概念 | `PlayerControl`（候选） | 表示特殊效果使一名 Player 代替另一名 Player 作出游戏决定 |
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

<!-- SECTION_NAV_START -->
← 上一节 | [返回本章目录](README.md) | [下一节 →](02_official_and_project_concepts.md)
<!-- SECTION_NAV_END -->
