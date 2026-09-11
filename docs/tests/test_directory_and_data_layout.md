# 测试目录与数据布局规范

## 1. 目的

本规范用于统一项目测试目录、测试输入、预期结果与实际输出的组织方式。

本规范只负责测试数据与测试产物的目录布局，不负责定义：

```text
Card JSON 命名规范
正式 cards/ 目录结构
Scanner 的业务逻辑
Validator 的合法性规则
Index 的具体数据格式
```

这些内容应由对应的数据规范或功能规范单独定义。

## 2. 总体目录结构

测试相关数据统一放在：

```text
tests/
```

目录下，并区分为三类：

```text
tests/
├─ fixtures/
├─ expected/
└─ artifacts/
```

其中：

```text
fixtures/
→ 测试输入

expected/
→ 预期结果 / 标准答案

artifacts/
→ 测试运行后的实际输出
```

三者职责必须保持分离。

## 3. fixtures

`fixtures/` 用于保存人工构造或专门准备的测试输入。

例如：

```text
tests/
└─ fixtures/
   └─ scanner/
      ├─ case_01_basic/
      ├─ case_02_empty/
      ├─ case_03_wrong_paths/
      ├─ case_04_multiple_products/
      └─ case_05_extra_depth/
```

每个测试场景应拥有独立的 case 目录。

原则：

```text
统一测试框架
→ 共享 tests/ 结构

独立测试场景
→ 使用独立 fixture case
```

不同 case 之间不应依赖彼此的数据。

## 4. expected

`expected/` 用于保存测试的预期结果。

它表示：

```text
正确结果应该是什么
```

expected 应与 fixture case 保持明确对应关系，并属于长期有效的测试资产，不应被测试运行自动覆盖。

## 5. artifacts

`artifacts/` 用于保存测试运行后的实际输出。

它表示：

```text
程序这一次实际得到了什么
```

artifacts 主要用于：

```text
人工检查
调试
失败分析
结果对比
后续分析
```

### 5.1 当前阶段的保留策略

当前阶段不要求测试结束后自动清除 artifacts。

允许：

```text
保留旧 artifact
新一轮测试覆盖同名 artifact
```

但必须明确：

```text
artifacts
→ 可再生成
→ 不构成项目事实来源
→ 不替代 expected
→ 不作为后续测试输入
```

如果需要长期保存某项测试输入或标准结果，应分别存入：

```text
fixtures/
expected/
```

而不是依赖 artifacts。

## 6. 功能域分类

测试数据应按照被测试功能继续分类。

例如：

```text
tests/
├─ fixtures/
│  ├─ scanner/
│  ├─ validation/
│  └─ index/
├─ expected/
│  ├─ scanner/
│  ├─ validation/
│  └─ index/
└─ artifacts/
   ├─ scanner/
   ├─ validation/
   └─ index/
```

这样可以保持同一功能的 fixture、expected、artifact 具有明确对应关系。

## 7. Case 对应原则

每个测试场景应尽量采用一致的 case 名称。

例如：

```text
fixtures/scanner/case_01_basic/
expected/scanner/case_01_basic.json
artifacts/scanner/case_01_basic.json
```

其关系为：

```text
fixture
→ 给程序什么

expected
→ 正确答案应该是什么

artifact
→ 程序本次实际输出什么
```

case 名称应描述测试场景，而不是只使用无语义编号。

推荐：

```text
case_01_basic
case_02_empty
case_03_wrong_paths
```

不推荐：

```text
case_1
case_2
case_3
```

## 8. 路径表示原则

路径类测试结果统一使用相对路径。

例如保存：

```text
cards/TEST/TE01/TEST_W_TE01_T001.json
```

而不是保存开发机器上的绝对路径：

```text
G:\GPTtest\New_version\tests\fixtures\scanner\...
```

这样可以避免测试结果依赖操作系统盘符、仓库所在目录或开发者本机路径。

## 9. Scanner 测试中的应用示例

Scanner 测试可以构造：

```text
tests/
├─ fixtures/
│  └─ scanner/
│     └─ case_01_basic/
│        ├─ cards/
│        │  └─ TEST/
│        │     └─ TE01/
│        │        ├─ TEST_W_TE01_T001.json
│        │        ├─ TEST_W_TE01_T002.json
│        │        └─ note.txt
│        └─ decks/
│           └─ sample_deck.json
│
├─ expected/
│  └─ scanner/
│     └─ case_01_basic.json
│
└─ artifacts/
   └─ scanner/
      └─ case_01_basic.json
```

其中：

```text
fixtures
→ 构造测试环境

expected
→ 保存应被 Scanner 发现的相对路径

artifacts
→ 保存 Scanner 本次实际输出
```

测试逻辑应比较：

```text
actual result
vs
expected result
```

artifact 只是附加的可观察输出，不应取代自动断言。

## 10. 基本原则总结

本规范最终要求：

```text
tests/
├─ fixtures/   → 输入
├─ expected/   → 标准答案
└─ artifacts/  → 实际输出
```

并遵守：

```text
测试框架统一
每个 case 输入相互隔离
fixture / expected / artifact 职责分离
case 命名保持对应
路径使用相对表示
artifact 当前允许保留和覆盖
artifact 不构成事实来源
```

后续 Scanner、Validator、Index Builder 等测试均应按照这一目录与数据布局规范组织。
