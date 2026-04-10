# 论文内容管理

每篇论文一个目录，结构如下：

```
papers/
└── zhixue/              ← 智学云课论文
    ├── meta.json            封面/摘要/致谢等元数据
    ├── ch1_introduction.json    第1章 绪论
    ├── ch2_technology.json      第2章 相关技术
    ├── ch3_analysis.json        第3章 系统分析
    ├── ch4_design.json          第4章 系统设计
    ├── ch5_implementation.json  第5章 系统实现
    ├── ch6_testing.json         第6章 系统测试
    ├── ch7_conclusion.json      第7章 总结与展望
    ├── references.json          参考文献
    └── build.py                 组装并导出
```

每个 JSON 文件 < 200 行，包含该章节的标题和段落内容。
build.py 读取所有 JSON，组装成完整数据，调用 generate.py 导出。
```
