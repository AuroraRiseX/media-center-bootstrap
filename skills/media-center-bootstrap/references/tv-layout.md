# 小米电视端 Nuvio 移植、文件夹大图与更多行

本目录记录把 Mac 上的 Nuvio 配置搬到小米电视（`com.nuvio.tv`，Android TV 14，
<TV_IP>），并把「点进 Apple TV / Netflix / 地区等文件夹」后的页面改成参考图的效果。

## 最终效果

- 电视端 11 个扩展全部可用；本地中文精选目录通过 Mac 局域网服务加载，
  共 **118 个目录**（59 个基础目录 + 每个目录 1 页「更多」）。
- 首页保持：6 个精选集合置顶 + 热门电影 / 热门剧集 两行（现代视图，8 行，其余 229 个目录行隐藏）。
- **点进任意文件夹**后：
  - 顶部固定显示当前选中影片的背景大图、标题、类型、时长、上映日期、评分和中文简介；
  - 底部左右切换影片时，顶部信息实时跟着切换；
  - 下方是该文件夹的影片行，卡片为横版大图；
  - 每个文件夹是 **2 行**：基础行 + 一行「更多」（例如「Netflix · 电影」「Netflix · 电影 · 更多」），
    流媒体平台文件夹为 4 行（电影/剧集各 2 行）；向下滚动可以继续找更多影片，顶部大图保持不变。
- **地区电影 26 个国家/地区**：内地、香港、台湾、美国、英国、法国、德国、意大利、
  西班牙、葡萄牙、荷兰、瑞典、挪威、丹麦、波兰、俄罗斯、土耳其、印度、泰国、
  日本、韩国、巴西、墨西哥、澳大利亚、加拿大、爱尔兰。
- 地区封面不再固定：每个地区从当前推荐影片中随机取一部，取它的背景图/海报。
  服务端每次请求随机选择并返回 `no-store`，所以每次重新加载/重启应用封面都会变。
- 行标题不再出现重复的「- 电影」「- 剧集」后缀。

参考图 `nuvio-home-customization/video-reference/frame-03/04/05.jpg` 的顶部大图行为已复现。

## 关于「右下角显示更多按钮」

Nuvio 电视版 1.0.0 的界面里没有可配置的「增加行」按钮：文件夹页的每一行来自一个目录源，
行末尾也没有「加载更多」磁贴（已实测滚到行尾确认）。要新增一个悬浮按钮必须改 App 本身，
仅靠账号配置或插件数据做不到。

因此这里用**原生可达的最接近方案**实现需求 1：给每个文件夹配置多页来源，
一进文件夹就有 2 行（平台 4 行），可以向下滚动浏览更多影片，顶部焦点大图保持不变；
新增的「更多」行是按页加载的（TMDB 第 2 页、平台列表 offset 20），不会重复第一页内容。

## 之前的两个问题

1. **找不到扩展**：电视端扩展地址是 `http://127.0.0.1:17863`，在电视上指向电视自己，
   所以显示「目录：0」；集合里引用 `local.nuvio.curated.zh` 的文件夹全部报「找不到扩展」。
2. **文件夹页没有顶部大图**：收藏的查看模式是「行」，点进去只有普通标题 + 影片行。
   另外地区封面用的是 `http://127.0.0.1:17863/art/...`，电视上同样打不开。

## 改动一：目录服务改为局域网可访问（Mac 侧）

- 服务：`~/Library/Application Support/Nuvio/custom-catalog-service/server.py`
- 监听：`0.0.0.0:17863`，由 LaunchAgent `local.nuvio.curated-catalog` 自动拉起。
- 新增 `/assets/<file>`：提供本地 logo / 封面；`/art` 改为随机取片并 `no-store`。
- 目录支持「更多页」：`catalog()` 读取 `page`，`localized_platform()` 读取 `skip_offset`。
- 电视端扩展地址：`http://<CATALOG_HOST>:17863`。
- Mac 端 `nuvio_addons.properties`、`nuvio_collections.properties` 里的
  `127.0.0.1:17863` 已同步改成 `<CATALOG_HOST>:17863`。

