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

