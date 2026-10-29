# 迁移总流程

1. 在新电脑用自己的 GitHub 身份克隆私密仓库。不要将仓库或凭证转公开。
2. 盘点电脑 OS/CPU、电视 IP、Android SDK/ABI、ADB 授权。仅从官方仓库下载适配的安装包。ADB/VPN/辅助功能等系统提示由用户按当前工具规则处理。
3. 按 ClashFest/Aerial 文档安装，记录原 HOME，保留系统桌面及回退入口。
4. 从官方 Nuvio 下载电脑/电视对应版本，登录目标新账号，选择实际个人资料。账号密码不作为 Skill 参数保存。
5. 准备 TMDB key 文件（权限 600），以及 required-private-sources.json 指明的源的新账号配置。服务代码需要 Mac 的 CoreFoundation；Windows/Linux 不能不经适配就直接执行此版本。
6. 运行 prepare_mac.py，先生成暂存文件。检查 `${PRIVATE_SOURCE_*}`、`${SECRET_REQUIRED}`，完成新的来源配置。不要把旧用户路径复制到新机器。
7. 备份并退出 Nuvio，再应用配置和部署目录服务。Mac 仅本机访问用 127.0.0.1；电视访问选择明确的局域网 IP。电脑必须保持开机和同网。安装后通过应用刷新/安装插件并正常保存到新账号，重启确认未被云端覆盖。
8. 电视在“集合导入”导入经替换的 TV 集合，启用现代布局、FOLLOW_LAYOUT，导入 layout.json 对应栏目顺序；详细见 tv-layout.md。先通过本机服务 /health 和 /manifest.json 验证，再从电视实际访问。
9. 验证中文目录、地区/类型筛选、第一/随机封面策略、原播放 ID、继续观看、影片播放和遥控操作。外部流媒体/源是否能播放取决于用户自己的授权与第三方服务。
