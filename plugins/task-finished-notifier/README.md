# Task Finished Notifier

Windows 上的 Codex 任务结束提醒插件。主线程触发 Stop 时，在屏幕右下方显示一个独立小窗口并播放系统提示音，8 秒后自动关闭；也可手动关闭。无需第三方 Python 包。

## 安装与启用

源代码位于 `New_version/plugins/task-finished-notifier`。在该目录运行 `powershell -NoProfile -ExecutionPolicy Bypass -File install.ps1`。
安装器把发布副本放入用户个人 marketplace，并运行 `codex plugin add`；不会覆盖已有同名源码目录。
安装后需在 Codex CLI 的 `/hooks` 中审核并信任这个 Stop Hook，再重载 IDE 扩展并开始新对话。
这是 Codex 自身的 Hook 信任要求，安装插件不会自动授予信任。不要绕过信任审核。

手动测试：`python -B scripts/notify.py --test`。
禁用：`codex plugin remove task-finished-notifier@personal`，或通过 `/hooks` 禁用该 Hook。

## 行为边界

- Stop 表示本轮回复停止，并不证明开发目标全部成功；提示文案使用“本轮工作已结束”。其他 Stop Hook 若要求继续，仍可能已经发出提醒。
- 不监听工具调用、子代理结束或用户中断。
- 仅本机弹窗和系统声音；不读取对话文件，不显示或上传提示词和回答。
- Hook 读取标准输入 JSON，启动隐藏控制台的短时通知进程后立即返回 `{}`，不等待用户关闭弹窗。
- 需要 Windows、可从 PATH 调用的 Python、Tkinter 和可交互桌面。系统静音会影响提示音。
- 本轮现有会话是否能热加载插件尚未验证，请以新会话实际触发为准。

官方依据：https://learn.chatgpt.com/docs/hooks 和 https://developers.openai.com/plugins/build/plugins 。
