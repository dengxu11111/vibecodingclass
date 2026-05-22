"""Capstone · 步骤 5：把草稿里每个数字回链到 CSV，揪 AI 编数据。

这一步是"AI 辅助科研"的安全带：起草员 / 润色员可能写出 csv 里根本没有的数字，
肉眼很难逐个核对，但脚本可以。

做法很朴素：
1. 扫 data/processed/ 下所有 csv 的所有 cell，把出现过的数字（按 2 位 / 3 位 / 4 位小数）
   统一规范成"数字 + 容差"放进一张表
2. 扫 outputs/ 下指定 Markdown（默认 草稿_v2.md 或 最终稿.md），用正则抠出所有看着像
   测量值的数字（°C、°C/年、% 、CI 区间数字、年份）
3. 对每个数字，查它能不能在 csv 表里找到一个容差范围内的匹配
4. 输出报告：traced（找到了） / untraced（没找到，可能是 AI 编的）

注意事项：
- 年份（1900-2099）不算测量值，跳过
- 整数（n / R²×N 之类）单独处理
- 容差默认 ±0.01（°C 精度）和 ±0.001（slope 精度），可调

跑法：
    python 05_核验.py                       # 默认核验 outputs/草稿_v2.md
    python 05_核验.py outputs/最终稿.md      # 指定其它草稿
    python 05_核验.py --tol 0.05            # 放宽容差

产出：
    outputs/核验报告.md
    退出码：untraced == 0 → 0；否则 → 1（便于接 CI / pre-commit）
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).parent
PROC = HERE / "data" / "processed"
OUTPUTS = HERE / "outputs"

# 数字识别：带小数点的浮点数，或带正负号的浮点数。整数后面单独筛。
NUM_RE = re.compile(r"[-+]?\d+\.\d+|\d+")

# 年份范围（1900-2099），跳过
YEAR_RANGE = range(1900, 2100)

# 噪音过滤：如果一个数字 token 出现在这些上下文里，**不是**真的测量值，跳过。
# 这些正则匹配的是「数字 + 紧邻字符」的小局部，不影响 csv 里真有的浮点。
NOISE_PATTERNS = [
    re.compile(r"^\s*\d+\.\s"),            # "1. " 段落编号
    re.compile(r"^#+\s*\d+"),               # "# 1" / "## 2" 章节编号
    re.compile(r"v\d+"),                     # v1 / v2 版本号
    re.compile(r"\d+\s*字"),                 # "800 字" 字数
    re.compile(r"\d+\s*[月日时分秒]"),        # "12 月 / 31 日"
    re.compile(r"\d+\s*[座位个家本张城项处次倍件篇名条]"),  # "7 座 / 3 个 / 4 城" 计数量词
    re.compile(r"\d+\s*-\d+"),               # "2021-2025" 区间
    re.compile(r"0\d_"),                     # 01_下载 / 04_起草 文件名编号
    re.compile(r"\bn\s*=\s*\d+"),            # "n=5" 样本量声明（方法描述非测量）
    re.compile(r"\bdf\s*=\s*\d+"),           # "df=28" 自由度
    re.compile(r"\d+\s*天"),                 # "1826 天" 天数（方法学描述）
    re.compile(r"图\s*\d+"),                 # "图 1" 图编号
    re.compile(r"第\s*\d+\s*[行列章节段步]"),  # "第 2 行" 引用编号
    re.compile(r"\d+\s*米"),                 # "2 米气温" 高度描述
    re.compile(r"\d+\s*MB|\d+\s*KB|\d+\s*GB"),  # 文件大小
    re.compile(r"跨\s*[+\-]?\d+"),                # "CI 都跨 0"
    re.compile(r"约束\D{0,8}\d+|落在\D{0,8}\d+"),  # "字数约束 800" / "落在 600-1000"
    re.compile(r"\d+\s*[-–—]\s*\d+\s*之间"),       # "600-1000 之间"
    # P1-b 收紧：消除常见误识别
    re.compile(r"ERA[\s-]*\d+"),              # "ERA5" 里的 5 不是测量值
    re.compile(r"ERA\d+"),                    # 同上的紧凑写法
    re.compile(r"\(\s*\d+\s*\)"),              # "(3)"、"(1)" 列表枚举
    re.compile(r"AR[\s-]*\d+"),                # "AR(1)" / "AR1" 自相关阶数
    re.compile(r"\d+\s*%"),                   # "100 %" / "30%" 百分比（容易跟数据冲突，按需关）
    re.compile(r"含\s*0|跨\s*0|不含\s*0"),     # "CI 含 0 / 不含 0"
    re.compile(r"\d+\s*\+\s*年"),              # "60+ 年"
    re.compile(r"GPT-?\d+|GLM-?\d+|R-?\d+|V-?\d+|H-?\d+"),  # 型号名里的数字（GPT-4 / GLM-4.5）
]

# 方法学常量白名单：写论文 / 综述时常引用的固定数字，**几乎**都不是测量值。
# 形如 "95%"、"R² = 0.93 (this is data) vs 0.93 (this is the literal R-squared constant?)
# 这里只放真的"常量"：alpha、置信水平、自由度计算等；R²、p 值、slope 值**不**进白名单（那是结果）。
METHOD_CONSTANTS = {
    1.96,    # 正态分布 95% 双尾
    2.576,   # 正态分布 99% 双尾
    0.05,    # 显著性水平 alpha
    0.01,    # 严格显著性水平
    95.0,    # "95% CI" / "95% 置信"
    99.0,    # "99% CI"
    90.0,    # "90% CI"
    50.0,    # "50%" 中位
    0.25,    # ERA5 空间分辨率（°）
    2.0,     # "2 米气温" / "2m"
    1.0,     # 出现在 "1 倍"、"1 个" 等
    7.0,     # "7 城" 城市数（在 capstone 语境里）
    30.0,    # "30 年" 窗口
    300.0,   # "≥ 300 天" 年度覆盖阈值
    365.0,   # 一年天数
}


def is_method_constant(value: float) -> bool:
    """是不是写综述时常引用的方法学常量（95% / 1.96σ / 0.25° 等）。"""
    for c in METHOD_CONSTANTS:
        if abs(value - c) < 1e-6:
            return True
    return False


def is_noise(line: str, match: re.Match) -> bool:
    """判断数字 match 在 line 里是否属于明显非测量值（章节编号 / 字数 / 日期片段等）。"""
    # 取数字周围 6 字的局部
    start = max(0, match.start() - 6)
    end = min(len(line), match.end() + 6)
    local = line[start:end]
    return any(p.search(local) for p in NOISE_PATTERNS)


def load_csv_numbers(processed_dir: Path) -> set[float]:
    """把 processed/ 下所有 csv 单元格里的数字都收集到一个 set。"""
    nums: set[float] = set()
    if not processed_dir.exists():
        return nums
    for csv_path in sorted(processed_dir.glob("*.csv")):
        with csv_path.open("r", encoding="utf-8-sig") as f:
            for row in csv.reader(f):
                for cell in row:
                    cell = cell.strip()
                    if not cell:
                        continue
                    try:
                        nums.add(float(cell))
                    except ValueError:
                        # cell 可能是 "39.9042" 也可能是 "北京"，转不动就跳
                        continue
    return nums


def extract_md_numbers(md_path: Path) -> list[tuple[int, str, float]]:
    """从 Markdown 抠数字，返回 (行号, 上下文片段, 值)。"""
    out: list[tuple[int, str, float]] = []
    text = md_path.read_text(encoding="utf-8")
    for lineno, line in enumerate(text.splitlines(), 1):
        # 跳过代码块围栏行
        if line.strip().startswith("```"):
            continue
        for m in NUM_RE.finditer(line):
            raw = m.group()
            try:
                val = float(raw)
            except ValueError:
                continue
            # 年份跳过
            if "." not in raw and int(val) in YEAR_RANGE:
                continue
            # 噪音过滤：段落编号、字数、日期片段等
            if is_noise(line, m):
                continue
            # 上下文：当前字符前后各 20 字
            start = max(0, m.start() - 20)
            end = min(len(line), m.end() + 20)
            context = line[start:end].strip()
            out.append((lineno, context, val))
    return out


def trace(value: float, csv_nums: set[float], tol_dec: float, tol_int: float) -> bool:
    """value 能否在 csv_nums 里找到一个容差内的匹配。"""
    # 整数（数字本身就是整数 / 没小数部分）用更大容差
    is_int_like = float(value).is_integer()
    tol = tol_int if is_int_like else tol_dec
    for n in csv_nums:
        if abs(n - value) <= tol:
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("draft", nargs="?", default=None,
                    help="要核验的 Markdown 文件，默认 outputs/草稿_v2.md")
    ap.add_argument("--tol", type=float, default=0.01,
                    help="浮点数容差，默认 0.01（°C 精度）")
    ap.add_argument("--tol-int", type=float, default=0.0,
                    help="整数容差，默认 0（严格匹配）")
    args = ap.parse_args()

    if args.draft:
        draft = Path(args.draft)
        if not draft.is_absolute():
            draft = (HERE / draft).resolve() if (HERE / draft).exists() else Path.cwd() / draft
    else:
        # 优先 最终稿，其次 草稿_v2
        for cand in ["最终稿.md", "草稿_v2.md", "起草员_v1.md"]:
            p = OUTPUTS / cand
            if p.exists():
                draft = p
                break
        else:
            print("[错误] 找不到草稿。请先按 04_起草.md 跑出 outputs/草稿_v2.md 或最终稿.md。")
            return 2

    if not draft.exists():
        print(f"[错误] 草稿不存在：{draft}")
        return 2

    csv_nums = load_csv_numbers(PROC)
    if not csv_nums:
        print(f"[错误] {PROC} 下没找到任何 csv 数字。先跑 01_下载.py / 02_分析.py。")
        return 2

    print(f"→ 核验：{draft}")
    print(f"  对照 csv 数字池：{len(csv_nums)} 个唯一值")
    print(f"  容差：浮点 ±{args.tol}，整数 ±{args.tol_int}")

    items = extract_md_numbers(draft)
    if not items:
        print("[警告] 草稿里没抠到任何数字。是不是空文件？")
        return 1

    traced: list[tuple[int, str, float]] = []
    untraced: list[tuple[int, str, float]] = []
    method_const: list[tuple[int, str, float]] = []
    for entry in items:
        _, _, val = entry
        if trace(val, csv_nums, args.tol, args.tol_int):
            traced.append(entry)
        elif is_method_constant(val):
            # 数字本身是方法学常量（95% / 1.96 / 0.25°），不是 csv 测量值
            method_const.append(entry)
        else:
            untraced.append(entry)

    # 写报告
    report = OUTPUTS / "核验报告.md"
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    with report.open("w", encoding="utf-8") as f:
        f.write(f"# 数字核验报告\n\n")
        f.write(f"- 草稿：`{draft.relative_to(HERE) if draft.is_relative_to(HERE) else draft}`\n")
        f.write(f"- csv 数字池：{len(csv_nums)} 个唯一值\n")
        f.write(f"- 容差：浮点 ±{args.tol}，整数 ±{args.tol_int}\n")
        f.write(f"- **traced（结果数字回链 csv）**：{len(traced)} 个\n")
        f.write(f"- **方法学常量**：{len(method_const)} 个（95% / 1.96 / 0.25° 等，写综述常引用，不算编造）\n")
        f.write(f"- **untraced（疑似 AI 编造）**：{len(untraced)} 个 ← 重点处理这一类\n\n")

        if untraced:
            f.write("## [X] untraced — 这些数字 csv 里找不到，可能是 AI 编的\n\n")
            f.write("| 行号 | 数字 | 上下文 |\n| --- | --- | --- |\n")
            for lineno, ctx, val in untraced:
                ctx_md = ctx.replace("|", "\\|")
                f.write(f"| {lineno} | `{val}` | {ctx_md} |\n")
            f.write("\n**处理建议**：逐条复核。\n")
            f.write("- 真的在 csv 里、只是精度不同 → 改成 csv 同精度，或放宽 `--tol`\n")
            f.write("- csv 里不存在 → AI 编的，从草稿里删掉或重写\n")
            f.write("- 是方法学常量但没被白名单识别 → 加到 `05_核验.py` 的 `METHOD_CONSTANTS`\n\n")
        else:
            f.write("## [OK] untraced = 0\n\n所有结果数字都能在 csv 里找到容差内的匹配。\n\n")

        if method_const:
            f.write("## 方法学常量（参考，不需要修改）\n\n")
            f.write("| 行号 | 数字 | 上下文 |\n| --- | --- | --- |\n")
            for lineno, ctx, val in method_const[:20]:
                ctx_md = ctx.replace("|", "\\|")
                f.write(f"| {lineno} | `{val}` | {ctx_md} |\n")
            if len(method_const) > 20:
                f.write(f"| ... | ... | （另有 {len(method_const) - 20} 条）|\n")
            f.write("\n")

        if traced:
            f.write("## [OK] traced — csv 里能找到匹配（仅显示前 20 条）\n\n")
            f.write("| 行号 | 数字 | 上下文 |\n| --- | --- | --- |\n")
            for lineno, ctx, val in traced[:20]:
                ctx_md = ctx.replace("|", "\\|")
                f.write(f"| {lineno} | `{val}` | {ctx_md} |\n")

    print(f"\n[完成] 报告写入：{report}")
    print(f"  traced       : {len(traced)}（结果数字 → csv）")
    print(f"  方法学常量   : {len(method_const)}（95% / 1.96 / 0.25° 等，不算编造）")
    print(f"  untraced     : {len(untraced)} ← 重点关注这一栏")

    if untraced:
        print("\n[!] 有 untraced 数字。读 outputs/核验报告.md，逐条复核 / 修改草稿。")
        return 1
    print("\n[OK] 所有结果数字都能回链到 csv。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