## 改动二：文件夹页改为「跟随首页布局」

Nuvio 电视版的收藏有「查看模式」：标签 / 行 / **跟随首页布局**。
只有 `viewMode: FOLLOW_LAYOUT` 会让文件夹详情页沿用首页的现代布局：
顶部焦点区块跟随当前选中影片，左右切换实时刷新，下方行使用横版大图卡片。

6 个收藏全部设置为 `FOLLOW_LAYOUT`，Mac 与电视两端一致。

配套设置（电视端界面）：

- 设置 → 布局 → 首页布局：开启，现代视图；
- 设置 → 布局 → 首页内容 → **显示目录类型：关闭**；
- 恢复「流媒体平台」文件夹顺序为 Netflix、Disney+、Prime Video、Apple TV+、HBO Max。

## 改动三：每个文件夹多页、多行

- `build_catalogs.py` 为 59 个基础目录各加一个 `-p2`「更多」目录：
  - TMDB 目录：同一筛选条件换 `page=2`；
  - 平台目录：同一上游列表取 `skip_offset` 20。
- `apply_regions_and_rows.py` 在每个文件夹的每个来源后追加一个 `-p2`，
  来源标题写成「xxx · 更多」（电视直接显示这个标题），并清掉旧配置里残留的 `-p3`。
- 结果：普通文件夹 2 行，平台文件夹 4 行；所有界面都不再出现「更多 2」；
  首页仍只有 8 行（新增目录全部在首页禁用）。
- `warm_cache.py` 预取全部 177 个目录和 26 张地区封面，避免电视首次打开时等待。

## 改动四：制片厂标题单行 + 封面统一

哥伦比亚影业、二十世纪影业的标题原来会折成两行，压住封面左侧的 logo。现在：

- 标题缩短为「哥伦比亚」「二十世纪」，和其它制片厂一样单行显示，不再折行；
- 封面恢复为原来的剧照 + logo（tvflix 原图），和环球影业、派拉蒙等保持同一风格；
- 标题在底部、logo 在中部，二者不再重叠。

服务目录里旧的 `studio-columbia.png` / `studio-20th.png` 已删除，不再使用。

## 改动五：地区扩充 + 随机封面

- 地区从 8 个扩到 26 个（见上），每个地区 3 行。
- `/art/country-XX.jpg` 每次随机选该地区一部影片的背景图（没有背景图用海报），
  返回 `Cache-Control: no-store`；同一个 8 秒窗口内封面和顶部大图保持同一部片，
  之后重新加载/重启应用就会换一部（实测连续请求、重启前后封面均不同）。
- 地区文件夹的封面和焦点背景都用这个地址，所以首页卡片和顶部大图都会跟着变。

## 改动六：每行末尾的「更多」卡片

每个收藏（精选推荐、流媒体平台、类型精选、地区电影、制片厂、年代佳片）的文件夹列表末尾，
新增一个标题为「更多」的文件夹卡片（加号图标封面）：

- 卡片放在该行最右侧，点开是「跟随首页布局」的文件夹页，顶部焦点大图和其它文件夹一致；
- 页面里为该收藏下每个文件夹各放一行「下一页」内容：
  精选推荐 4 行、流媒体平台 10 行、类型精选 8 行、地区电影 26 行、
  制片厂 6 行、年代佳片 5 行；
- 行标题沿用「xxx · 更多」，可以向下滚动找更多影片。

对应实现：`apply_regions_and_rows.py` 的 `more_folder()`，封面是
`custom-home-zh/more-cover.png`（加号图标）。

## 插件源连通性检查（2026-10-28）

