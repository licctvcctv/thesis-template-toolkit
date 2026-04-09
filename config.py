"""
论文基本信息配置：封面、摘要、致谢等。
修改这里的数据即可生成不同论文。
"""

# === 封面信息 ===
COVER = {
    "title_zh": "基于深度学习的海洋鱼类图像识别研究",
    "title_en": "Research on Marine Fish Image Recognition Based on Deep Learning",
    "college": "信息学院",
    "class_name": "计算机2201",
    "name": "张三",
    "student_id": "2022001234",
    "advisor": "李教授",
    "year": "2026",
    "month": "4",
}

# === 中文摘要 ===
ABSTRACT_ZH = (
    "随着海洋渔业资源的不断开发利用，海洋鱼类的快速准确识别成为渔业资源管理的重要需求。"
    "传统的鱼类识别方法依赖专家经验，效率低且主观性强。本文提出一种基于深度学习的海洋鱼类图像识别方法，"
    "利用卷积神经网络（CNN）对20种常见海洋鱼类进行自动分类识别。"
    "实验采用自建的海洋鱼类图像数据集，包含10000张标注图片。"
    "通过数据增强、迁移学习和模型融合等策略，最终在测试集上达到了96.5%的识别准确率。"
    "研究结果表明，深度学习方法能够有效解决海洋鱼类图像识别问题，"
    "为海洋渔业资源的智能化管理提供了技术支撑。"
)
KEYWORDS_ZH = "深度学习；鱼类识别；卷积神经网络；图像分类；迁移学习"

# === 英文摘要 ===
ABSTRACT_EN = (
    "With the continuous development and utilization of marine fishery resources, "
    "rapid and accurate identification of marine fish species has become an important "
    "requirement for fishery resource management. This paper proposes a marine fish "
    "image recognition method based on deep learning, using CNN to automatically "
    "classify and identify 20 common marine fish species. The final recognition "
    "accuracy reaches 96.5% on the test set."
)
KEYWORDS_EN = (
    "Deep learning;Fish recognition;Convolutional neural network;"
    "Image classification;Transfer learning"
)

# === 致谢 ===
ACKNOWLEDGEMENT = (
    "本论文的完成离不开许多人的帮助与支持。首先，我要衷心感谢我的指导教师李教授，"
    "在论文选题、研究方法和论文撰写等方面给予了悉心的指导和耐心的帮助。"
    "其次，感谢信息学院的各位老师在我本科四年学习期间的辛勤教导。"
    "同时，感谢实验室的同学们在实验过程中提供的帮助和宝贵建议。"
    "最后，感谢我的家人一直以来的理解、支持与鼓励，使我能够顺利完成学业。"
)
