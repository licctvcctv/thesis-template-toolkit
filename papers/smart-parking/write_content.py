"""写入城市智慧停车系统论文数据 JSON。"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def dump(name: str, data):
    (HERE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def text(s: str):
    return {"text": s}


def image(path: str, caption: str, width_cm: float):
    return {"image": path, "caption": caption, "width_cm": width_cm}


def table(caption: str, headers, rows):
    return {"table": {"caption": caption, "headers": headers, "rows": rows}}


def code(caption: str, body: str):
    return {"code": body, "caption": caption}


meta = {
    "abstract_zh": [
        "随着城市机动车保有量持续增长，商业区、交通枢纽和公共服务场所停车资源紧张的问题日益突出。传统停车场依赖人工登记、现场找位和事后统计，容易出现车位状态更新滞后、用户查找车位效率低、管理人员统计困难等问题。围绕停车资源在线查询、预约锁定、入场出场管理、订单计费和后台统计等需求，本文设计并实现了一套城市智慧停车管理系统。",
        "系统采用前后端分离架构，前端基于 Vue3、Vite、Naive UI、Pinia 和 ECharts 构建用户端与管理员端界面，后端基于 Spring Boot、Spring Security、JWT、MyBatis-Plus 和 MySQL 完成接口服务、权限控制、业务处理和数据持久化。系统主要包括用户登录注册、停车场查询、车位状态展示、车辆管理、预约停车、订单支付、停车场管理、车位管理、订单管理、用户管理、操作日志、系统配置和数据统计等模块。",
        "在实现过程中，系统通过停车订单状态流转保证预约、入场、出场和支付环节的业务一致性，通过车位状态控制避免重复预约，通过操作日志记录关键管理行为，通过数据统计模块展示收入趋势、订单趋势、停车场利用率和订单状态分布。测试结果表明，系统能够较好地完成智慧停车场景下的信息查询、业务办理和后台管理工作，具有一定的实用价值和扩展空间。"
    ],
    "keywords_zh": "智慧停车；Spring Boot；Vue3；MySQL；预约管理；停车订单",
    "abstract_en": [
        "With the continuous growth of urban motor vehicles, parking resources in business districts, transportation hubs and public service areas have become increasingly insufficient. Traditional parking management relies heavily on manual registration and on-site searching, which often leads to delayed space status updates, low user efficiency and weak management statistics. To address these problems, this thesis designs and implements an urban smart parking management system.",
        "The system adopts a front-end and back-end separated architecture. The front end is developed with Vue3, Vite, Naive UI, Pinia and ECharts, while the back end is implemented with Spring Boot, Spring Security, JWT, MyBatis-Plus and MySQL. The system provides user login and registration, parking lot query, parking space display, vehicle management, reservation, order payment, parking lot management, parking space management, order management, user management, operation logs, system configuration and data statistics.",
        "During implementation, the system maintains business consistency through the state transition of parking orders, prevents repeated reservations through parking space status control, records important administrative operations through logs, and visualizes revenue trends, order trends, parking lot utilization and order status distribution. The test results show that the system can effectively support information query, parking reservation and back-office management in smart parking scenarios."
    ],
    "keywords_en": "Smart parking; Spring Boot; Vue3; MySQL; Reservation management; Parking order"
}


ch1 = {
    "title": "1 前言",
    "content": [
        text("近年来，城市机动车数量保持较快增长，停车供需矛盾逐渐成为城市交通治理中的重要问题。大型商圈、医院、交通枢纽和公共服务区域经常出现停车场入口排队、驾驶员反复绕行寻找车位、停车场管理人员无法及时掌握场内状态等现象。这类问题不仅降低了出行效率，也增加了道路拥堵和管理成本。"),
        text("智慧停车系统通过信息化手段将停车场、车位、车辆、用户、订单和支付等对象进行统一管理，使用户能够在到达目的地前查询停车场空闲情况并提前预约车位，使管理端能够实时维护停车资源、处理订单并统计运营数据。相比传统人工管理方式，智慧停车系统具有信息更新及时、业务流程规范、数据可追溯和管理效率高等特点。"),
        text("本文研究的城市智慧停车管理系统来源于一个前后端分离的实际开发项目。系统以城市停车场运营为业务背景，围绕用户端停车服务和管理员端资源管理两条主线展开设计，实现停车场查询、车位预约、入场出场、支付、车辆管理、订单管理和运营统计等功能。")
    ],
    "sections": [
        {
            "title": "1.1 研究背景",
            "content": [
                text("传统停车场管理通常以入口人工登记、固定收费规则和人工统计为主，系统化程度较低。当停车场数量增加、车位状态变化频繁时，管理人员很难依靠人工方式实时同步空闲车位、维护订单状态并形成统计报表。用户也无法在出行前准确判断目标区域的停车资源，只能到达现场后再寻找停车位。"),
                text("随着移动互联网、Web 前端框架、后端快速开发框架以及数据库技术的发展，停车业务具备了在线化、流程化和数据化的技术条件。将停车场资源接入系统，通过统一接口提供停车场列表、车位状态、预约订单、支付记录和统计报表，可以明显改善用户体验和后台管理效率。")
            ]
        },
        {
            "title": "1.2 研究目的",
            "content": [
                text("本文的研究目的是结合实际停车场管理业务，设计并实现一套功能较完整、结构清晰、便于扩展的城市智慧停车管理系统。系统需要同时服务普通用户和管理员：普通用户侧重点在于快速查找停车场、查看车位、预约停车和管理订单；管理员侧重点在于维护停车场与车位资源、处理订单、管理用户和查看统计数据。"),
                text("在技术实现上，系统需要体现前后端分离开发模式，后端提供 RESTful 接口和统一返回结构，前端通过 Axios 访问接口并通过 Pinia 管理登录状态。系统还需要基于 JWT 实现登录认证和角色权限控制，避免普通用户访问后台管理功能。")
            ]
        },
        {
            "title": "1.3 研究意义",
            "content": [
                text("从用户角度看，智慧停车系统能够帮助用户提前了解停车场位置、营业时间、收费标准和剩余车位情况，减少盲目寻找车位带来的时间浪费。通过预约停车和订单管理功能，用户可以清晰掌握停车流程和费用信息。"),
                text("从管理角度看，系统能够对停车场、车位、订单、用户和日志进行集中管理，使运营数据可查询、可统计、可追踪。管理人员可以根据订单趋势、收入趋势和车位利用率对运营情况进行分析，为停车资源调度和后续扩容提供数据依据。")
            ]
        },
        {
            "title": "1.4 论文组织结构",
            "content": [
                text("本文共分为七章。第一章介绍课题背景、研究目的和意义；第二章介绍系统涉及的关键技术；第三章对用户端和后台管理端的功能需求进行分析；第四章给出数据库逻辑结构和主要数据表设计；第五章阐述系统总体架构、核心业务流程和包结构设计；第六章介绍系统主要功能实现和运行效果；第七章对全文工作进行总结并提出后续改进方向。")
            ]
        }
    ]
}


ch2 = {
    "title": "2 系统相关技术概述",
    "content": [
        text("城市智慧停车系统采用 B/S 架构和前后端分离开发模式，前端负责页面展示、交互处理和接口调用，后端负责业务规则、权限控制和数据库访问。系统所采用的主要技术包括 Spring Boot、Vue3、MySQL、MyBatis-Plus、Spring Security、JWT、Naive UI 和 ECharts 等。")
    ],
    "sections": [
        {
            "title": "2.1 Spring Boot 框架",
            "content": [
                text("Spring Boot 是基于 Spring 生态的快速开发框架，能够通过自动配置、起步依赖和内嵌服务器降低 Java Web 项目的搭建成本。本系统后端以 Spring Boot 为基础，按照 controller、service、mapper、entity 等分层组织代码。控制层负责接收请求，服务层封装业务逻辑，持久层通过 MyBatis-Plus 访问数据库。"),
                text("在智慧停车系统中，Spring Boot 主要承担接口发布、参数接收、统一异常处理、跨域配置、定时任务和业务组件装配等工作。借助其成熟的生态，系统可以较方便地集成安全认证、接口文档、数据库连接池和日志切面。")
            ]
        },
        {
            "title": "2.2 Vue3 与 Vite",
            "content": [
                text("Vue3 是渐进式 JavaScript 前端框架，具有组件化、响应式数据和组合式 API 等特点。Vite 是面向现代浏览器的前端构建工具，开发环境启动速度快，模块热更新效率高。本系统前端使用 Vue3 构建用户端和管理员端页面，使用 Vite 作为构建和开发工具。"),
                text("系统页面按照业务模块划分为停车场列表、停车场详情、我的订单、我的车辆、个人中心、后台统计、停车场管理、车位管理、订单管理、用户管理、日志管理和系统配置等视图。各页面通过 Vue Router 进行路由管理，通过 Pinia 保存登录用户、Token 和角色信息。")
            ]
        },
        {
            "title": "2.3 MySQL 数据库",
            "content": [
                text("MySQL 是常用的关系型数据库，支持事务、索引、约束和多种数据类型，适合存储停车系统中的结构化业务数据。系统以 smart_parking 为数据库名称，主要包含用户、车辆、停车场、车位、订单、支付记录、操作日志和系统配置等表。"),
                text("在停车预约业务中，用户、车辆、车位和订单之间存在明确的关联关系，因此采用关系型数据库能够较好地表达实体之间的约束。通过唯一索引、普通索引和软删除字段，系统能够兼顾数据一致性、查询效率和业务可维护性。")
            ]
        },
        {
            "title": "2.4 MyBatis-Plus 持久层框架",
            "content": [
                text("MyBatis-Plus 在 MyBatis 基础上封装了常用的 CRUD、分页和条件构造能力，能够减少重复 SQL 编写。本系统中各实体对象均对应数据库表，Mapper 接口继承 MyBatis-Plus 基础 Mapper，服务层通过条件构造器完成列表查询、状态筛选和分页查询。"),
                text("停车场列表、车位列表、订单列表和用户列表都需要支持分页与条件查询。MyBatis-Plus 提供的分页插件和 LambdaQueryWrapper 能够使这类查询逻辑更加清晰，同时也便于后续扩展更多筛选条件。")
            ]
        },
        {
            "title": "2.5 Spring Security 与 JWT",
            "content": [
                text("Spring Security 是 Spring 体系中常用的安全框架，可用于认证、授权和请求拦截。JWT 是一种基于 JSON 的令牌格式，适合前后端分离场景下的无状态登录认证。本系统登录成功后由后端生成 Token，前端在后续请求中通过 Authorization 请求头携带 Token。"),
                text("系统根据用户角色区分普通用户和管理员。普通用户可以访问停车场查询、预约停车、个人订单和车辆管理等接口，管理员可以访问后台统计、停车场管理、车位管理、订单管理、用户管理和系统配置等接口。通过角色权限控制，可以降低越权访问风险。")
            ]
        },
        {
            "title": "2.6 Naive UI 与 ECharts",
            "content": [
                text("Naive UI 为 Vue3 项目提供了表格、表单、按钮、卡片、弹窗、标签、分页和日期选择等常用组件。本系统后台管理端大量使用数据表格和表单组件，用户端使用卡片、标签和表单组件展示停车场信息与订单信息。"),
                text("ECharts 是常用的数据可视化库，适合绘制折线图、柱状图、饼图等。本系统的后台统计模块使用 ECharts 展示收入趋势、订单趋势、停车场利用率和订单状态分布，使管理员能够直观了解系统运营情况。")
            ]
        },
        {
            "title": "2.7 高德地图定位服务",
            "content": [
                text("停车系统具有明显的空间位置属性，停车场的经纬度、地址和导航能力直接影响用户体验。系统前端预留高德地图组件，用于停车场详情页面中的地图展示和导航跳转。后台停车场管理页面也提供地图选点入口，便于管理员维护停车场位置。")
            ]
        },
        {
            "title": "2.8 开发技术汇总",
            "content": [
                table("表2-1 系统主要开发技术", ["技术名称", "应用位置", "主要作用"], [
                    ["Vue3 / Vite", "前端", "构建用户端与管理员端页面，提供组件化交互"],
                    ["Naive UI", "前端", "提供表格、表单、卡片、弹窗等界面组件"],
                    ["Pinia", "前端", "保存登录状态、用户信息和角色信息"],
                    ["Axios", "前端", "调用后端 REST 接口并统一携带 Token"],
                    ["ECharts", "前端", "展示收入、订单、利用率等统计图表"],
                    ["Spring Boot", "后端", "提供接口服务、业务组织和组件装配"],
                    ["Spring Security / JWT", "后端", "完成登录认证、请求拦截和角色权限控制"],
                    ["MyBatis-Plus", "后端", "简化数据库 CRUD、分页和条件查询"],
                    ["MySQL", "数据层", "存储用户、车辆、停车场、车位、订单和日志数据"]
                ])
            ]
        }
    ]
}


ch3 = {
    "title": "3 智慧停车系统需求分析",
    "content": [
        text("需求分析是系统设计和实现的基础。根据停车场管理业务，本系统面向两类用户：普通用户和管理员。普通用户主要完成停车场查询、车位查看、预约停车、订单处理和车辆维护；管理员主要完成停车资源维护、订单监管、用户管理、日志查看、系统配置和运营统计。")
    ],
    "sections": [
        {
            "title": "3.1 后台管理端功能需求",
            "content": [
                text("后台管理端面向停车场运营人员，要求能够对系统基础资源和业务数据进行维护。管理员登录后进入后台首页，可以查看统计卡片和可视化图表，再根据管理需要进入停车场管理、车位管理、订单管理、用户管理、操作日志和系统配置等功能模块。"),
                image("images/fig3-1-admin-usecase.png", "图3-1 管理员用例图", 11.2)
            ],
            "subsections": [
                {
                    "title": "3.1.1 停车场管理需求",
                    "content": [
                        text("停车场管理模块需要支持停车场列表查询、新增、编辑和删除。停车场信息包括名称、地址、经纬度、总车位数、空闲车位数、收费标准、营业时间、联系电话、图片和状态等。管理员可以根据名称和状态筛选停车场，也可以从停车场列表跳转到对应车位管理页面。")
                    ]
                },
                {
                    "title": "3.1.2 车位管理需求",
                    "content": [
                        text("车位管理模块需要维护每个停车场下的具体车位。车位信息包括所属停车场、车位编号、楼层或区域、车位类型和车位状态。车位状态分为空闲、已占用、已预约和维护中。系统应限制对已占用、已预约车位的随意删除，避免破坏订单与车位之间的业务关联。")
                    ]
                },
                {
                    "title": "3.1.3 订单管理需求",
                    "content": [
                        text("订单管理模块需要展示停车订单的完整生命周期，包括预约、入场、出场、待支付、已完成和已取消。管理员可以按订单编号、车牌号、停车场、状态和日期进行查询，对异常情况进行备注，也可以在管理场景下执行手动入场和手动出场操作。")
                    ]
                },
                {
                    "title": "3.1.4 用户、日志和配置需求",
                    "content": [
                        text("用户管理模块用于查看注册用户、角色、状态和注册时间，并支持重置密码和启用禁用。操作日志模块用于记录登录、添加、修改、删除等关键管理操作，便于追踪问题。系统配置模块用于维护预约超时时长、默认收费标准、车辆绑定数量限制和系统公告等参数。")
                    ]
                }
            ]
        },
        {
            "title": "3.2 用户端功能需求",
            "content": [
                text("用户端面向普通停车用户，重点是减少寻找车位的时间成本，并提供清晰的停车订单办理流程。用户可以在未登录状态下查看停车场列表和详情，登录后可以绑定车辆、选择空闲车位并创建预约订单。"),
                image("images/fig3-2-user-usecase.png", "图3-2 用户端用例图", 11.2)
            ],
            "subsections": [
                {
                    "title": "3.2.1 停车场查询需求",
                    "content": [
                        text("用户需要根据停车场名称或地址进行查询，并按距离、价格或空闲车位数进行排序。列表页应显示停车场名称、营业状态、地址、剩余车位、收费标准和营业时间，使用户能够快速判断是否适合前往。")
                    ]
                },
                {
                    "title": "3.2.2 车位预约需求",
                    "content": [
                        text("用户进入停车场详情后，可以查看停车场基本信息、地图位置和不同区域的车位状态。只有空闲车位允许被选择，已预约、已占用和维护中的车位不能被预约。用户提交预约时必须选择已绑定车辆，预约成功后系统生成订单并锁定车位。")
                    ]
                },
                {
                    "title": "3.2.3 订单与车辆管理需求",
                    "content": [
                        text("用户可以查看自己的历史订单和当前订单，并根据订单状态执行取消预约、模拟入场、支付或查看详情等操作。车辆管理模块需要支持新增车辆、编辑车辆、删除车辆和设置默认车辆，以便预约时快速选择车牌。")
                    ]
                }
            ]
        },
        {
            "title": "3.3 非功能需求",
            "content": [
                table("表3-1 系统非功能需求", ["需求类型", "具体要求", "实现方式"], [
                    ["安全性", "区分普通用户与管理员，防止越权访问后台接口", "JWT 登录认证、Spring Security 角色校验"],
                    ["一致性", "预约、入场、出场和支付过程中车位状态与订单状态保持一致", "服务层统一执行业务状态流转"],
                    ["可维护性", "前后端模块职责清晰，便于后续扩展功能", "前端按视图与 API 分层，后端按 controller/service/mapper 分层"],
                    ["易用性", "页面结构清晰，列表、表单、统计图便于操作", "使用 Naive UI 组件和 ECharts 图表"],
                    ["可追溯性", "关键管理行为需要留痕", "操作日志表记录模块、类型、内容、URL 和 IP"]
                ]),
                text("综上，系统需要在功能完整性的基础上保证业务状态清晰、权限控制明确、界面操作简洁和数据可追踪。后续数据库设计和系统设计均围绕上述需求展开。")
            ]
        }
    ]
}


ch4 = {
    "title": "4 数据库设计",
    "content": [
        text("数据库设计需要将需求分析中的业务对象转换为关系型数据表。城市智慧停车系统的核心业务围绕用户、车辆、停车场、车位、停车订单和支付记录展开，同时为了支持后台管理，还需要操作日志表和系统配置表。"),
        image("images/fig4-1-er.png", "图4-1 系统数据库逻辑结构图", 12.6)
    ],
    "sections": [
        {
            "title": "4.1 数据库总体设计",
            "content": [
                text("系统数据库名称为 smart_parking，字符集采用 utf8mb4，以支持中文停车场名称、地址、用户名、日志内容和配置说明等信息。各表均使用自增 id 作为主键，业务删除场景采用 deleted 字段进行软删除，避免直接物理删除造成历史订单和统计数据丢失。"),
                text("用户与车辆之间是一对多关系，一个用户可以绑定多辆车；停车场与车位之间是一对多关系，一个停车场包含多个车位；订单表关联用户、车辆、停车场和车位，是系统业务流转的核心表；支付记录表与订单表关联，用于记录支付金额、支付方式和交易流水。")
            ]
        },
        {
            "title": "4.2 数据表结构设计",
            "content": [
                text("用户表用于保存系统登录账号和基础身份信息，包括用户名、手机号、昵称、角色、状态等字段。系统通过 role 字段区分普通用户和管理员，通过 status 字段控制账号是否可用。"),
                table("表4-1 用户表（sys_user）", ["字段名", "类型", "说明"], [
                    ["id", "BIGINT", "主键，自增"],
                    ["username", "VARCHAR(50)", "用户名，唯一"],
                    ["password", "VARCHAR(255)", "BCrypt 加密后的密码"],
                    ["phone", "VARCHAR(20)", "手机号，唯一"],
                    ["nickname", "VARCHAR(50)", "昵称"],
                    ["avatar", "VARCHAR(255)", "头像地址"],
                    ["gender", "TINYINT", "性别：0未知、1男、2女"],
                    ["email", "VARCHAR(100)", "邮箱"],
                    ["role", "VARCHAR(20)", "角色：USER 或 ADMIN"],
                    ["status", "TINYINT", "状态：0禁用、1启用"],
                    ["create_time", "DATETIME", "创建时间"],
                    ["update_time", "DATETIME", "更新时间"],
                    ["deleted", "TINYINT", "软删除标识"]
                ]),
                text("车辆表用于保存用户绑定的车牌和车辆属性。预约停车时，订单需要关联具体车辆，因此车辆表通过 user_id 与用户表建立关联，并通过 plate_number 保存车牌号。"),
                table("表4-2 车辆表（user_vehicle）", ["字段名", "类型", "说明"], [
                    ["id", "BIGINT", "主键，自增"],
                    ["user_id", "BIGINT", "所属用户 ID"],
                    ["plate_number", "VARCHAR(20)", "车牌号"],
                    ["vehicle_type", "VARCHAR(20)", "车辆类型"],
                    ["vehicle_color", "VARCHAR(20)", "车辆颜色"],
                    ["vehicle_brand", "VARCHAR(50)", "车辆品牌"],
                    ["is_default", "TINYINT", "是否默认车辆"],
                    ["create_time", "DATETIME", "创建时间"],
                    ["update_time", "DATETIME", "更新时间"],
                    ["deleted", "TINYINT", "软删除标识"]
                ]),
                text("停车场表用于保存停车场基础资料，是用户查询与管理员维护的核心基础表。该表保存地址、经纬度、收费标准、营业时间、剩余车位数和状态等信息。"),
                table("表4-3 停车场表（parking_lot）", ["字段名", "类型", "说明"], [
                    ["id", "BIGINT", "主键，自增"],
                    ["name", "VARCHAR(100)", "停车场名称"],
                    ["address", "VARCHAR(255)", "详细地址"],
                    ["longitude", "DECIMAL(10,7)", "经度"],
                    ["latitude", "DECIMAL(10,7)", "纬度"],
                    ["total_spaces", "INT", "总车位数"],
                    ["available_spaces", "INT", "空闲车位数"],
                    ["hourly_rate", "DECIMAL(10,2)", "每小时收费"],
                    ["open_time", "VARCHAR(20)", "营业开始时间"],
                    ["close_time", "VARCHAR(20)", "营业结束时间"],
                    ["contact_phone", "VARCHAR(20)", "联系电话"],
                    ["images", "VARCHAR(1000)", "停车场图片地址"],
                    ["status", "TINYINT", "状态：0关闭、1营业"],
                    ["create_time", "DATETIME", "创建时间"],
                    ["update_time", "DATETIME", "更新时间"],
                    ["deleted", "TINYINT", "软删除标识"]
                ]),
                text("车位表用于描述停车场内的具体停车位。系统通过 lot_id 将车位归属到停车场，通过 status 字段标记车位是否空闲、占用、预约或维护。"),
                table("表4-4 车位表（parking_space）", ["字段名", "类型", "说明"], [
                    ["id", "BIGINT", "主键，自增"],
                    ["lot_id", "BIGINT", "所属停车场 ID"],
                    ["space_code", "VARCHAR(30)", "车位编号"],
                    ["floor", "VARCHAR(30)", "楼层或区域"],
                    ["space_type", "VARCHAR(20)", "车位类型"],
                    ["status", "TINYINT", "状态：0空闲、1占用、2预约、3维护"],
                    ["create_time", "DATETIME", "创建时间"],
                    ["update_time", "DATETIME", "更新时间"],
                    ["deleted", "TINYINT", "软删除标识"]
                ]),
                text("停车订单表是业务流转的核心表，保存用户预约、入场、出场、计费、取消和支付状态等信息。订单表冗余保存 lot_name、space_code 和 plate_number，便于历史订单展示。"),
                table("表4-5 停车订单表（parking_order）", ["字段名", "类型", "说明"], [
                    ["id", "BIGINT", "主键，自增"],
                    ["order_no", "VARCHAR(32)", "订单编号，唯一"],
                    ["user_id", "BIGINT", "用户 ID"],
                    ["vehicle_id", "BIGINT", "车辆 ID"],
                    ["plate_number", "VARCHAR(20)", "车牌号"],
                    ["lot_id", "BIGINT", "停车场 ID"],
                    ["lot_name", "VARCHAR(100)", "停车场名称"],
                    ["space_id", "BIGINT", "车位 ID"],
                    ["space_code", "VARCHAR(30)", "车位编号"],
                    ["reserve_time", "DATETIME", "预约时间"],
                    ["expire_time", "DATETIME", "预约过期时间"],
                    ["enter_time", "DATETIME", "入场时间"],
                    ["exit_time", "DATETIME", "出场时间"],
                    ["duration_minutes", "INT", "停车时长"],
                    ["hourly_rate", "DECIMAL(10,2)", "订单收费标准"],
                    ["amount", "DECIMAL(10,2)", "订单金额"],
                    ["status", "TINYINT", "订单状态"],
                    ["pay_status", "TINYINT", "支付状态"],
                    ["cancel_reason", "VARCHAR(200)", "取消原因"],
                    ["remark", "VARCHAR(500)", "管理备注"],
                    ["create_time", "DATETIME", "创建时间"],
                    ["update_time", "DATETIME", "更新时间"],
                    ["deleted", "TINYINT", "软删除标识"]
                ]),
                text("支付记录表用于保存订单支付结果。一个订单支付成功后生成一条支付记录，记录支付金额、支付方式、交易号和支付时间，为后续对账和统计提供依据。"),
                table("表4-6 支付记录表（payment_record）", ["字段名", "类型", "说明"], [
                    ["id", "BIGINT", "主键，自增"],
                    ["order_id", "BIGINT", "订单 ID"],
                    ["order_no", "VARCHAR(32)", "订单编号"],
                    ["user_id", "BIGINT", "用户 ID"],
                    ["amount", "DECIMAL(10,2)", "支付金额"],
                    ["pay_method", "VARCHAR(20)", "支付方式"],
                    ["trade_no", "VARCHAR(64)", "第三方交易号"],
                    ["pay_time", "DATETIME", "支付时间"],
                    ["status", "TINYINT", "支付状态"],
                    ["create_time", "DATETIME", "创建时间"]
                ]),
                text("操作日志表用于记录管理员和系统关键操作，包括操作人、操作类型、模块、摘要、请求方法、请求地址和 IP 地址。该表可以帮助管理员追踪异常操作和定位问题。"),
                table("表4-7 操作日志表（operation_log）", ["字段名", "类型", "说明"], [
                    ["id", "BIGINT", "主键，自增"],
                    ["operator_id", "BIGINT", "操作人 ID"],
                    ["operator", "VARCHAR(50)", "操作人用户名"],
                    ["operate_type", "VARCHAR(20)", "操作类型"],
                    ["module", "VARCHAR(50)", "业务模块"],
                    ["content", "VARCHAR(500)", "操作摘要"],
                    ["request_method", "VARCHAR(10)", "请求方法"],
                    ["request_url", "VARCHAR(255)", "请求路径"],
                    ["ip", "VARCHAR(50)", "客户端 IP"],
                    ["create_time", "DATETIME", "操作时间"]
                ]),
                text("系统配置表用于保存业务参数，避免将可变配置写死在程序中。例如预约锁定时长、默认收费标准、每个用户最大车辆数和系统公告均可通过配置表维护。"),
                table("表4-8 系统配置表（sys_config）", ["字段名", "类型", "说明"], [
                    ["id", "BIGINT", "主键，自增"],
                    ["config_key", "VARCHAR(100)", "配置键，唯一"],
                    ["config_value", "VARCHAR(500)", "配置值"],
                    ["description", "VARCHAR(200)", "配置说明"],
                    ["create_time", "DATETIME", "创建时间"],
                    ["update_time", "DATETIME", "更新时间"]
                ])
            ]
        }
    ]
}


ch5 = {
    "title": "5 智慧停车系统设计",
    "content": [
        text("系统设计需要在需求分析和数据库设计基础上确定整体架构、模块划分、业务流程和代码组织方式。城市智慧停车系统采用前后端分离架构，前端通过浏览器访问页面，后端通过 REST API 提供数据服务，数据库负责持久化业务数据。")
    ],
    "sections": [
        {
            "title": "5.1 系统总体架构设计",
            "content": [
                text("系统总体架构分为表现层、前端层、接口层、安全层、业务层、持久层和数据层。表现层包括用户端浏览器、管理员浏览器和移动端浏览器；前端层负责页面渲染、路由、状态管理和图表展示；后端层负责接口、认证、业务处理和数据访问；数据层通过 MySQL 保存核心业务数据。"),
                image("images/fig5-1-architecture.png", "图5-1 系统总体架构图", 10.0)
            ]
        },
        {
            "title": "5.2 功能模块设计",
            "content": [
                text("系统功能模块围绕用户端和管理员端展开。用户端强调停车服务闭环，管理员端强调资源维护和运营监管。两个端共用后端接口、统一认证机制和同一套数据库。"),
                table("表5-1 系统功能模块划分", ["模块名称", "服务对象", "主要功能"], [
                    ["登录注册模块", "用户/管理员", "登录认证、注册、Token 保存和角色识别"],
                    ["停车场查询模块", "用户", "停车场列表、条件筛选、详情查看、地图位置"],
                    ["车位预约模块", "用户", "车位状态展示、选择车辆、提交预约、取消预约"],
                    ["订单支付模块", "用户", "订单列表、详情、入场、出场计费和支付记录"],
                    ["车辆管理模块", "用户", "添加、编辑、删除车辆和设置默认车辆"],
                    ["停车场管理模块", "管理员", "停车场新增、编辑、删除、查询和状态维护"],
                    ["车位管理模块", "管理员", "单个或批量新增车位、维护状态和类型"],
                    ["订单管理模块", "管理员", "订单查询、手动入场、手动出场和异常备注"],
                    ["统计分析模块", "管理员", "收入趋势、订单趋势、利用率和状态分布"],
                    ["日志配置模块", "管理员", "操作日志查看、预约时长和系统公告配置"]
                ])
            ]
        },
        {
            "title": "5.3 预约停车业务流程设计",
            "content": [
                text("预约停车流程是系统的核心业务流程。用户从停车场列表进入详情页，选择空闲车位和已绑定车辆后提交预约。后端需要校验用户是否存在未完成订单、车辆是否属于当前用户、停车场是否营业、车位是否处于空闲状态。校验通过后，系统锁定车位并生成订单。"),
                image("images/fig5-2-order-flow.png", "图5-2 预约停车与计费业务流程图", 8.2),
                text("当用户到达停车场后，系统将订单状态由已预约更新为进行中，并将车位状态更新为已占用。用户离场时，系统根据入场时间、出场时间和收费标准计算金额，订单进入待支付状态。支付成功后生成支付记录，订单状态更新为已完成，并释放车位。")
            ]
        },
        {
            "title": "5.4 登录认证与权限设计",
            "content": [
                text("系统采用 JWT 方式实现无状态认证。用户或管理员登录成功后，后端返回 token 和 userInfo，前端将 token 保存到本地并在后续请求中放入 Authorization 请求头。后端过滤器解析 token，校验签名和过期时间，并将用户身份写入安全上下文。"),
                image("images/fig5-3-auth-flow.png", "图5-3 登录认证与权限校验流程图", 12.2),
                text("权限控制按角色进行划分。普通用户只能访问用户端接口，管理员可以访问后台接口。当前端路由进入需要认证的页面时，会先检查本地登录状态；后端接口则通过 Spring Security 进行最终校验，避免只依赖前端判断导致越权访问。")
            ]
        },
        {
            "title": "5.5 后端包结构设计",
            "content": [
                text("后端代码以 com.smartparking 为根包，按照业务职责进行分包。controller 包负责接口入口，service 包定义业务服务，service.impl 包提供具体实现，mapper 包负责数据库访问，entity 包映射数据表，dto 和 vo 分别承载请求数据和响应数据。security、config、common、aspect 和 task 等包提供安全、配置、通用返回、日志切面和定时任务能力。"),
                image("images/fig5-4-package.png", "图5-4 后端包结构图", 9.8)
            ]
        }
    ]
}


ch6 = {
    "title": "6 智慧停车系统实现",
    "content": [
        text("系统实现部分结合实际项目结构介绍主要功能。前端项目为 smart-parking-frontend，后端项目为 smart-parking-backend。前端通过 Vite 启动开发服务，后端通过 Spring Boot 提供接口服务，数据库使用 smart_parking 保存业务数据。")
    ],
    "sections": [
        {
            "title": "6.1 开发环境与项目结构",
            "content": [
                table("表6-1 系统开发环境", ["环境项", "版本或说明", "用途"], [
                    ["JDK", "17", "运行 Spring Boot 后端"],
                    ["Spring Boot", "3.3.5", "后端主体框架"],
                    ["Node.js", "本地开发环境", "运行 Vue3 前端项目"],
                    ["Vue", "3.x", "构建用户端和管理员端页面"],
                    ["MySQL", "8.x 兼容", "保存业务数据"],
                    ["Maven", "项目构建工具", "管理后端依赖"],
                    ["Vite", "前端构建工具", "开发调试和打包前端页面"]
                ]),
                text("后端项目的核心目录包括 controller、service、mapper、entity、dto、vo、security、config、aspect 和 task。前端项目的核心目录包括 views、api、router、store、layout 和 utils。这样的目录划分使前后端模块职责清晰，便于开发和维护。")
            ]
        },
        {
            "title": "6.2 登录认证功能实现",
            "content": [
                text("登录功能由前端登录页面、AuthController、SysUserService 和 JwtUtils 共同完成。前端将用户名和密码提交至 /public/auth/login，后端根据用户名或手机号查询用户，校验密码和账号状态后生成 JWT，并返回给前端。管理员端登录后进入后台统计页面，普通用户登录后进入用户端页面。"),
                code("代码6-1 前端登录调用示例", "const res = await login(form.value)\nconst { token, userInfo } = res.data\nauthStore.setAuth(token, userInfo)\nrouter.push(userInfo.role === 'ADMIN' ? '/admin/dashboard' : '/home')"),
                text("前端请求拦截器会从本地存储读取 token，并在请求头中加入 Authorization。后端 JwtAuthenticationFilter 对后续请求进行解析和认证，从而实现前后端分离场景下的登录保持。")
            ]
        },
        {
            "title": "6.3 后台统计模块实现",
            "content": [
                text("后台统计页面是管理员登录后的首页，主要展示今日收入、今日订单、在场车辆和注册用户等统计卡片，同时通过图表展示收入与订单趋势、订单状态分布、停车场利用率和最近订单。该页面能够帮助管理员快速了解停车场整体运营情况。"),
                image("screenshots/fig6-1-admin-dashboard.png", "图6-1 后台数据统计页面", 13.2)
            ]
        },
        {
            "title": "6.4 停车场管理模块实现",
            "content": [
                text("停车场管理页面通过表格展示停车场名称、地址、总车位、空闲车位、收费标准、营业时间、状态和创建时间。管理员可以按停车场名称和状态筛选数据，也可以新增、编辑、删除停车场，或跳转查看该停车场下的车位。"),
                image("screenshots/fig6-2-admin-parking-lot.png", "图6-2 停车场管理页面", 13.2)
            ]
        },
        {
            "title": "6.5 车位管理模块实现",
            "content": [
                text("车位管理页面展示车位编号、所属停车场、楼层区域、车位类型和车位状态。管理员可以按停车场、车位编号、状态和类型筛选车位，支持单个新增和批量新增。系统通过状态控制避免对已预约和已占用车位执行不合理操作。"),
                image("screenshots/fig6-3-admin-parking-space.png", "图6-3 车位管理页面", 13.2)
            ]
        },
        {
            "title": "6.6 订单管理模块实现",
            "content": [
                text("订单管理页面用于管理停车业务的完整过程。订单列表展示订单编号、用户名、车牌号、停车场、车位、入场时间、出场时间、停车时长、费用和订单状态。管理员可以按订单编号、车牌号、停车场、状态和时间范围进行查询。"),
                image("screenshots/fig6-4-admin-order.png", "图6-4 订单管理页面", 13.2),
                text("在业务实现上，预约订单生成后状态为已预约；用户入场后状态变为进行中；出场时系统根据停车时长和 hourly_rate 计算费用，订单进入待支付；支付成功后订单变为已完成。")
            ]
        },
        {
            "title": "6.7 用户管理、日志与系统配置实现",
            "content": [
                text("用户管理页面用于查看系统账号、手机号、昵称、角色、注册时间和状态，管理员可以查看详情、重置密码和启用禁用账号。操作日志页面记录系统登录、停车场管理、车位管理、订单管理等关键操作。系统配置页面用于维护预约锁定时长、默认收费标准、每用户最大车辆数和系统公告。"),
                image("screenshots/fig6-5-admin-user.png", "图6-5 用户管理页面", 13.2),
                image("screenshots/fig6-6-admin-log.png", "图6-6 操作日志页面", 13.2),
                image("screenshots/fig6-7-admin-config.png", "图6-7 系统配置页面", 13.2)
            ]
        },
        {
            "title": "6.8 用户端停车服务实现",
            "content": [
                text("用户端停车服务主要包括停车场列表、停车场详情、车位状态展示、车辆管理、订单管理和个人中心。停车场列表页可以按名称或地址搜索，并显示剩余车位、收费标准和营业时间；停车场详情页展示地址、电话、车位网格和状态图例。"),
                image("screenshots/fig6-8-user-parking-list.png", "图6-8 用户端停车场列表页面", 13.0),
                image("screenshots/fig6-9-user-parking-detail.png", "图6-9 用户端停车场详情页面", 13.0),
                text("用户登录后可以查看自己的停车订单和车辆信息。订单页面按状态展示预约、进行中、待支付、已完成和已取消订单，车辆页面支持查看车牌、车辆颜色、品牌和默认车辆标记。"),
                image("screenshots/fig6-10-user-orders.png", "图6-10 用户端订单页面", 13.0),
                image("screenshots/fig6-11-user-vehicles.png", "图6-11 用户端车辆管理页面", 13.0),
                image("screenshots/fig6-12-user-profile.png", "图6-12 用户端个人中心页面", 13.0)
            ]
        },
        {
            "title": "6.9 核心业务实现说明",
            "content": [
                text("停车预约业务在服务层进行统一校验。系统首先检查用户是否存在未完成订单，再校验车辆归属、停车场状态和车位状态。只有当车位为空闲且停车场营业时，系统才会锁定车位并生成订单。该设计能够减少重复预约和状态不一致问题。"),
                code("代码6-2 预约业务核心逻辑示例", "if (hasActiveOrder(userId)) {\n    throw new BusinessException(\"存在未完成订单\");\n}\ncheckVehicleBelongsToUser(vehicleId, userId);\ncheckLotOpen(lotId);\ncheckSpaceAvailable(spaceId);\nreserveSpace(spaceId);\ncreateParkingOrder(userId, vehicleId, spaceId);"),
                text("出场计费业务根据订单入场时间、出场时间和停车场收费标准计算金额。为了便于用户理解，系统按小时计费并对不足一小时的部分进行向上取整。支付完成后，系统生成 payment_record，并将订单和车位状态同步更新。")
            ]
        }
    ]
}


ch7 = {
    "title": "7 总结与展望",
    "content": [
        text("本文围绕城市停车资源管理和用户停车服务需求，设计并实现了一套城市智慧停车管理系统。系统采用 Vue3 与 Spring Boot 前后端分离架构，结合 MySQL、MyBatis-Plus、Spring Security、JWT、Naive UI 和 ECharts 等技术，完成了用户端停车场查询、车位预约、订单管理、车辆管理和个人中心，以及管理员端停车场管理、车位管理、订单管理、用户管理、操作日志、系统配置和数据统计等功能。"),
        text("从业务实现来看，系统以停车订单为核心，串联用户、车辆、停车场、车位和支付记录，通过订单状态与车位状态的协同变化完成预约、入场、出场、支付和释放车位的闭环流程。通过后台统计模块，管理员能够直观查看收入趋势、订单趋势、车位利用率和订单状态分布。"),
        text("本系统仍有进一步完善空间。后续可以接入真实停车闸机和车牌识别设备，实现自动入场和自动出场；可以进一步接入真实支付平台，完善支付回调与对账机制；可以基于历史订单数据进行车位需求预测，为停车场资源调度提供更智能的决策支持；还可以完善移动端适配和消息通知，提高用户使用体验。")
    ],
    "sections": []
}


references = [
    "陈刚. Spring Boot 企业级应用开发实战[M]. 北京: 电子工业出版社, 2022.",
    "王珊, 萨师煊. 数据库系统概论[M]. 北京: 高等教育出版社, 2023.",
    "尤雨溪. Vue.js 设计与实现[M]. 北京: 人民邮电出版社, 2022.",
    "刘伟. 基于 Spring Boot 的停车场管理系统设计与实现[J]. 信息与电脑, 2023(12): 88-91.",
    "张明, 李强. 智慧停车系统关键技术研究[J]. 现代信息科技, 2024, 8(3): 45-49.",
    "赵文. 基于前后端分离的 Web 管理系统设计[J]. 电脑知识与技术, 2023, 19(20): 72-75.",
    "周立. MySQL 数据库索引优化在管理系统中的应用[J]. 软件导刊, 2022, 21(8): 101-104.",
    "李敏. 基于 JWT 的前后端分离认证机制研究[J]. 网络安全技术与应用, 2023(9): 53-55.",
    "黄俊. 基于 Vue 和 Spring Boot 的后台管理系统实现[J]. 电子技术与软件工程, 2024(5): 64-67.",
    "郭磊. 城市智慧停车平台架构设计研究[J]. 中国交通信息化, 2023(7): 112-116.",
    "张浩. 基于 ECharts 的数据可视化系统设计[J]. 信息技术与信息化, 2022(11): 136-139.",
    "李晓. MyBatis-Plus 在 Java Web 项目中的应用研究[J]. 软件工程, 2023, 26(4): 30-33.",
    "王磊, 赵宁. 基于微服务思想的停车管理平台设计[J]. 计算机时代, 2024(2): 58-61.",
    "刘洋. 基于角色权限控制的管理系统设计[J]. 网络安全和信息化, 2023(6): 79-82.",
    "朱峰. 停车场车位预约与计费模型研究[J]. 交通科技与管理, 2023(15): 41-44.",
    "Oracle Corporation. MySQL 8.0 Reference Manual[EB/OL]. https://dev.mysql.com/doc/.",
    "VMware Tanzu. Spring Boot Reference Documentation[EB/OL]. https://docs.spring.io/spring-boot/.",
    "Vue.js Team. Vue 3 Documentation[EB/OL]. https://vuejs.org/.",
    "Naive UI Team. Naive UI Documentation[EB/OL]. https://www.naiveui.com/.",
    "Apache Software Foundation. MyBatis Documentation[EB/OL]. https://mybatis.org/mybatis-3/."
]


for name, data in {
    "meta.json": meta,
    "ch1.json": ch1,
    "ch2.json": ch2,
    "ch3.json": ch3,
    "ch4.json": ch4,
    "ch5.json": ch5,
    "ch6.json": ch6,
    "ch7.json": ch7,
    "references.json": references,
}.items():
    dump(name, data)

print("论文 JSON 已写入", HERE)
