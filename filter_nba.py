#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从已生成的 Mac_playlist.m3u 里筛出 NBA 专属列表，写成 NBA.m3u。

用法: python3 filter_nba.py [输入文件] [输出文件]
默认: 输入 Mac_playlist.m3u，输出 NBA.m3u（与输入同目录）。

筛选规则：EXTINF 行（台名、分组名）里含独立的 NBA 一词（忽略大小写，
如 NBA GAME、NBA TV、NBATV）即保留。WNBA 不算（W 后面的 NBA 不是独立一词，会被排除）。

关键：一个台在文件里占多行——EXTINF 后面还跟着 #EXTVLCOPT 行（播放参数）
和最后的播放地址行。过滤时必须把一个台的整块（EXTINF + 后面直到下一个
EXTINF 之前的所有行）一起保留或一起丢掉，只留 EXTINF、不留地址行是播不了的。

文件头（第一个 EXTINF 之前的所有行）原样保留。
不联网、不需要任何账号，纯文本过滤。
"""
import pathlib
import re
import sys

NBA_RE = re.compile(r"(?<![a-z])nba(?![a-z])")


def main():
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("Mac_playlist.m3u")
    dst = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else src.with_name("NBA.m3u")

    lines = src.read_text(encoding="utf-8", errors="ignore").splitlines()
    n = len(lines)
    out = []
    kept = 0

    # 文件头：第一个 EXTINF 之前的所有非空行，原样保留
    i = 0
    while i < n and not lines[i].startswith("#EXTINF"):
        if lines[i].strip() != "":
            out.append(lines[i])
        i += 1

    # 逐台处理：每台 = 1 行 EXTINF + 之后直到下一个 EXTINF 之前的所有行
    while i < n:
        line = lines[i]
        if not line.startswith("#EXTINF"):
            i += 1
            continue
        low = line.lower()
        is_nba = bool(NBA_RE.search(low) or "nbatv" in low)
        j = i + 1
        block = []
        while j < n and not lines[j].startswith("#EXTINF"):
            if lines[j].strip() != "":
                block.append(lines[j])
            j += 1
        if is_nba:
            out.append(line)
            out.extend(block)
            kept += 1
        i = j

    dst.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"NBA channels: {kept} -> {dst.name} ({dst.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
