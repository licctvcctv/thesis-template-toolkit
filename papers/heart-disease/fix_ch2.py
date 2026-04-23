"""AIGC break: ch2.json — 相关技术介绍"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(HERE, "ch2.json")
with open(path, 'r', encoding='utf-8') as f:
    raw = f.read()

replacements = {
    # === 2.1 Hadoop (68.46) ===
    "Hadoop是Apache基金会维护的开源分布式计算平台，核心由HDFS（分布式文件系统）和YARN（资源调度器）两部分组成。":
        "Hadoop是Apache下面的一个开源项目，干的事情就是分布式计算。核心就两块：HDFS管存储，YARN管资源调度。",

    "HDFS把文件切成固定大小的数据块（默认128MB），分散存储在集群的多个节点上，每个块默认保存3份副本。":
        "HDFS的做法是把文件切成固定大小的块（默认128MB），分散放到集群里不同的机器上，每个块存3份。",

    "NameNode负责管理文件的元数据——哪个文件被切成了哪些块、每个块存在哪些节点上；DataNode负责实际的数据读写。":
        "NameNode记的是元数据——哪个文件切成了哪几个块、块在哪台机器上。DataNode就管读写数据本身。",

    "这种架构使Hadoop能处理PB级别的数据，单个节点宕机也不会导致数据丢失。":
        "靠这个架构，PB级的数据能扛得住，某台机器挂了数据也丢不了。",
}

count = 0
for old, new in replacements.items():
    if old in raw:
        raw = raw.replace(old, new)
        count += 1
with open(path, 'w', encoding='utf-8') as f:
    f.write(raw)
print(f"ch2.json: {count}/{len(replacements)} replacements applied")
