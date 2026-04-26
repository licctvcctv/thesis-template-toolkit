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

    # 每个关键词最多翻 2 页，每页 100 条候选，即扩大到 200 条候选池
    python fetch_references.py "微信小程序" "在线学习" --page-size 100 --max-pages 2

    # 搜英文文献（Crossref），生成 GB/T 7714 风格英文参考文献
    python fetch_references.py "mobile learning" --source crossref --lang en --min-year 2021

数据源: https://www.bigan.net/reference/
输出格式: JSON 数组，每条为 GB/T 7714 标准格式字符串
"""
import argparse
import html
import http.cookiejar
import json
import re
import sys
import time
import urllib.parse
import urllib.request

API_BASE = "https://www.bigan.net/api/reference"
CROSSREF_API = "https://api.crossref.org/works"
HEADERS = {
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.bigan.net/reference/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 Chrome/146.0.0.0 Safari/537.36",
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

# 全局 opener（带 cookie 管理，自动保持 JSESSIONID，跳过代理）
_cookie_jar = http.cookiejar.CookieJar()
_opener = urllib.request.build_opener(
    urllib.request.HTTPCookieProcessor(_cookie_jar),
    urllib.request.ProxyHandler({}))
_session_ready = False


def _ensure_session():
    """首次调用时访问页面获取 JSESSIONID"""
    global _session_ready
    if _session_ready:
        return
    req = urllib.request.Request(
        "https://www.bigan.net/reference/", headers=HEADERS)
    _opener.open(req, timeout=10)
    _session_ready = True


def search(query, size=200, datatype="journal", page=1):
    """搜索文献，返回命中列表"""
    _ensure_session()
    params = urllib.parse.urlencode({
        "query": query, "size": size,
        "datatype": datatype, "page": page,
    })
    url = f"{API_BASE}/search?{params}"
    req = urllib.request.Request(url, headers=HEADERS)
    with _opener.open(req, timeout=15) as resp:
        data = json.loads(resp.read())
    if data.get("code") != 0:
        print(f"  搜索失败: {data.get('msg')}", file=sys.stderr)
        return []
    return data.get("data", {}).get("hits", [])


def _extract_year(value):
    """Best-effort year parser for mixed API payloads."""
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        m = re.search(r"(19|20)\d{2}", value)
        return int(m.group(0)) if m else 0
    if isinstance(value, list):
        for item in value:
            y = _extract_year(item)
            if y:
                return y
    if isinstance(value, dict):
        for key in ("date-parts", "year", "published-print", "published-online", "created"):
            if key in value:
                y = _extract_year(value[key])
                if y:
                    return y
    return 0


def _clean_text(value):
    if isinstance(value, list):
        value = value[0] if value else ""
    return re.sub(r"\s+", " ", html.unescape(str(value or ""))).strip(" .")


def search_crossref(query, rows=100, page=1, min_year=2021):
    """Search English scholarly references through Crossref."""
    offset = max(0, page - 1) * rows
    params = urllib.parse.urlencode({
        "query": query,
        "rows": rows,
        "offset": offset,
        "filter": f"from-pub-date:{min_year}-01-01,type:journal-article",
        "sort": "relevance",
        "select": "DOI,title,author,container-title,published-print,published-online,published,created,issued,volume,issue,page,type",
    })
    url = f"{CROSSREF_API}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": HEADERS["User-Agent"]})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())
    return data.get("message", {}).get("items", [])


def format_crossref_item(item):
    title = _clean_text(item.get("title"))
    journal = _clean_text(item.get("container-title"))
    year = (
        _extract_year(item.get("published-print"))
        or _extract_year(item.get("published-online"))
        or _extract_year(item.get("published"))
        or _extract_year(item.get("issued"))
        or _extract_year(item.get("created"))
    )
    authors = []
    for author in item.get("author", [])[:4]:
        family = _clean_text(author.get("family"))
        given = _clean_text(author.get("given"))
        if family:
            initials = " ".join(f"{part[0]}." for part in given.split() if part)
            authors.append(f"{family} {initials}".strip())
    author_text = ", ".join(authors) if authors else "Unknown"
    volume = _clean_text(item.get("volume"))
    issue = _clean_text(item.get("issue"))
    pages = _clean_text(item.get("page"))
    if "thisLastPage" in pages:
        pages = ""
    doi = _clean_text(item.get("DOI"))
    tail = ""
    if volume and issue:
        tail = f", {volume}({issue})"
    elif volume:
        tail = f", {volume}"
    if pages:
        tail += f": {pages}"
    doi_text = f". DOI: {doi}" if doi else ""
    if not title or not journal or not year:
        return ""
    return f"{author_text}. {title}[J]. {journal}, {year}{tail}{doi_text}."


def format_gb(doc_ids):
    """将文献 docId 列表格式化为 GB/T 7714 引用格式"""
    if not doc_ids:
        return []
    _ensure_session()
    url = f"{API_BASE}/format/list?clienttime={time.time()}"
    body = json.dumps({
        "source": [{"type": "our", "docId": did} for did in doc_ids]
    }).encode("utf-8")
    fmt_headers = {**HEADERS, "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=body, headers=fmt_headers, method="POST")
    with _opener.open(req, timeout=20) as resp:
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
                    refs.append(html.unescape(v))
    return refs


def fetch_references(
    queries,
    total=20,
    datatype="journal",
    min_year=2000,
    page_size=100,
    max_pages=2,
):
    """
    按多组关键词搜索文献，去重后格式化为 GB/T 7714。

    参数:
        queries: 关键词列表
        total: 目标文献数量
        datatype: 文献类型 (journal/thesis/conference/book)
        min_year: 最早年份
        page_size: 每页候选数量
        max_pages: 每个关键词最多翻页数
    返回:
        GB/T 7714 格式的参考文献字符串列表
    """
    seen = set()
    seen_titles = set()
    doc_ids = []
    page_size = max(5, min(200, page_size))
    max_pages = max(1, max_pages)

    for query in queries:
        print(f"  搜索: {query}", file=sys.stderr)
        for page in range(1, max_pages + 1):
            hits = search(query, size=page_size, datatype=datatype, page=page)
            if not hits:
                break
            for hit in hits:
                did = hit.get("docid", "")
                year = _extract_year(hit.get("year"))
                title = _clean_text(hit.get("title_text", ""))
                title_key = title.lower()
                if did and did not in seen and title_key not in seen_titles and year >= min_year:
                    seen.add(did)
                    seen_titles.add(title_key)
                    doc_ids.append(did)
                    print(f"    ✓ p{page} {title[:40]} ({year})", file=sys.stderr)
            if len(doc_ids) >= total:
                break
            time.sleep(0.2)
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


def fetch_crossref_references(queries, total=20, min_year=2021, page_size=100, max_pages=2):
    """Fetch English references through Crossref and format them."""
    seen = set()
    seen_titles = set()
    refs = []
    page_size = max(5, min(200, page_size))
    max_pages = max(1, max_pages)
    for query in queries:
        print(f"  Crossref 搜索: {query}", file=sys.stderr)
        for page in range(1, max_pages + 1):
            try:
                hits = search_crossref(query, rows=page_size, page=page, min_year=min_year)
            except Exception as exc:
                print(f"    Crossref 失败: {exc}", file=sys.stderr)
                break
            if not hits:
                break
            for item in hits:
                doi = _clean_text(item.get("DOI")).lower()
                title_key = _clean_text(item.get("title")).lower()
                ref = format_crossref_item(item)
                year = _extract_year(ref)
                key = doi or ref.lower()
                if ref and key not in seen and title_key not in seen_titles and year >= min_year:
                    seen.add(key)
                    seen_titles.add(title_key)
                    refs.append(ref)
                    print(f"    ✓ p{page} {_clean_text(item.get('title'))[:55]} ({year})", file=sys.stderr)
                if len(refs) >= total:
                    break
            if len(refs) >= total:
                break
            time.sleep(0.2)
        if len(refs) >= total:
            break
    print(f"  ✓ Crossref 成功格式化 {len(refs)} 条参考文献", file=sys.stderr)
    return refs[:total]


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
    parser.add_argument("--page-size", type=int, default=100,
                        help="每页候选数量，最大200（默认100）")
    parser.add_argument("--max-pages", type=int, default=2,
                        help="每个关键词最多翻页数（默认2，即最多约200条候选）")
    parser.add_argument("--source", choices=["bigan", "crossref"],
                        default="bigan", help="检索来源（默认bigan）")
    parser.add_argument("--lang", choices=["zh", "en"], default="zh",
                        help="输出语言提示；en 默认使用 crossref")

    args = parser.parse_args()
    datatype = TYPE_MAP[args.type]

    source = "crossref" if args.lang == "en" and args.source == "bigan" else args.source
    if source == "crossref":
        refs = fetch_crossref_references(
            args.queries,
            total=args.count,
            min_year=args.min_year,
            page_size=args.page_size,
            max_pages=args.max_pages,
        )
    else:
        refs = fetch_references(
            args.queries,
            total=args.count,
            datatype=datatype,
            min_year=args.min_year,
            page_size=args.page_size,
            max_pages=args.max_pages,
        )

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
