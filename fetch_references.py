#!/usr/bin/env python3
"""
参考文献自动检索与格式化工具

从 bigan.net 学术搜索 API 检索文献，自动生成 GB/T 7714 格式的参考文献列表。

用法:
    # 按关键词搜索，生成20条参考文献
    python fetch_references.py "房屋租赁管理系统" "SSM框架" "Java Web" -n 20

    # 指定输出文件
    python fetch_references.py "在线教育" "Spring Boot" -o papers/zhixue/references.json

    # 搜学位论文
    python fetch_references.py "房屋租赁" --type thesis -n 10

    # 只搜近5年的
    python fetch_references.py "Spring Boot" --min-year 2020

数据源: https://www.bigan.net/reference/
输出格式: JSON 数组，每条为 GB/T 7714 标准格式字符串
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

API_BASE = "https://www.bigan.net/api/reference"
HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.bigan.net/reference/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
}

# 文献类型映射
TYPE_MAP = {
    "journal": "journal",     # 期刊
    "thesis": "thesis",       # 学位论文
    "conference": "conference",# 会议论文
    "book": "book",           # 图书
    "patent": "patent",       # 专利
    "newspaper": "newspaper", # 报纸
    "standard": "standard",   # 标准
}


def search(query, size=10, datatype="journal", page=1):
    """搜索文献，返回命中列表"""
    params = urllib.parse.urlencode({
        "query": query, "size": size,
        "datatype": datatype, "page": page,
    })
    url = f"{API_BASE}/search?{params}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    if data.get("code") != 0:
        print(f"  搜索失败: {data.get('msg')}", file=sys.stderr)
        return []
    return data.get("data", {}).get("hits", [])


def format_gb(doc_ids):
    """将文献 docId 列表格式化为 GB/T 7714 引用格式"""
    if not doc_ids:
        return []
    url = f"{API_BASE}/format/list?clienttime={time.time()}"
    body = json.dumps({
        "source": [{"type": "our", "docId": did} for did in doc_ids]
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=HEADERS, method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())
    if data.get("code") != 0:
        print(f"  格式化失败: {data.get('msg')}", file=sys.stderr)
        return []
    refs = []
    for item in data.get("data", []):
        for fmt in item:
            if fmt.get("key") == "gb":
                v = fmt.get("value", "").strip()
                if v:
                    refs.append(v)
    return refs


def fetch_references(queries, total=20, datatype="journal", min_year=2000):
    """
    按多组关键词搜索文献，去重后格式化为 GB/T 7714。

    参数:
        queries: 关键词列表
        total: 目标文献数量
        datatype: 文献类型 (journal/thesis/conference/book)
        min_year: 最早年份
    返回:
        GB/T 7714 格式的参考文献字符串列表
    """
    seen = set()
    doc_ids = []
    per_query = max(5, (total * 2) // len(queries))

    for query in queries:
        print(f"  搜索: {query}", file=sys.stderr)
        hits = search(query, size=per_query, datatype=datatype)
        for hit in hits:
            did = hit.get("docid", "")
            year = int(hit.get("year", "0") or "0")
            if did and did not in seen and year >= min_year:
                seen.add(did)
                doc_ids.append(did)
                title = hit.get("title_text", "")[:40]
                print(f"    ✓ {title} ({year})", file=sys.stderr)
        if len(doc_ids) >= total:
            break

    doc_ids = doc_ids[:total]
    print(f"  共找到 {len(doc_ids)} 条，正在格式化...", file=sys.stderr)

    # 分批格式化（API 限制）
    all_refs = []
    for i in range(0, len(doc_ids), 10):
        batch = doc_ids[i:i + 10]
        refs = format_gb(batch)
        all_refs.extend(refs)
        if i + 10 < len(doc_ids):
            time.sleep(0.5)

    print(f"  ✓ 成功格式化 {len(all_refs)} 条参考文献", file=sys.stderr)
    return all_refs


def main():
    parser = argparse.ArgumentParser(
        description="参考文献自动检索工具 - 从 bigan.net 搜索并生成 GB/T 7714 格式引用",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "房屋租赁" "SSM框架" "Java Web" -n 20
  %(prog)s "在线教育" "NestJS" "Flutter" -o refs.json --min-year 2020
  %(prog)s "Spring Boot" --type thesis -n 10
        """,
    )
    parser.add_argument("queries", nargs="+", help="搜索关键词（可多个）")
    parser.add_argument("-n", "--count", type=int, default=20,
                        help="目标文献数量（默认20）")
    parser.add_argument("-o", "--output", default=None,
                        help="输出 JSON 文件路径（默认输出到终端）")
    parser.add_argument("--type", choices=list(TYPE_MAP.keys()),
                        default="journal", help="文献类型（默认journal期刊）")
    parser.add_argument("--min-year", type=int, default=2000,
                        help="最早发表年份（默认2000）")

    args = parser.parse_args()
    datatype = TYPE_MAP[args.type]

    refs = fetch_references(args.queries, total=args.count,
                            datatype=datatype, min_year=args.min_year)

    if not refs:
        print("未找到符合条件的参考文献", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(refs, f, ensure_ascii=False, indent=2)
        print(f"已保存到 {args.output}", file=sys.stderr)
    else:
        # 输出到终端
        for i, ref in enumerate(refs, 1):
            print(f"[{i}] {ref}")


if __name__ == "__main__":
    main()
