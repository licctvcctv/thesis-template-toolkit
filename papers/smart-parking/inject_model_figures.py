"""Insert model-generated thesis diagrams into the expanded paper JSON.

Expected flow:
  python write_content.py
  python expand_content_to_template.py
  python inject_model_figures.py
  python build.py 城市智慧停车管理系统毕业论文.docx
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name: str):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def dump(name: str, data):
    (HERE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def image(path: str, caption: str, width_cm: float):
    return {"image": path, "caption": caption, "width_cm": width_cm}


def has_image(blocks, path: str):
    return any(isinstance(block, dict) and block.get("image") == path for block in blocks)


def append_image(blocks, path: str, caption: str, width_cm: float):
    if not has_image(blocks, path):
        blocks.append(image(path, caption, width_cm))


def find_section(chapter, title: str):
    for section in chapter.get("sections", []):
        if section.get("title") == title:
            return section
    raise KeyError(title)


def find_subsection(chapter, title: str):
    for section in chapter.get("sections", []):
        for subsection in section.get("subsections", []):
            if subsection.get("title") == title:
                return subsection
    raise KeyError(title)


def set_caption(chapter, path: str, caption: str):
    def visit(blocks):
        for block in blocks:
            if isinstance(block, dict) and block.get("image") == path:
                block["caption"] = caption

    visit(chapter.get("content", []))
    for section in chapter.get("sections", []):
        visit(section.get("content", []))
        for subsection in section.get("subsections", []):
            visit(subsection.get("content", []))


def main():
    ch2 = load("ch2.json")
    for block in ch2.get("content", []):
        if block.get("text", "").startswith("与购物商城模板类似"):
            block["text"] = (
                "本章围绕系统实际用到的前端、后端、数据库、安全认证和可视化技术进行说明。"
                "各技术并不是简单堆叠，而是在系统中分别承担页面展示、业务处理、数据访问、"
                "身份认证和统计分析等职责。"
            )
    dump("ch2.json", ch2)

    for title, path, caption, width in [
        ("2.1 Spring Boot 框架", "images/fig2-1-springboot-layer-model.png", "图2-1 Spring Boot后端分层结构图", 11.8),
        ("2.2 Vue3 与 Vite", "images/fig2-2-vue3-frontend-model.png", "图2-2 Vue3前端项目结构图", 12.0),
        ("2.5 Spring Security 与 JWT", "images/fig2-3-jwt-auth-flow-model.png", "图2-3 JWT认证流程图", 7.4),
    ]:
        append_image(find_section(ch2, title).setdefault("content", []), path, caption, width)
    dump("ch2.json", ch2)

    ch3 = load("ch3.json")
    for title, path, caption, width in [
        ("3.1.1 登录认证与权限需求", "images/fig3-3-admin-auth-usecase-model.png", "图3-3 后台认证模块用例图", 10.3),
        ("3.1.2 停车场管理需求", "images/fig3-4-parking-lot-usecase-model.png", "图3-4 停车场管理用例图", 10.8),
        ("3.1.3 车位管理需求", "images/fig3-5-parking-space-usecase-model.png", "图3-5 车位管理用例图", 10.8),
        ("3.1.4 订单管理需求", "images/fig3-6-order-management-usecase-model.png", "图3-6 订单管理用例图", 10.8),
        ("3.2.3 车位预约需求", "images/fig3-7-user-parking-usecase-model.png", "图3-7 用户停车服务用例图", 8.8),
    ]:
        append_image(find_subsection(ch3, title).setdefault("content", []), path, caption, width)
    for path, caption in [
        ("images/fig3-1-admin-usecase.png", "图3-1 管理员用例图"),
        ("images/fig3-3-admin-auth-usecase-model.png", "图3-2 后台认证模块用例图"),
        ("images/fig3-4-parking-lot-usecase-model.png", "图3-3 停车场管理用例图"),
        ("images/fig3-5-parking-space-usecase-model.png", "图3-4 车位管理用例图"),
        ("images/fig3-6-order-management-usecase-model.png", "图3-5 订单管理用例图"),
        ("images/fig3-2-user-usecase.png", "图3-6 用户端用例图"),
        ("images/fig3-7-user-parking-usecase-model.png", "图3-7 用户停车服务用例图"),
    ]:
        set_caption(ch3, path, caption)
    dump("ch3.json", ch3)

    ch4 = load("ch4.json")
    for title, path, caption, width in [
        ("4.2.1 用户与车辆业务表", "images/fig4-2-user-vehicle-model.png", "图4-2 用户与车辆业务逻辑模型", 11.2),
        ("4.2.2 停车场与车位业务表", "images/fig4-3-lot-space-model.png", "图4-3 停车场与车位业务逻辑模型", 12.0),
        ("4.2.3 订单与支付业务表", "images/fig4-4-order-payment-model.png", "图4-4 订单与支付业务逻辑模型", 12.4),
    ]:
        blocks = find_subsection(ch4, title).setdefault("content", [])
        if not has_image(blocks, path):
            blocks.insert(1, image(path, caption, width))
    dump("ch4.json", ch4)

    ch5 = load("ch5.json")
    append_image(
        find_section(ch5, "5.2 系统功能模块设计").setdefault("content", []),
        "images/fig5-5-backend-resource-structure-model.png",
        "图5-5 后台资源管理业务结构图",
        11.6,
    )
    append_image(
        find_subsection(ch5, "5.2.1 用户端停车服务设计").setdefault("content", []),
        "images/fig5-7-user-portal-structure-model.png",
        "图5-6 用户端停车服务业务结构图",
        11.2,
    )
    flow_blocks = find_section(ch5, "5.3 预约停车业务流程设计").setdefault("content", [])
    append_image(flow_blocks, "images/fig5-6-order-status-flow-model.png", "图5-7 订单状态流转流程图", 8.6)
    append_image(flow_blocks, "images/fig5-8-reserve-timeout-flow-model.png", "图5-8 预约超时任务流程图", 7.8)
    for path, caption in [
        ("images/fig5-1-architecture.png", "图5-1 系统总体架构图"),
        ("images/fig5-5-backend-resource-structure-model.png", "图5-2 后台资源管理业务结构图"),
        ("images/fig5-7-user-portal-structure-model.png", "图5-3 用户端停车服务业务结构图"),
        ("images/fig5-2-order-flow.png", "图5-4 预约停车与计费业务流程图"),
        ("images/fig5-6-order-status-flow-model.png", "图5-5 订单状态流转流程图"),
        ("images/fig5-8-reserve-timeout-flow-model.png", "图5-6 预约超时任务流程图"),
        ("images/fig5-3-auth-flow.png", "图5-7 登录认证与权限校验流程图"),
        ("images/fig5-4-package.png", "图5-8 后端包结构图"),
    ]:
        set_caption(ch5, path, caption)
    dump("ch5.json", ch5)
    print("模型生成图已插入论文 JSON")


if __name__ == "__main__":
    main()
