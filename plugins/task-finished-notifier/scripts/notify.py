"""Windows-only local notification. Hook stdout is always a JSON object."""
import json
from pathlib import Path
import subprocess
import sys


def should_notify(payload):
    return (isinstance(payload, dict)
            and payload.get("hook_event_name") == "Stop"
            and not payload.get("agent_id"))


def launch_popup():
    # No transcript, prompt, or response text is passed to the desktop process.
    subprocess.Popen(
        [sys.executable, "-B", str(Path(__file__).resolve()), "--popup"],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
        close_fds=True,
    )


def popup():
    import tkinter as tk
    import winsound

    root = tk.Tk()
    root.title("Codex")
    root.resizable(False, False)
    root.attributes("-topmost", True)
    width, height = 360, 130
    root.geometry(f"{width}x{height}+{max(0, root.winfo_screenwidth()-width-25)}+{max(0, root.winfo_screenheight()-height-80)}")
    root.configure(bg="#eef5ff")
    tk.Label(root, text="Codex 本轮工作已结束", font=("Microsoft YaHei", 13, "bold"),
             bg="#eef5ff").pack(pady=(18, 5))
    tk.Label(root, text="请返回编辑器查看回复。", bg="#eef5ff").pack()
    tk.Button(root, text="关闭", command=root.destroy).pack(pady=8)
    root.after(8000, root.destroy)
    try:
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except RuntimeError:
        root.bell()
    root.mainloop()


def main():
    if "--popup" in sys.argv:
        popup()
        return
    if "--test" in sys.argv:
        launch_popup()
        print("Notification test launched.")
        return
    try:
        payload = json.load(sys.stdin)
        if should_notify(payload):
            launch_popup()
    except (ValueError, OSError) as exc:
        print(f"Notification skipped: {type(exc).__name__}", file=sys.stderr)
    print("{}")


if __name__ == "__main__":
    main()