电视的插件页里有 7 个仓库、192 个提供者，每个提供者都自带「测试」按钮和诊断面板。
本轮做了这些检查：

- 用电视自带的「测试」逐个跑源，诊断面板会显示 scraper 类型、测试片（TMDB 603《黑客帝国》）
  和结果（例如 `Result: 9 streams` / `Result: 0 streams`）；
- 用电视侧 `toybox nc` 探测 192 个提供者的 269 个主机、7 个仓库清单地址、10 个扩展宿主
  的 443/17863 端口。

结果：

| 源 | 电视测试结果 | 处理 |
| --- | --- | --- |
| 4KHDHub | 16 个流 | 保留 |
| UHDMovies | 9 个流 | 保留 |
| NetMirror | 0 个流 | 已关闭 |
| MoviesMod | 0 个流 | 已关闭 |
| MalluMV | 0 个流（测试片不匹配也会 0） | 暂不关闭 |
| 其余 187 个 | 未逐个测试 | 未改动 |

- 10 个扩展宿主、7 个仓库清单从电视侧全部可达；本地目录服务正常。
- 269 个提供者主机从电视侧 TCP 全部可达（电视走代理），没有 DNS/网络层失败；
  所谓「连接不上」更像是源站自身失效或片库没有测试片。
- 电视 App 没有「批量测试」，192 个提供者只能逐个点；且测试固定用一部电影，
  动画/地区类源天然可能返回 0 流，因此没有按「0 流」批量关闭，避免误关可用源。
- 过程中曾误触 Yoru's Repo 的总开关，已恢复为开启；其原本单独关闭的 1 个提供者被重新启用。

脚本：

- `plugin_audit.py`：从 Mac 的插件状态中提取每个源的主机并做 HTTP 探测（Mac 网络环境参考用）。
- `tv_provider_test.py`：在电视插件页上聚焦「测试」按钮、运行测试并读取结果（半自动）。

## 怎么改电视（不用遥控器逐项点）

电视打开「设置 → 内容与发现 → 扩展 → 从手机管理」后，电视会在
`http://<TV_IP>:8080` 提供配置页；脚本直接调用它的接口：

```bash
# 0)（只在改了目录列表/数量时需要）重建目录并预热
python3 build_catalogs.py
python3 warm_cache.py

# 1) 重建收藏：26 个地区、每个文件夹追加「更多」行（写 Mac 配置 + collections-new.json）
python3 apply_regions_and_rows.py

# 2) 把收藏推给电视（会弹确认框）
python3 push_tv_config.py --tv <TV_IP> --addon http://<CATALOG_HOST>:17863 \
  --collections collections-new.json

# 3) 应用重启拉取新目录后，把首页隐藏到只剩 8 行（会弹确认框）
python3 push_tv_config.py --tv <TV_IP> --addon http://<CATALOG_HOST>:17863 \
  --layout layout.json
```

常用补充：

```bash
# 扩展地址 / 收藏封面里的 127.0.0.1 改成局域网地址
python3 push_tv_config.py --tv <TV_IP> --addon http://<CATALOG_HOST>:17863

# 所有文件夹页启用「跟随首页布局」并恢复平台顺序
python3 push_tv_config.py --tv <TV_IP> --addon http://<CATALOG_HOST>:17863 \
  --view-mode FOLLOW_LAYOUT --folder-order platform-order.json
```

每次会弹出电视确认框「确认扩展与目录更改」，用遥控器选「确认」即可；
脚本会轮询结果并保存改动前后的快照（`tv-state-*.json`）。

想改回普通「行」视图：把 `--view-mode FOLLOW_LAYOUT` 换成 `--view-mode ROWS`。

## 文件说明

