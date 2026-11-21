# NASA APOD — a SwiftBar plugin / NASA 每日天文图 SwiftBar 插件

A [SwiftBar](https://github.com/swiftbar/SwiftBar) plugin for macOS that shows the [NASA Astronomy Picture of the Day (APOD)](https://apod.nasa.gov/apod/) in your menu bar — and quietly archives the original picture to your Pictures folder every day.

一个 macOS [SwiftBar](https://github.com/swiftbar/SwiftBar) 插件：把 [NASA 每日天文图（APOD）](https://apod.nasa.gov/apod/) 放进菜单栏——并在每天悄悄把原图存进你的图片文件夹归档。

## Origin / 出处

This plugin is based on Jake Vossen's [apod plugin](https://github.com/matryer/xbar-plugins/blob/main/Science/apod.1h.py) from the xbar-plugins collection (MIT, © 2019 Jacob Vossen). We used it for a while — until it broke.

本插件源自 xbar-plugins 插件集里 Jake Vossen 的 [apod 插件](https://github.com/matryer/xbar-plugins/blob/main/Science/apod.1h.py)（MIT，© 2019 Jacob Vossen）。我们用了一阵子——直到它坏了。

## What was broken, and what we changed / 坏在哪，我们改了什么

NASA redesigned the APOD page, and the original 2019 extraction logic no longer works:

NASA 改版了 APOD 页面，原版 2019 年的抓取逻辑失效了：

- **Image URL** — The original scanned the page backwards from the first `.jpg` it found; that now lands on the wrong image. Our first fix read the page's `og:image` meta tag — which turned out to be a site-wide template image (an Eagle Nebula share card) that never changes, so the title updated daily while the picture never did. Since v1.2 the plugin takes the day's real photo from the `image-article` link on the page, the entry date from that link's slug, and archives the full-size original served from NASA's asset store.
  **图片地址**——原版从页面里第一个 `.jpg` 往回拼地址，如今会拼错图。我们的第一版修复改读页面的 `og:image` 元标签——后来发现那是全站写死的模板图（一张鹰状星云的分享卡），永远不变，于是标题天天换、图片永不动。v1.2 起改为从页面里的 `image-article` 条目链接取当日真图，日期取自链接 slug，归档存资产库里的原图大文件。
- **Title** — The page `<title>` and `og:title` are now a generic "APOD - NASA Science", so the original could no longer show the picture's real title. This version takes the title from the page's main heading.
  **标题**——页面的 `<title>` 与 `og:title` 如今只剩泛称 "APOD - NASA Science"，原版再也显示不出图片的真实标题。本版改从页面主标题取。
- **The name, right under the picture — and it is clickable / 图下方就有名字，还能点** — In the dropdown, today's title is printed directly beneath the picture, so you always know what you are looking at — and the archived file on disk carries the same name (date + title). The most practical touch of all: a picture whose name you can read. Since v1.1 the title is clickable: click it and Finder opens the archive folder with today's picture selected.
  下拉菜单里，今天的标题就印在图片正下方，看图先识名；存到硬盘的归档文件也用同一个名字（日期＋标题）。这是最实用的一条：图有名，才认得。v1.1 起标题可以点：点一下，Finder 就打开归档文件夹，并选中今天这张图。
- **Daily archive / 每日归档** — Every fetched picture is also saved at full size, named `YYYY-MM-DD Title.jpg` (existing files are never overwritten). The archive folder defaults to `~/Pictures/NASA-Apod/` and is yours to change: on first run the plugin offers a setup dialog with the default filled in, and the dropdown's Archive submenu can pick a different folder, take a typed path, turn archiving off, or restore the default at any time (stored in `~/.nasa-apod.conf`). Over time this builds a quiet little local archive of the sky.
  每次抓到的图片还会以原图尺寸归档，命名为 `YYYY-MM-DD 标题.jpg`（已有文件不覆盖）。归档文件夹默认 `~/Pictures/NASA-Apod/`，且可由你做主：首次运行时插件会弹出设置框、预填默认路径；之后下拉菜单的归档子菜单里随时可以选另一个文件夹、输入路径、关闭归档或恢复默认（设置存在 `~/.nasa-apod.conf`）。
- **Black borders trimmed for display / 显示时裁掉黑边** — Some of NASA's delivered files carry pure-black side bars (a portrait photo on a wider canvas). Since v1.3 the dropdown image is trimmed of fully-black border rows and columns, so the menu hugs the photo itself. The archived file is never touched.
  NASA 交付的部分图文件自带纯黑侧边（竖幅照片装进宽画布）。v1.3 起，下拉里显示的图会先裁掉整行整列的纯黑边，菜单宽度跟照片本身走。归档文件一像素不动。
- **Refresh every 12 hours / 12 小时刷新** — APOD changes once a day, and the full-size image is a few MB, so the plugin refreshes twice a day instead of hourly.
  APOD 一天一换，原图有几 MB，插件改为每 12 小时刷新一次，不再每小时抓一遍。

## Install / 安装

1. Install [SwiftBar](https://github.com/swiftbar/SwiftBar). / 安装 [SwiftBar](https://github.com/swiftbar/SwiftBar)。
2. Install the one dependency, Pillow: / 安装唯一的依赖 Pillow：

   ```
   pip3 install --user pillow
   ```

3. Download `NASA-Apod.12h.py` into your SwiftBar plugins folder and make it executable:
   把 `NASA-Apod.12h.py` 放进 SwiftBar 插件目录并赋予执行权限：

   ```
   chmod +x NASA-Apod.12h.py
   ```

4. Refresh SwiftBar. A 🔭 appears in your menu bar; click it to see today's picture and its title.
   刷新 SwiftBar，菜单栏出现 🔭；点开即可看到今天的图片与标题。

The `.12h.` in the file name is SwiftBar's refresh-interval convention (every 12 hours).

文件名里的 `.12h.` 是 SwiftBar 的刷新间隔约定（每 12 小时）。

## Notes / 说明

- On days when APOD features a video instead of a picture, the plugin shows a fallback message instead of an image — that is the original behaviour, kept as is.
  APOD 当天是视频而非图片时，插件会显示一句提示而非图片——这是原版行为，原样保留。
- Archived pictures land in `~/Pictures/NASA-Apod/` unless you change the folder (or turn archiving off) in the dropdown's Archive submenu.
  归档图片默认位于 `~/Pictures/NASA-Apod/`；在下拉菜单的归档子菜单里可以改文件夹，或关掉归档。
- This is the exact script running daily on the author's Mac, shared in the hope it is useful to someone else who likes a piece of the sky in their menu bar.
  这是作者每天在自己 Mac 上实际运行的脚本原样分享，希望能帮到同样喜欢在菜单栏里放一片星空的人。

## Changelog / 更新日志

- **v1.8.1** (2026-11-21) — The title is now shown as written: HTML entities in NASA's heading (e.g. `&#039;`) are unescaped, so "Voyager's Neptune" no longer displays as "Voyager&#039;s Neptune"; archived filenames are cleaned the same way. / 标题按原文显示：NASA 标题里的网页编码（如 `&#039;`）现在会解开，不再显示成 "Voyager&#039;s Neptune"，归档文件名同步变干净。

- **v1.8** (2026-11-21) — New Refresh item under the picture's title in the dropdown: one click makes SwiftBar re-run the plugin at once and fetch the newest picture, instead of waiting for the 12-hour cycle. The click first compares dates and answers with a hint — "Up to date!" when there is no newer picture, "Update successfully" when there is. The error line gains the same item, so a failed fetch can be retried with one click. / 下拉菜单的图片标题下方新增「刷新」一项：点一下，SwiftBar 立刻重跑插件、拉取最新图片，不必再等 12 小时周期；点击时先比对日期并给一句提示——没有新图是 "Up to date!"，有新图是 "Update successfully"。取图失败的报错行下也带同一项，可一键重试。

- **v1.7** (2026-11-20) — Bilingual UI that follows the system language: Chinese on Chinese systems, English elsewhere — dropdown, Archive submenu, first-run setup dialog, folder/path dialogs and the error line included. Set the `APOD_LANG` environment variable (`zh`/`en`) to override. / 界面双语跟随系统语言：中文系统显示中文，其它显示英文——下拉菜单、归档子菜单、首次运行设置框、选目录/输路径对话框与报错行全覆盖；可用环境变量 `APOD_LANG`（`zh`/`en`）覆盖。

- **v1.6** (2026-11-20) — Plugin UI language unified to Simplified Chinese (title, description, status and error lines). / 插件界面文字统一为简体中文（标题、说明、状态与报错行）。
- **v1.5** (2026-11-20) — The first-run setup dialog gains a “Choose folder…” button: pick a folder and you return to the dialog with the path filled in, then confirm. / 首次运行设置框新增「选择文件夹…」按钮：选好文件夹后带着新路径回到框里，再点确定。
- **v1.4** (2026-11-20) — The archive folder is configurable: a first-run setup dialog (default prefilled, one click to accept) and an Archive submenu in the dropdown (choose folder, type a path, turn off, restore default), stored in `~/.nasa-apod.conf`. / 归档文件夹可配置：首次运行设置框（预填默认路径，点确定即用）＋下拉菜单里的归档子菜单（选择文件夹、输入路径、关闭、恢复默认），设置存 `~/.nasa-apod.conf`。
- **v1.3** (2026-11-20) — Display image trimmed of the pure-black borders baked into some of NASA's files, so the menu width follows the photo. / 显示图裁掉 NASA 文件自带的纯黑边，菜单宽度跟照片本身走。
- **v1.2** (2026-11-20) — Fixed the frozen-picture bug: `og:image` on the redesigned page is a fixed site template (Eagle Nebula). The day's photo now comes from the `image-article` link, the date from its slug, and the archive stores the full original. / 修复图片冻结的 bug：改版页面的 `og:image` 是写死的站点模板图（鹰状星云）。当日照片改从 `image-article` 链接取，日期取自其 slug，归档存原图。
- **v1.1** (2026-11-19) — The title under the picture is clickable (Finder reveals the archived file); bilingual README. / 图片下方的标题可点击（在 Finder 中显示归档文件）；双语 README。
- **v1.0** (2026-11-19) — Revived for NASA's redesigned APOD page: title from the main heading, daily full-size archive, 12-hour refresh. / 为 NASA 改版后的 APOD 页面复活：标题取自主标题、每日原图归档、12 小时刷新。

## Credits / 作者

Original plugin by **Jake Vossen** ([@jakevossen5](https://github.com/jakevossen5)), MIT licensed.
Revived, extended and re-shared by **Otakun** ([@iam-otakun](https://github.com/iam-otakun)) and **Dash**, his Muse assistant.

原插件作者 **Jake Vossen**（[@jakevossen5](https://github.com/jakevossen5)），MIT 许可。
由 **Otakun**（[@iam-otakun](https://github.com/iam-otakun)）与他的 Muse 助手 **Dash** 修复、扩展并重新分享。

## License / 许可

MIT — see the LICENSE file. The original copyright of Jacob Vossen is preserved in the script header and in LICENSE.
MIT——见 LICENSE 文件。Jacob Vossen 的原版权声明保留在脚本头部与 LICENSE 中。
