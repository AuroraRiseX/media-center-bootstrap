# 历史可选：Mac 托管模式

当前电视本机方案见 android-tv.md 和仓库 README，以下仅适用于主动选择电脑托管的情况。

# Nuvio 配置与目录服务

官方电脑版：https://github.com/NuvioMedia/NuvioDesktop/releases
官方 TV：https://github.com/NuvioMedia/NuvioTV/releases
官网：https://nuvio.tv/

assets/mac-profile.json 导出当前账号 profile 1 的插件、仓库、集合、栏目及外观偏好，不包含认证与观看记录；新目标索引通过 --profile 指定。assets/catalog-service 包含实际运行服务的源代码与完整目录查询配置；assets/tv 是较新的电视布局及素材。私有源占位符清单见 assets/required-private-sources.json，旧账号专属服务需在新账号重新配置。

运行 `python3 scripts/prepare_mac.py --output /tmp/nuvio-stage --profile 1 --base http://127.0.0.1:17863`。先检查输出，不直接覆盖正在运行的应用。`--apply --tmdb-key-file /path/to/private-key` 才会备份并部署本机文件及 LaunchAgent，默认仅回环监听。电视模式另传 `--listen LAN_IP`，并使用 `--base http://LAN_IP:17863`；IP 必须是新电脑实际可达地址。该参数暴露的是只读目录/素材，不是播放代理。Mac 服务依赖 Python3、curl、CoreFoundation。

新账号：先登录，在应用插件页面安装新服务的 /manifest.json，把中文元数据插件排在合适优先级，导入集合，正常保存设置并等待账号同步。不要移植旧会话或把基于旧版本 JAR 的临时 JNI 同步工具当作跨版本安装方案。原生 UI 不可访问时将安装清单交付给用户完成必要登录/导入，不声称全自动验收。

服务必须在目标电脑持续运行，手机/电视上 127.0.0.1 是设备自己，不是电脑。海报及译文依赖 TMDB 数据，缺失中文时保留原文，不编造译名。目录可访问不代表播放源已授权或可以播放。

快照保留 7 个插件仓库和 192 个源的清单/开关；缓存的第三方 JavaScript 不重新分发，须在新应用中刷新仓库重新下载。私有源占位符可能包括需要核对的长配置 URL，先按 host 检查，不应盲目删除。
