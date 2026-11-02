# 当前电视布局与图片规则

真源为 assets/tv/collections-new.json、layout.json 与 android-tv/assets/catalogs.json；基于2026-11-01原机快照，取代旧Mac依赖的6集合/118目录方案。

首页：继续观看（Nuvio自身功能、历史不导出）+7集合+热门电影/剧集。7集合依次为精选推荐、流媒体平台、类型精选·电影、类型精选·剧集、地区电影、制片厂、年代佳片。集合全部 FOLLOW_LAYOUT，pinToTop，启用全部标签；每个文件夹的所有布尔选项以JSON为准。

文件夹横版 LANDSCAPE，focusGifEnabled=false，focusGlowEnabled=true；viewMode=FOLLOW_LAYOUT 沿用Nuvio现代首页，焦点背景和简介由Nuvio渲染。插件只提供元数据/图片，无法通过它新增悬浮加载按钮。更多由第二页目录行和集合末尾的更多文件夹实现，平台通常电影/剧集各两行。

地区26个：CN、HK、TW、US、GB、FR、DE、IT、ES、PT、NL、SE、NO、DK、PL、RU、TR、IN、TH、JP、KR、BR、MX、AU、CA、IE。查询用with_origin_country，合拍片可交叉，绝不在失败时回退到不相关热门列表。

地区/类型/精选文件夹：/art/<catalog-id>.jpg 从真实当前目录随机选片，8秒窗口保持同一影片，优先background，回退poster；no-store。与最初“第一部电影”方案相比，当前采用随机推荐片，非国旗。图片的 X-Source-Movie 标明来源影片ID。

平台：保留品牌Logo和名称；上游平台目录保留原顺序、IMDb ID，查TMDB中文资料并核对影片ID，再补充中文片名/简介/背景；必要时去掉英文clearlogo，缺少中文则保留原文。原语言不等于片单地区，平台不是国家分类。

制片厂/年代：具体封面、heroBackdropUrl、titleImageUrl、hideTitle等按JSON引用；Logo既有本机/assets资源也有第三方HTTPS资源。打包19张本地图像，在线图像仍需网络。旧custom-home-video中的国旗素材是兼容旧Mac模板的历史资源，当前电视地区集合不引用它们。

继续观看聚焦展示由Nuvio现代布局实现，插件不导入历史也不替代播放源。Desktop版悬停弹窗与TV全屏焦点效果不同。

136个目录的基础/分页参数、类型ID、公司ID、年份区间在catalogs.json中。API key单独写入电视私有目录，不进入配置JSON或APK。
