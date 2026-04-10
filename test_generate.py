"""
用 3 个模板分别生成测试论文。
正文通过 Jinja2 循环生成（不用 subdoc），格式从模板继承。
"""
import os
from docxtpl import DocxTemplate
from builder import build_references

# 测试数据 - 标题不含编号（由模板格式自动编号或直接显示）
TEST_CHAPTERS = [
    {
        "title": "绪论",
        "sections": [
            {
                "title": "研究背景",
                "content": [
                    "随着人工智能技术的发展，图像识别成为计算机视觉领域的研究热点。",
                    "深度学习方法在该领域取得了显著成果，推动了工业检测、医疗诊断等应用。",
                ],
                "subsections": [
                    {
                        "title": "国内研究现状",
                        "content": [
                            "国内学者在图像识别领域开展了大量研究工作。",
                        ],
                    },
                ],
            },
        ],
    },
    {
        "title": "系统设计",
        "sections": [
            {
                "title": "总体架构",
                "content": [
                    "系统采用B/S架构，前端使用React框架，后端使用Python Flask。",
                ],
                "subsections": [],
            },
        ],
    },
]

TEST_REFS = [
    "何凯明. 深度残差学习[C]. CVPR, 2016.",
    "李明. 图像识别综述[J]. 计算机学报, 2024.",
]

TEST_DATA = {
    "title_zh": "基于深度学习的图像识别系统设计与实现",
    "title_en": "Design and Implementation of Image Recognition System Based on Deep Learning",
    "name": "张三",
    "student_id": "2022001234",
    "college": "信息工程学院",
    "class_name": "计算机2201",
    "major": "计算机科学与技术",
    "advisor": "李教授",
    "advisor_in": "李明",
    "advisor_in_title": "副教授",
    "advisor_out": "",
    "advisor_out_title": "",
    "year": "2026",
    "month": "5",
    "届": "2026",
    "abstract_zh": "本文设计并实现了基于深度学习的图像识别系统，识别准确率达96.5%。",
    "keywords_zh": "深度学习；图像识别；卷积神经网络",
    "abstract_en": "This paper designs an image recognition system based on deep learning with 96.5% accuracy.",
    "keywords_en": "Deep learning;Image recognition;CNN",
    "acknowledgement": "感谢指导教师的悉心指导，感谢同学们的帮助。",
    "appendix_content": "附录内容",
}

templates = [
    ("output/A_template.docx", "output/A_output.docx", "A-上海海洋"),
    ("output/B_template.docx", "output/B_output.docx", "B-陕西商贸"),
    ("output/C_template.docx", "output/C_output.docx", "C-毕设模版"),
]

for tpl, out, label in templates:
    if not os.path.exists(tpl):
        print(f"  {label}: 模板不存在，跳过")
        continue
    try:
        doc = DocxTemplate(tpl)
        refs_sd = build_references(doc, TEST_REFS)
        ctx = {
            **TEST_DATA,
            "chapters": TEST_CHAPTERS,  # 直接传给模板循环
            "refs_subdoc": refs_sd,
        }
        doc.render(ctx)
        doc.save(out)
        print(f"  {label}: {out}")
    except Exception as e:
        print(f"  {label}: 错误 - {e}")
