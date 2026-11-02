---
name: media-center-bootstrap
description: 迁移和部署 Android TV 的 Nuvio 中文首页、电视本机目录服务、分类与图片规则，并按需安装 Aerial 和 ClashFest。
---

# 影音中心部署与迁移

当前优先方案：目录运行在电视本机，电脑只用于部署。先读仓库根README与 [电视服务](references/android-tv.md)、[显示规则](references/tv-layout.md)。以android-tv/assets/catalogs.json及assets/tv/collections-new.json、layout.json为真源；不要用旧Mac模板覆盖7集合/136目录布局。

检查ADB目标、ABI、Android版本、Nuvio版本/登录资料，以及用户自己的TMDB key文件。使用android-tv/install.py安装服务；通过scripts/apply_tv_layout.py预览、备份并在Nuvio原生手机管理界面导入，保留当前账号、观看历史与现有扩展。新目录首次安装会自动启用，需要再次应用隐藏/排序。云同步后重启核查。

电视本机已有服务时使用127.0.0.1:17863；若选择旧Mac托管模式，该地址指向电视自身，须改成Mac可达LAN地址。不要混用两种模式。Mac资料为历史脱敏模板。

启动/待机恢复需保留原辅助功能和通知监听条目，追加本服务；不得覆盖Aerial守护。新设备授权由当前用户指令决定。key、订阅、会话、签名私钥、个人状态备份保存在private/，不要提交公开仓库。

验证health、目录内容、图片对应、中文平台资料、重启、待机和断开电脑目录服务后的独立工作；播放另行测试，不将目录可用等同于播放可用。原机记录不等于新设备已验收。

按需读取：[Aerial](references/aerial.md)、[ClashFest](references/clashfest.md)、[旧Mac迁移](references/nuvio.md)。只在用户选择Mac模式时使用scripts/prepare_mac.py；缺失来源占位符须由使用者提供，不复制原作者账号。
