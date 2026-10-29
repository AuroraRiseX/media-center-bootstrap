# ClashFest（电视）

官方：https://github.com/Nemu-x/ClashFest ，发布：https://github.com/Nemu-x/ClashFest/releases ，文档：https://nemu-x.github.io/ClashFest/ 。执行时重新读取官方说明，不把其他 Clash 分支的包名或权限套用过来。

打开电视开发者选项/网络调试，在用户授权的电视上 `adb connect TV_IP:ADB_PORT`，读取 `adb shell getprop ro.product.cpu.abilist` 与 SDK。运行 scripts/releases.py Nemu-x/ClashFest 列出官方最新包，按 ABI、Android 版本和官方 TV 支持说明选 APK，不把“Android APK”当作必然支持电视遥控。

下载后核对发布源与摘要，`adb -s SERIAL install -r APK_PATH`。不要直接卸载签名不一致的旧包，先备份其用户配置。打开应用，导入用户自己提供的订阅或 YAML，完成 VPN 提示、节点连通测试和按需分流。订阅、节点密码不得进入 Git。无法用遥控完成时先检查官方兼容性，不能宣称已成功。

验收：重启电视后应用可进入、所选节点可连接、Nuvio 目录与影片请求可访问；故障时可关闭 VPN 恢复原网络。不要同时让两个 VPN 客户端争用 Android VPN。
