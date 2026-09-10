### 1.2 官方概念与项目概念

官方概念来自 WS 官方规则，例如 Type、Zone、Stage Position、Phase、Step、Ability、Effect、Rule Action、Owner、Master 等。对于这些概念，原则上优先使用官方术语。

项目概念是为了实现模拟器而建立的软件抽象，例如 `Card`、`GameState`、`Action`、`Continuation`、`GameEvent`、`Replay` 等。项目概念不要求在官方规则中存在同名术语，但必须保持明确，并避免与官方术语冲突。

当项目概念与官方术语同名时，官方术语优先保留，项目概念增加限定词。例如：

```text
Event
→ 官方规则中的事件卡概念

GameEvent
→ 模拟器中已经发生的游戏事件
```

