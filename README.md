# NASA APOD — a SwiftBar plugin / NASA 每日天文图 SwiftBar 插件

A [SwiftBar](https://github.com/swiftbar/SwiftBar) plugin for macOS that shows the [NASA Astronomy Picture of the Day (APOD)](https://apod.nasa.gov/apod/) in your menu bar — and quietly archives the original picture to your Pictures folder every day.

一个 macOS [SwiftBar](https://github.com/swiftbar/SwiftBar) 插件：把 [NASA 每日天文图（APOD）](https://apod.nasa.gov/apod/) 放进菜单栏——并在每天悄悄把原图存进你的图片文件夹归档。

## Origin / 出处

This plugin is based on Jake Vossen's [apod plugin](https://github.com/matryer/xbar-plugins/blob/main/Science/apod.1h.py) from the xbar-plugins collection (MIT, © 2019 Jacob Vossen). We used it for a while — until it broke.

本插件源自 xbar-plugins 插件集里 Jake Vossen 的 [apod 插件](https://github.com/matryer/xbar-plugins/blob/main/Science/apod.1h.py)（MIT，© 2019 Jacob Vossen）。我们用了一阵子——直到它坏了。

## What was broken, and what we changed / 坏在哪，我们改了什么

NASA redesigned the APOD page, and the original 2019 extraction logic no longer works:

NASA 改版了 APOD 页面，原版 2019 年的抓取逻辑失效了：

- **Image URL** — The original scanned the page backwards from the first `.jpg` it found; that now lands on the wrong image. This version reads the page's `og:image` meta tag first (the canonical share image), and only falls back to the old scan if it is missing.
  **图片地址**——原版从页面里第一个 `.jpg` 往回拼地址，如今会拼错图。本版优先读取页面的 `og:image` 元标签（官方分享图地址），缺失时才回退到旧方法。
- **Title** — The page `<title>` and `og:title` are now a generic "APOD - NASA Science", so the original could no longer show the picture's real title. This version takes the title from the page's main heading.
  **标题**——页面的 `<title>` 与 `og:title` 如今只剩泛称 "APOD - NASA Science"，原版再也显示不出图片的真实标题。本版改从页面主标题取。
- **Daily archive / 每日归档** — Every fetched picture is also saved at full size to `~/Pictures/NASA-Apod/`, named `YYYY-MM-DD Title.jpg` (existing files are never overwritten). Over time this builds a quiet little local archive of the sky.
  每次抓到的图片还会以原图尺寸存入 `~/Pictures/NASA-Apod/`，命名为 `YYYY-MM-DD 标题.jpg`（已有文件不覆盖）。日积月累，就是一座安静的小小星空档案馆。
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
- Archived pictures land in `~/Pictures/NASA-Apod/`. If you don't want the archive, delete the clearly-marked save block in the script — the menu bar display does not depend on it.
  归档图片位于 `~/Pictures/NASA-Apod/`。不想要归档的话，删掉脚本里有注释标明的那段保存代码即可，菜单栏显示不依赖它。
- This is the exact script running daily on the author's Mac, shared in the hope it is useful to someone else who likes a piece of the sky in their menu bar.
  这是作者每天在自己 Mac 上实际运行的脚本原样分享，希望能帮到同样喜欢在菜单栏里放一片星空的人。

## Credits / 作者

Original plugin by **Jake Vossen** ([@jakevossen5](https://github.com/jakevossen5)), MIT licensed.
Revived, extended and re-shared by **Otakun** ([@iam-otakun](https://github.com/iam-otakun)) and **Dash**, his Muse assistant.

原插件作者 **Jake Vossen**（[@jakevossen5](https://github.com/jakevossen5)），MIT 许可。
由 **Otakun**（[@iam-otakun](https://github.com/iam-otakun)）与他的 Muse 助手 **Dash** 修复、扩展并重新分享。

## License / 许可

MIT — see the LICENSE file. The original copyright of Jacob Vossen is preserved in the script header and in LICENSE.
MIT——见 LICENSE 文件。Jacob Vossen 的原版权声明保留在脚本头部与 LICENSE 中。
