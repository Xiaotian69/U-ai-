# Unipus Popup Clicker

这是一个本地 Playwright 自动化脚本，用来打开指定的 Unipus 页面，并在普通通知弹窗出现时自动点击“确定”。

脚本不会保存账号密码。第一次运行时，如果网页要求登录，需要你在打开的浏览器窗口里手动登录；之后登录状态会保存在本地 `.browser-profile/` 目录中。这个目录已被 `.gitignore` 排除，不应该上传到 GitHub。

## 文件说明

- `popup_clicker.py`: 主脚本。
- `requirements.txt`: Python 依赖。
- `tests/test_popup_clicker.py`: 单元测试。
- `setup_windows.bat`: Windows 一键安装依赖和浏览器运行时。
- `run_windows.bat`: Windows 一键启动脚本。

## Windows 快速使用

1. 安装 Python 3.10 或更新版本。
2. 双击 `setup_windows.bat`，等待依赖安装完成。
3. 双击 `run_windows.bat`。
4. 如果页面要求登录，在打开的 Chromium 窗口里手动登录。
5. 保持浏览器窗口和命令行窗口不关闭，脚本会持续检测并点击“确定”。

## 命令行使用

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m playwright install chromium
python popup_clicker.py
```

## 可选参数

```powershell
python popup_clicker.py --button-text "确定" --poll-seconds 5
```

常用参数：

- `--button-text`: 要点击的按钮文字，默认是“确定”。
- `--poll-seconds`: 检测间隔秒数，默认是 5 秒，最小为 1 秒。
- `--profile-dir`: 浏览器登录态目录，默认是 `.browser-profile`。
- `--url`: 要打开的页面链接。

## 测试

```powershell
python -m pytest -q
```

## 不要上传的内容

这些内容可能包含本地状态或缓存，已经被 `.gitignore` 排除：

- `.browser-profile/`
- `logs/`
- `.venv/`
- `.pytest_cache/`
- `__pycache__/`
