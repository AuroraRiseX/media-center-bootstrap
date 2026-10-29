---
name: media-center-bootstrap
description: 在换电脑或更换 Nuvio 账号时，迁移此仓库中的 Mac/Android TV 影音配置，安装和验证 Aerial、ClashFest、Nuvio，部署中文目录服务与电视首页集合。
---

# 影音中心部署与迁移

先读 [迁移流程](references/migration.md)，确认目标操作系统、电视 Android 版本/ABI、ADB 连接、新账号及目录服务运行位置。此 Skill 不会继承创建仓库时的设备或账号操作授权。

- ClashFest：[安装说明](references/clashfest.md)。
- Aerial：[安装说明](references/aerial.md)。
- Nuvio：[迁移说明](references/nuvio.md)，电视效果及已知限制见 [电视布局](references/tv-layout.md)。

当前实际配置以 assets/mac-profile.json 和 assets/tv/collections-new.json 为准，不使用早期 36 文件夹版本覆盖较新的 26 地区布局。保留源 ID、播放 ID 与中文元数据的关联。

使用 scripts/prepare_mac.py 先在暂存目录生成配置，确认缺失凭证与占位符后再应用。不要导入旧账号认证文件、观看历史或用户 ID。新账号须登录新账号后选择实际 profile 索引，不能假定永远是 1。

电视不能使用 127.0.0.1 访问电脑服务：显式使用 --base 指定电视能访问的服务电脑地址；选择 LAN 监听前说明作用范围。云同步可能覆盖直接写入的设置，应通过应用正常导入/安装流程完成账号同步，不能把文件写入成功当作新账号迁移成功。

只有在接口可访问、目录返回内容、封面对应正确影片、重启后设置仍保留、电视遥控和播放测试通过后，才报告完成；未获得窗口或设备访问时明确列出未验收项。桌面悬停弹窗不等于 TV 全屏焦点背景联动。
