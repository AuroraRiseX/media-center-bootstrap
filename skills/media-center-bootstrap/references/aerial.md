# Aerial（电视桌面）

官方：https://github.com/pengchujin/aerial-tv ，网站：https://aerial.qust.me/ 。

在目标电脑克隆官方仓库，阅读其当前 README 与 tools/install.sh；使用它配套的安装/恢复工具，而不是使用本机早期复制的安装脚本。检测电视 SDK/ABI、厂商、原 HOME 包名和 ADB 授权。

官方工具的一般入口：在官方仓库根目录运行 `TV=TV_IP tools/install.sh`；guard、lite 等参数须以当时版本文档和设备系统为准。标准 HOME 无法生效时再按官方流程启用 Home Guard，遇到辅助功能或其他授权按工具确认要求处理。不要自动卸载/禁用原厂桌面。

验收：按 Home 进入 Aerial；待机唤醒及重启后仍可进入；遥控焦点可移动；Nuvio/ClashFest 入口能打开。回退使用同一官方版本的 tools/restore.sh，保留可用的原厂 HOME。
