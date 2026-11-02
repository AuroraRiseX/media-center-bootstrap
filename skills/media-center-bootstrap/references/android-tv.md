# 电视本机目录部署

先按仓库根 README 操作；当前真源是 android-tv/ 和 assets/tv/。电脑仅用于部署，运行不依赖电脑。包名local.nuvio.catalog，版本1.0.0；manifest目录版本1.3.0，ID维持local.nuvio.curated.zh以保留集合关联。

install.py 参数：--serial TV_IP:5555 --catalogs /path/catalogs.json --key-file /path/tmdb-key。仅将key写入应用私有files/tmdb-key（600），不上传任何云端仓库。目录文件files/catalogs.json，cache为可重建资料缓存。

构建需Mac/JDK17/Android SDK34、build-tools34.0.0；build.sh使用javac、d8、aapt、zipalign、apksigner，不需Gradle。private和build被忽略。dist APK含自制Java程序、公开目录规则和图像，不包含用户密钥。它采用本地维护debuggable模式，首次允许用户通过授权ADB配置。

开机：BootReceiver和CatalogGuard确保目录启动。待机：本机小米实测force-stop并移除无障碍服务，因此CatalogRevival利用系统通知监听重绑定，重启本服务并恢复自身CatalogGuard。WRITE_SECURE_SETTINGS仅用于追加自身守护，保留Aerial原条目。启动守护仅监听Nuvio窗口状态，不能读取窗口内容；通知内容不处理、不存储。不能把进程暂时运行当作已完成待机验收。不要替换其他厂商系统组件，也不应为了本服务禁用系统桌面。

HTTP监听仅127.0.0.1:17863，接口health、manifest.json、catalog、meta、art、assets。访问外部TMDB、平台片单和图片使用电视本身网络/VPN。无视频流代理。资料缓存6小时，上游失败回退已有过期缓存。

原机2026-11-01完成：136目录均返回20项、48引用图片路径HTTP200；Mac服务bootout后测试；重启自动启动和云同步不回退；待机强停后进程重建与健康检查通过。未测试完整播放。2026-11-02公开整理时ADB无设备，不宣称再次现场验收。

外部依据：https://github.com/pengchujin/aerial-tv/blob/main/docs/devices/xiaomi-mitv-mftr0.md 。固件变化可能影响系统重绑定，换机须重测。