| 文件 | 用途 |
| --- | --- |
| `server.py` | 目录服务（局域网 + `/assets` + 随机封面 + 更多页），已部署到 Nuvio 服务目录 |
| `build_catalogs.py` | 生成 26 个地区目录和每个目录的 `-p2` / `-p3`，写回 `catalogs.json` |
| `apply_regions_and_rows.py` | 重建收藏（地区 26 个、每文件夹追加更多行、行末「更多」卡片、制片厂封面），写 Mac 配置和 `collections-new.json` |
| `push_tv_config.py` | 通过电视「从手机管理」接口改扩展、目录、收藏、查看模式和首页布局 |
| `warm_cache.py` | 预热全部目录与地区封面缓存 |
| `plugin_audit.py` | 从 Mac 插件状态提取源的主机并做连通性探测 |
| `tv_provider_test.py` | 在电视插件页上逐个运行「测试」并读取结果 |
| `layout.json` | 首页目录顺序 / 启用清单（6 集合 + 2 热门） |
| `platform-order.json` | 流媒体平台文件夹顺序 |
| `collections-new.json` | 本次推给电视的完整收藏配置 |
| `screenshots/` | 验收截图 |
| `mac-backup-*/` | 改动前的 Mac 端 properties 备份 |
| `tv-state-*.json` | 电视端配置快照（before/after） |

## 验证记录

- 服务：`/health` → `{"catalogs":177,"listen":"0.0.0.0:17863"}`。
- 电视扩展页：中文精选目录（本机）v1.2.0，`http://<CATALOG_HOST>:17863`。
- 电视 `/api/state`：178 个目录（本地 118 + 其它扩展 60）、8 个在首页启用；
  6 个收藏全部 `FOLLOW_LAYOUT`；地区 26 个文件夹 / 78 个来源，
  平台 5 个文件夹 / 30 个来源。
- 目录分页：`country-TH` 第 1 页「拳霸」、第 2 页「地狱犬」、第 3 页「想爱就爱」，互不重复。
- 随机封面：连续请求 `/art/country-TH.jpg` 返回 3 个不同电影 ID；重启应用后地区封面整体变化。
- 重启电视端应用后，文件夹页仍保持顶部大图 + 多行，说明配置不会被账号同步覆盖。
- 验收截图：
  - `screenshots/before-apple-tv-folder-no-hero.png`：改动前，文件夹页没有顶部大图；
  - `screenshots/apple-tv-folder-hero.png` / `...-switched.png`：Apple TV+ 文件夹与左右切换；
  - `screenshots/netflix-folder-hero.png`：Netflix 文件夹；
  - `screenshots/regions-random-covers-1.png` / `...-2.png` / `...-3.png`：多次加载的地区封面不同；
  - `screenshots/studios-one-line-labels.png`：哥伦比亚 / 二十世纪标题单行、封面与其它制片厂一致；
  - `screenshots/folder-two-rows-only.png`：文件夹只有「基础 + 更多」两行；
  - `screenshots/home-more-card.png`：每行末尾的「更多」卡片；
  - `screenshots/more-page-studios.png`：点开「更多」后的多行页面；
  - `screenshots/home-modern-netflix-row.png`、`home-final.png`：首页现代视图。

## 注意事项

- 电视不在 Mac 本机，目录服务依赖这台 Mac：**Mac 要开机、同一局域网、不休眠**。
- 地址写死为 `<CATALOG_HOST>`。如果 Mac 的局域网 IP 变了，需要重新执行脚本更新地址，
  或在路由器里给 Mac 绑定固定 IP。
- 目录数从 41 扩到 177 后，电视首次刷新扩展会新增很多行；务必执行第 3 步 `--layout`，
  否则首页会把新目录都显示出来。
- 多出来的行是按页取数据，不是「点一下按钮再加载」；如果一定要那个按钮，需要修改电视 App。
- 账号同步不是实时的：其它设备改过配置后，按电视「账户」页提示重启应用；
  本次电视和 Mac 两端配置已改成一致。
- 本地服务只提供目录 / 元数据 / 封面，不做播放抓取；只监听家庭局域网，未暴露到公网。
