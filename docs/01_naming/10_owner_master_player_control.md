### 1.10 Owner、Master 与 Player Control

必须区分以下三个概念：

```text
Owner
→ Card 的固定拥有者

Master
→ Card、Ability、Effect 等对象按官方规则确定的当前主控方

Player Control
→ 模拟器为特殊效果建立的项目概念：谁实际代替某名 Player 作出游戏决定
```

对 `Card` 而言，`Owner` 由游戏开始时该 Card 属于哪名 Player 的 Deck 决定，并在该局中保持不变。

`Master` 与 `Owner` 不是同义词。Card 的 Master 通常依据其当前所在 Zone 的 Master 确定，因此 Card 进入另一名 Player 的 Zone 后，Owner 可以保持不变，而 Master 按规则改变。

不得使用项目自造的 `Controller` 代替官方 `Master`。

`Player Control` 也不得与 `Master` 合并。例如特殊效果使 P1 在 P2 的一个 Turn 中控制 P2 时：

```text
Turn Player
→ 仍然是 P2

P2 的 Turn Count
→ 正常增加

P2 的 Zone
→ 仍然属于 P2

Card Owner / Master
→ 仍按各自规则判断

实际替 P2 作出游戏决定的 Player
→ P1
```

因此 Player Control 描述的是“谁代替某名 Player 提供决定”，而不是改变被控制 Player 的规则身份或其 Card 的 Owner / Master。

`PlayerControl`、`decision_maker` 等具体程序结构暂不在第一节锁定。
