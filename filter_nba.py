#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从已生成的 Mac_playlist.m3u 里筛出 NBA 专属列表，写成 NBA.m3u。

用法: python3 filter_nba.py [输入文件] [输出文件]
默认: 输入 Mac_playlist.m3u，输出 NBA.m3u（与输入同目录）。

筛选规则：EXTINF 行（台名、分组名）里含独立的 NBA 一词（忽略大小写，
如 NBA GAME、NBA TV、NBATV）即保留，连同紧跟其后的播放地址行一起写入。
WNBA 不算（W 后面的 NBA 不是独立一词，会被排除）。
文件头原样保留。不联网、不需要任何账号，纯文本过滤。
"""
import pathlib
import re
import sys

NBA_RE = re.compile(r"(?<![a-z])nba(?![a-z])")


def main():
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("Mac_playlist.m3u")
    dst = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name("NBA.m3u")

    lines = src.read_text(encoding="utf-8", errors="ignore").splitlines()
    out = []
    kept = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("#EXTM3U") or line.startswith("#EXT-X-"):
            out.append(line)
            i += 1
            continue
        if line.startswith("#EXTINF"):
            low = line.lower()
            if NBA_RE.search(low) or "nbatv" in low:
                out.append(line)
                # 紧跟的地址行（非 # 开头）一起保留
                if i + 1 < len(lines) and not lines[i + 1].startswith("#"):
                    out.append(lines[i + 1])
                    i += 1
                kept += 1
            i += 1
            continue
        # 其他行（地址行已随 EXTINF 处理，孤立行跳过）
        i += 1

    dst.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"NBA channels: {kept} -> {dst.name} ({dst.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
