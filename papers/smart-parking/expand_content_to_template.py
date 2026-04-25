"""Expand the smart-parking thesis JSON toward the shop-mall template density.

Run after write_content.py when the base JSON needs to be regenerated.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name: str):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def dump(name: str, data):
    (HERE / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def text(value: str):
    return {"text": value}


def image(path: str, caption: str, width_cm: float):
    return {"image": path, "caption": caption, "width_cm": width_cm}


def table(caption: str, headers, rows, col_widths=None):
    data = {"caption": caption, "headers": headers, "rows": rows}
    if col_widths:
        data["col_widths"] = col_widths
    return {"table": data}


def code(caption: str, body: str):
    return {"code": body, "caption": caption}


def extend_section(chapter, title, paras):
    for sec in chapter.get("sections", []):
        if sec.get("title") == title:
            sec.setdefault("content", []).extend(text(p) for p in paras)
            return
    raise KeyError(title)


def extend_subsection(chapter, title, paras):
    for sec in chapter.get("sections", []):
        for sub in sec.get("subsections", []):
            if sub.get("title") == title:
                sub.setdefault("content", []).extend(text(p) for p in paras)
                return
    raise KeyError(title)


def table_from(chapter, caption_prefix):
    def walk(blocks):
        for block in blocks:
            if "table" in block and block["table"].get("caption", "").startswith(caption_prefix):
                return block
        return None

    found = walk(chapter.get("content", []))
    if found:
        return found
    for sec in chapter.get("sections", []):
        found = walk(sec.get("content", []))
        if found:
            return found
        for sub in sec.get("subsections", []):
            found = walk(sub.get("content", []))
            if found:
                return found
    raise KeyError(caption_prefix)


def module_paras(name, actor, data, actions, rule, output):
    return [
        f"{name}模块面向{actor}，主要围绕{data}展开。该模块不是孤立页面，而是与登录认证、数据表约束、业务状态流转和操作日志共同工作，因此设计时需要同时考虑前端交互、后端校验和数据库一致性。用户在页面上看到的是列表、表单和按钮，系统内部则需要完成参数接收、权限判断、条件查询、事务提交和结果返回等步骤。",
        f"在业务处理过程中，{name}模块重点完成{actions}。前端负责收集查询条件和表单字段，并通过统一请求封装调用后端接口；后端控制层负责参数校验和入口分发，服务层根据业务规则执行新增、修改、删除或状态变更，持久层再将最终结果写入 MySQL。这样的分层方式能够减少页面逻辑和业务逻辑之间的耦合。",
        f"{name}模块的关键规则是{rule}。当规则校验失败时，后端通过统一异常处理返回明确提示，前端再以消息提示或表单校验的方式反馈给用户；当操作成功后，系统刷新列表或跳转到详情页，并在必要时写入操作日志。最终输出包括{output}，能够支撑停车业务从查询到管理的闭环。"
    ]


def expand_meta():
    meta = load("meta.json")
    meta["abstract_zh"] = [
        "随着城市机动车保有量持续增长，商业区、交通枢纽、医院、学校和公共服务场所的停车供需矛盾逐渐突出。传统停车场主要依靠人工登记、现场找位、人工收费和事后汇总，容易出现空闲车位更新滞后、用户查找效率低、预约规则不清、订单状态难追踪、管理人员统计困难等问题。围绕停车资源在线查询、车位预约锁定、入场出场记录、订单计费支付和后台运营管理等需求，本文结合实际开发项目，设计并实现了一套城市智慧停车管理系统。",
        "系统采用前后端分离架构，前端基于 Vue3、Vite、Naive UI、Pinia、Vue Router、Axios 和 ECharts 构建用户端与管理员端页面，后端基于 Spring Boot、Spring Security、JWT、MyBatis-Plus、MySQL、AOP 和定时任务完成接口服务、权限控制、业务处理、数据持久化与预约超时处理。系统主要包括用户登录注册、停车场查询、车位状态展示、车辆管理、预约停车、订单支付、停车场管理、车位管理、订单管理、用户管理、操作日志、系统配置、数据统计和用户个人中心等模块。",
        "在实现过程中，系统通过停车订单状态流转保证预约、入场、出场和支付环节的业务一致性，通过车位状态控制避免重复预约，通过定时任务处理预约超时，通过操作日志记录后台关键行为，通过统计图表展示收入趋势、订单趋势、停车场利用率和订单状态分布。测试与运行结果表明，系统能够较好地完成智慧停车场景下的信息查询、预约办理、订单处理和后台管理工作，具有一定的实用价值和后续扩展空间。"
    ]
    meta["abstract_en"] = [
        "With the continuous growth of urban motor vehicles, the contradiction between parking supply and demand has become increasingly prominent in business districts, transportation hubs, hospitals, schools and public service areas. Traditional parking lots mainly rely on manual registration, on-site space searching, manual charging and post-event statistics, which often lead to delayed parking space updates, inefficient user searching, unclear reservation rules, difficult order tracking and weak operation statistics. Based on an actual development project, this thesis designs and implements an urban smart parking management system.",
        "The system adopts a front-end and back-end separated architecture. The front end is developed with Vue3, Vite, Naive UI, Pinia, Vue Router, Axios and ECharts, while the back end is implemented with Spring Boot, Spring Security, JWT, MyBatis-Plus, MySQL, AOP and scheduled tasks. The system provides user login and registration, parking lot query, parking space display, vehicle management, reservation, order payment, parking lot management, parking space management, order management, user management, operation logs, system configuration, data statistics and user profile management.",
        "During implementation, the system maintains business consistency through parking order state transitions, prevents repeated reservations through parking space status control, handles reservation timeout through scheduled tasks, records important administrative operations through logs, and visualizes revenue trends, order trends, parking lot utilization and order status distribution. The running results show that the system can effectively support information query, reservation processing, order handling and back-office management in smart parking scenarios."
    ]
    dump("meta.json", meta)


def expand_ch1():
    ch = load("ch1.json")
    ch["content"].extend([
        text("从实际项目角度看，停车系统既包含典型的信息管理系统特征，又具有较强的业务状态约束。普通的信息管理页面只需要完成增删改查，而停车预约场景还要处理车位占用、预约过期、车辆入场、车辆出场、费用计算和支付完成等状态变化。如果这些状态缺少统一约束，就会出现同一车位被重复预约、订单费用计算不一致、已完成订单仍占用车位等问题。"),
        text("因此，本文并不只是简单完成页面展示，而是围绕停车业务的完整链路进行分析。系统以停车订单为核心，将用户、车辆、停车场、车位、支付记录和操作日志串联起来，使用户端操作和管理端监管能够使用同一套业务数据。")
    ])
    extend_section(ch, "1.1 研究背景", [
        "在城市公共交通和私家车出行并存的背景下，停车问题具有明显的时段性和区域性。工作日早晚高峰、节假日商圈客流、医院就诊高峰都会导致停车需求集中释放，而停车场管理人员往往只能在现场根据经验判断车位余量，难以及时向用户提供准确的停车信息。",
        "同时，传统停车场缺少统一的数据沉淀。收费记录、入场记录、出场记录和车位状态如果分散在不同人员或设备中，后续统计收入、分析使用率、追踪异常订单都会比较困难。智慧停车系统通过数据库统一保存业务过程，可以把原本零散的信息转化为可查询、可统计、可分析的数据资源。",
        "本项目采用 Web 管理端和用户端相结合的方式，既能满足停车场运营人员对资源和订单的管理，也能满足普通用户在线查询与预约的需要。该模式适合中小型停车场、园区停车场、商圈停车场以及校园停车场等场景。"
    ])
    extend_section(ch, "1.2 研究目的", [
        "系统实现需要达到三个层面的目标。第一是业务完整性，要求从停车场查询、车辆绑定、车位预约、入场出场到支付完成形成闭环；第二是数据一致性，要求订单状态、车位状态和支付状态在关键操作后保持同步；第三是管理可视化，要求后台能够通过统计卡片和图表展示运营情况。",
        "为了实现上述目标，系统在后端服务层集中处理核心规则。例如预约前检查用户是否存在未完成订单，预约时检查车位是否空闲，入场时检查订单是否仍有效，出场时根据入场时间和收费标准计算金额，支付后释放车位并生成支付记录。这些规则能够提升系统的可靠性。",
        "在前端实现方面，系统希望通过相对清晰的页面结构降低用户操作成本。用户端以停车场列表、详情、订单、车辆和个人中心为主；管理端以统计首页、停车场管理、车位管理、订单管理、用户管理、日志管理和配置管理为主。"
    ])
    extend_section(ch, "1.3 研究意义", [
        "从工程实践角度看，本文能够体现 Spring Boot 与 Vue3 前后端分离项目的完整开发过程，包括数据库建模、接口设计、权限认证、状态管理、页面渲染、图表展示和运行测试等环节。通过该系统可以较系统地理解一个管理类 Web 项目的实现流程。",
        "从业务应用角度看，系统有助于提升停车资源使用效率。用户提前查询并预约车位，可以减少到达现场后反复寻找车位的时间；管理员通过后台维护车位状态和订单记录，可以更及时地掌握场内情况。对于停车资源紧张的区域，该系统具有一定的应用价值。",
        "从后续扩展角度看，系统保留了与地图定位、车牌识别、闸机设备和第三方支付平台对接的空间。当前项目完成了核心软件流程，后续可以在此基础上进一步接入硬件设备和真实支付渠道。"
    ])
    extend_section(ch, "1.4 论文组织结构", [
        "论文各章之间的逻辑关系如下：第一章提出课题背景和研究目标；第二章说明完成系统所需的开发技术；第三章从角色和业务流程出发分析系统需求；第四章将需求转化为数据库表结构；第五章对系统架构、功能模块、业务流程、权限流程和包结构进行设计；第六章结合实际运行页面说明主要功能实现；第七章总结本文工作并提出改进方向。",
        "这种组织方式与管理系统类毕业论文的常见写法基本一致，先说明为什么做，再说明用什么技术做，随后分析做什么、如何设计、如何实现，最后总结系统完成情况。"
    ])
    dump("ch1.json", ch)


def expand_ch2():
    ch = load("ch2.json")
    ch["content"].append(text("与购物商城模板类似，本章不单独讨论某一种技术，而是围绕系统实际用到的前端、后端、数据库、安全认证和可视化技术进行说明。各技术并不是简单堆叠，而是在系统中分别承担页面展示、业务处理、数据访问、身份认证和统计分析等职责。"))
    additions = {
        "2.1 Spring Boot 框架": [
            "在本系统中，Spring Boot 的作用不只是启动 Web 服务，还承担了统一接口规范的组织工作。项目中的 Result、ResultCode、BusinessException 和 GlobalExceptionHandler 共同构成统一返回与异常处理机制，使前端能够以相同方式处理成功、失败和未登录等响应。",
            "后端控制器按照业务对象拆分为认证控制器、公共停车场控制器、用户订单控制器、用户车辆控制器、后台停车场控制器、后台车位控制器和后台订单控制器等。这样的拆分方式与实际业务边界一致，便于后期维护和定位问题。"
        ],
        "2.2 Vue3 与 Vite": [
            "Vue3 的组合式 API 适合在页面中组织查询条件、表单状态、弹窗状态和表格加载状态。本系统后台页面大量使用列表查询和弹窗编辑，前端通过 ref、reactive、computed 和 onMounted 等能力完成数据响应和页面生命周期控制。",
            "Vite 在开发阶段能够快速启动本地服务，便于对停车场列表、车位管理和订单页面进行调试。与传统构建工具相比，Vite 的热更新速度较快，修改页面后能够及时看到效果，提高了前端开发效率。"
        ],
        "2.3 MySQL 数据库": [
            "系统数据库表围绕业务主线设计，用户表、车辆表、停车场表、车位表、订单表和支付记录表构成核心业务数据，日志表和配置表则服务于后台运维。各表均设置创建时间、更新时间或软删除字段，使数据具备一定的历史追踪能力。",
            "在索引设计上，系统针对常用查询字段设置索引。例如停车场按状态和名称查询，车位按停车场与状态查询，订单按用户与状态、停车场与状态、车牌号和创建时间查询。这些索引能够提升后台列表和用户订单查询效率。"
        ],
        "2.4 MyBatis-Plus 持久层框架": [
            "项目中的实体类与数据库表一一对应，通过注解或命名约定完成字段映射。服务层在处理查询时通常使用 LambdaQueryWrapper 拼接条件，这种方式比手写字符串 SQL 更不容易出现字段名拼写错误，也更符合 Java 项目的类型安全习惯。",
            "分页查询是后台管理系统中非常常见的需求。MyBatis-Plus 的 Page 对象可以封装页码、每页数量、总记录数和记录列表，前端表格再根据这些信息显示分页控件，从而形成完整的分页查询流程。"
        ],
        "2.5 Spring Security 与 JWT": [
            "在前后端分离系统中，服务端一般不再依赖传统 Session 保存登录状态，而是通过 Token 在每次请求中携带身份信息。本系统登录成功后返回 JWT，前端将其保存并在请求拦截器中自动加入 Authorization 请求头。",
            "后端的 JwtAuthenticationFilter 会解析 Token、读取用户身份并放入安全上下文。SecurityConfig 对不同接口进行权限划分，公共接口允许匿名访问，用户端接口要求登录用户，后台接口要求管理员角色，从而形成清晰的访问控制边界。"
        ],
        "2.6 Naive UI 与 ECharts": [
            "Naive UI 在后台表格、搜索表单、分页、弹窗、标签和按钮方面使用较多，能够减少手写基础组件的工作量。停车场管理、车位管理和订单管理页面的结构均采用搜索区、操作区、表格区和分页区的形式，符合后台管理系统的使用习惯。",
            "ECharts 主要用于后台首页的数据展示。与单纯表格相比，折线图、柱状图和饼图能够更直观地体现收入变化、订单变化和状态分布，管理人员可以快速判断近期停车场运营情况。"
        ],
        "2.7 高德地图定位服务": [
            "地图能力不是停车系统的核心数据库功能，但会直接影响用户查找停车场的体验。系统在停车场详情页面保留地图展示位置，使用户能够结合地址和地图判断停车场位置；在后台维护停车场信息时，经纬度字段也为后续地图选点和导航扩展提供基础。"
        ]
    }
    for title, paras in additions.items():
        extend_section(ch, title, paras)
    dump("ch2.json", ch)


def rebuild_ch3():
    ch = {
        "title": "3 智慧停车系统需求分析",
        "content": [
            text("需求分析是系统设计和实现的基础。根据停车场管理业务，本系统面向两类用户：普通用户和管理员。普通用户主要完成停车场查询、车位查看、预约停车、订单处理和车辆维护；管理员主要完成停车资源维护、订单监管、用户管理、日志查看、系统配置和运营统计。"),
            text("与一般后台管理系统相比，智慧停车系统的需求重点在于状态变化。停车场状态影响用户能否预约，车位状态影响订单能否创建，订单状态影响入场、出场和支付操作能否继续进行。因此需求分析需要把角色操作和状态约束结合起来。")
        ],
        "sections": [
            {
                "title": "3.1 后台管理端功能需求",
                "content": [
                    text("后台管理端面向停车场运营人员，要求能够对系统基础资源和业务数据进行维护。管理员登录后进入后台首页，可以查看统计卡片和可视化图表，再根据管理需要进入停车场管理、车位管理、订单管理、用户管理、操作日志和系统配置等功能模块。"),
                    text("后台管理端的设计目标是让管理人员能够在一个统一界面内完成资源维护、状态监管和运营统计。对于停车场这类实时性较强的业务，后台页面不仅要能录入数据，还要能根据业务状态限制操作，减少人工误操作造成的数据异常。"),
                    image("images/fig3-1-admin-usecase.png", "图3-1 管理员用例图", 10.8)
                ],
                "subsections": [
                    {"title": "3.1.1 登录认证与权限需求", "content": [text(p) for p in module_paras("登录认证与权限", "管理员", "管理员账号、密码、角色和登录状态", "登录校验、Token 生成、角色识别和后台路由访问控制", "只有管理员角色才能进入后台管理页面和调用后台接口", "登录结果、用户角色、访问控制结果和异常提示")]},
                    {"title": "3.1.2 停车场管理需求", "content": [text(p) for p in module_paras("停车场管理", "停车场运营人员", "停车场名称、地址、经纬度、收费标准、营业时间、联系电话和状态", "停车场新增、编辑、删除、查询、状态维护和图片信息维护", "已存在车位或订单的停车场不能被随意删除，关闭停车场后用户端不能继续预约", "停车场列表、详情数据和可预约状态")]},
                    {"title": "3.1.3 车位管理需求", "content": [text(p) for p in module_paras("车位管理", "停车场运营人员", "停车场下的车位编号、楼层区域、车位类型和车位状态", "单个新增、批量新增、状态调整、条件查询和维护标记", "同一停车场内车位编号不能重复，已预约或已占用车位不能直接删除", "车位状态列表、车位统计和可预约车位数据")]},
                    {"title": "3.1.4 订单管理需求", "content": [text(p) for p in module_paras("订单管理", "停车场运营人员", "订单编号、用户、车辆、停车场、车位、入场时间、出场时间、金额和状态", "订单查询、手动入场、手动出场、异常备注、取消处理和导出扩展", "订单必须按照预约、进行中、待支付、已完成或已取消的顺序流转", "订单列表、订单详情、计费结果和管理备注")]},
                    {"title": "3.1.5 用户与车辆管理需求", "content": [text(p) for p in module_paras("用户与车辆管理", "管理员", "注册账号、手机号、昵称、角色、状态以及用户绑定车辆", "用户查询、启用禁用、重置密码、查看车辆和审查异常账号", "管理员不能随意修改用户历史订单，禁用账号后该用户不能继续创建预约", "用户列表、账号状态、车辆信息和重置结果")]},
                    {"title": "3.1.6 日志、配置与统计需求", "content": [text(p) for p in module_paras("日志、配置与统计", "管理员", "操作日志、系统参数、收入数据、订单数据和停车场利用率", "记录关键操作、维护预约超时时长、展示收入趋势、订单趋势和状态分布", "配置修改应立即影响后续业务，日志记录应保留操作人、模块、类型和时间", "操作追踪结果、业务参数和统计图表")]}
                ]
            },
            {
                "title": "3.2 用户端功能需求",
                "content": [
                    text("用户端面向普通停车用户，重点是减少寻找车位的时间成本，并提供清晰的停车订单办理流程。用户可以在未登录状态下查看停车场列表和详情，登录后可以绑定车辆、选择空闲车位并创建预约订单。"),
                    text("用户端需求更强调体验和流程顺畅。用户在停车前需要快速知道附近或目标区域有哪些停车场、是否营业、还有多少空闲车位以及收费标准；停车中需要知道订单状态；停车后需要查看费用和历史记录。"),
                    image("images/fig3-2-user-usecase.png", "图3-2 用户端用例图", 10.8)
                ],
                "subsections": [
                    {"title": "3.2.1 用户注册登录需求", "content": [text(p) for p in module_paras("用户注册登录", "普通用户", "用户名、手机号、密码、昵称和登录状态", "账号注册、密码登录、Token 保存、退出登录和个人资料读取", "手机号与用户名不能重复，未登录用户不能创建预约和支付订单", "登录状态、用户信息和接口访问权限")]},
                    {"title": "3.2.2 停车场查询需求", "content": [text(p) for p in module_paras("停车场查询", "普通用户", "停车场名称、地址、营业状态、收费标准、剩余车位和地图位置", "关键字搜索、列表浏览、详情查看、地图展示和营业状态判断", "关闭状态的停车场只能查看不能预约，剩余车位为零时应提示用户", "停车场列表、详情信息和位置展示")]},
                    {"title": "3.2.3 车位预约需求", "content": [text(p) for p in module_paras("车位预约", "普通用户", "车位编号、车位类型、车辆信息、预约时间和过期时间", "选择车辆、选择空闲车位、提交预约、取消预约和预约超时释放", "同一用户不能同时存在多个未完成订单，非空闲车位不能创建预约", "预约订单、车位锁定结果和状态提示")]},
                    {"title": "3.2.4 订单支付需求", "content": [text(p) for p in module_paras("订单支付", "普通用户", "订单状态、入场时间、出场时间、停车时长、订单金额和支付记录", "查看订单、模拟入场、出场计费、确认支付和查看支付结果", "订单只有进入待支付状态后才能支付，支付成功后才能释放车位并完成订单", "订单详情、支付记录和历史订单")]},
                    {"title": "3.2.5 车辆与个人中心需求", "content": [text(p) for p in module_paras("车辆与个人中心", "普通用户", "车牌号、车辆类型、车辆颜色、车辆品牌和用户资料", "新增车辆、编辑车辆、删除车辆、设置默认车辆和修改个人资料", "车辆必须属于当前登录用户，默认车辆只能有一辆", "车辆列表、默认车辆标记和个人资料")]}
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
                        ["可追溯性", "关键管理行为需要留痕", "操作日志表记录模块、类型、内容、URL 和 IP"],
                        ["可扩展性", "后续能够接入车牌识别、闸机设备和真实支付平台", "预留车牌、订单、支付和地图相关字段"]
                    ]),
                    text("除功能需求外，系统还需要满足性能、可维护性和安全性的要求。后台列表查询应支持分页，避免一次性加载大量数据；用户端页面应保持清晰的操作流程，避免用户在停车场详情、车辆选择和订单支付之间迷失；后端接口应对关键参数进行校验，防止异常数据写入数据库。"),
                    text("对于停车预约这类存在并发可能的业务，系统还需要特别关注数据一致性。虽然本项目属于毕业设计规模，但仍在业务层强调车位状态校验和订单状态流转，避免同一车位被重复预约或已完成订单未释放车位的问题。")
                ]
            }
        ]
    }
    dump("ch3.json", ch)


def rebuild_ch4():
    old = load("ch4.json")
    ch = {
        "title": "4 数据库设计",
        "content": [
            text("数据库设计需要将需求分析中的业务对象转换为关系型数据表。城市智慧停车系统的核心业务围绕用户、车辆、停车场、车位、停车订单和支付记录展开，同时为了支持后台管理，还需要操作日志表和系统配置表。"),
            text("本章按照模板中数据库设计章节的写法，先说明数据库环境和总体模型，再分别介绍主要业务表。每张表前均给出文字说明，使表结构与业务作用对应起来，避免只罗列字段而缺少解释。"),
            image("images/fig4-1-er.png", "图4-1 系统数据库逻辑结构图", 11.8)
        ],
        "sections": [
            {
                "title": "4.1 数据库环境与连接配置",
                "content": [
                    text("系统数据库名称为 smart_parking，字符集采用 utf8mb4，以支持中文停车场名称、地址、用户名、日志内容和配置说明等信息。各表均使用自增 id 作为主键，业务删除场景采用 deleted 字段进行软删除，避免直接物理删除造成历史订单和统计数据丢失。"),
                    text("后端通过 Spring Boot 配置数据源连接 MySQL，并使用 MyBatis-Plus 完成实体映射和条件查询。数据库初始化脚本位于后端项目 sql/init.sql 中，包含建库、建表、默认管理员、测试用户、系统配置和演示停车场数据。"),
                    text("在字段命名上，数据库采用下划线命名方式，Java 实体类采用驼峰命名方式，由 MyBatis-Plus 完成映射。时间字段主要包括 create_time、update_time、reserve_time、enter_time、exit_time 和 pay_time，用于记录业务发生时间。")
                ]
            },
            {
                "title": "4.2 数据库逻辑模型设计",
                "content": [
                    text("用户与车辆之间是一对多关系，一个用户可以绑定多辆车；停车场与车位之间是一对多关系，一个停车场包含多个车位；订单表关联用户、车辆、停车场和车位，是系统业务流转的核心表；支付记录表与订单表关联，用于记录支付金额、支付方式和交易流水。"),
                    text("从业务依赖看，停车订单表处于模型中心位置。订单创建时需要读取用户、车辆、停车场和车位数据；订单入场和出场时需要同步更新车位状态；订单支付完成后需要生成支付记录。因此数据库设计需要保证这些表之间具备清晰的关联字段。")
                ],
                "subsections": [
                    {"title": "4.2.1 用户与车辆业务表", "content": [
                        text("用户表用于保存系统登录账号和基础身份信息，包括用户名、手机号、昵称、角色、状态等字段。系统通过 role 字段区分普通用户和管理员，通过 status 字段控制账号是否可用。"),
                        table_from(old, "表4-1"),
                        text("车辆表用于保存用户绑定的车牌和车辆属性。预约停车时，订单需要关联具体车辆，因此车辆表通过 user_id 与用户表建立关联，并通过 plate_number 保存车牌号。"),
                        table_from(old, "表4-2")
                    ]},
                    {"title": "4.2.2 停车场与车位业务表", "content": [
                        text("停车场表用于保存停车场基础资料，是用户查询与管理员维护的核心基础表。该表保存地址、经纬度、收费标准、营业时间、剩余车位数和状态等信息。"),
                        table_from(old, "表4-3"),
                        text("车位表用于描述停车场内的具体停车位。系统通过 lot_id 将车位归属到停车场，通过 status 字段标记车位是否空闲、占用、预约或维护。"),
                        table_from(old, "表4-4")
                    ]},
                    {"title": "4.2.3 订单与支付业务表", "content": [
                        text("停车订单表是业务流转的核心表，保存用户预约、入场、出场、计费、取消和支付状态等信息。订单表冗余保存 lot_name、space_code 和 plate_number，便于历史订单展示。"),
                        table_from(old, "表4-5"),
                        text("支付记录表用于保存订单支付结果。一个订单支付成功后生成一条支付记录，记录支付金额、支付方式、交易号和支付时间，为后续对账和统计提供依据。"),
                        table_from(old, "表4-6")
                    ]},
                    {"title": "4.2.4 运维管理业务表", "content": [
                        text("操作日志表用于记录管理员和系统关键操作，包括操作人、操作类型、模块、摘要、请求方法、请求地址和 IP 地址。该表可以帮助管理员追踪异常操作和定位问题。"),
                        table_from(old, "表4-7"),
                        text("系统配置表用于保存业务参数，避免将可变配置写死在程序中。例如预约锁定时长、默认收费标准、每个用户最大车辆数和系统公告均可通过配置表维护。"),
                        table_from(old, "表4-8")
                    ]}
                ]
            },
            {
                "title": "4.3 数据库约束与索引设计",
                "content": [
                    text("数据库约束主要用于保证基础数据不重复和业务数据可追踪。用户表对 username 和 phone 设置唯一约束，车辆表对 user_id 与 plate_number 设置联合唯一约束，停车位表对 lot_id 与 space_code 设置联合唯一约束，订单表对 order_no 设置唯一约束，支付记录表对 order_id 与 trade_no 设置唯一约束。"),
                    text("索引设计围绕系统常用查询场景展开。停车场列表常按状态和名称查询，车位列表常按停车场和状态查询，订单列表常按用户、停车场、状态、车牌号和创建时间查询。通过这些索引，可以提高用户端订单列表、后台订单筛选和统计查询的效率。"),
                    table("表4-9 主要索引设计说明", ["数据表", "索引字段", "作用说明"], [
                        ["sys_user", "username, phone, role, status", "支持登录查询、手机号唯一校验和账号筛选"],
                        ["user_vehicle", "user_id, plate_number", "支持用户车辆列表和车牌重复校验"],
                        ["parking_lot", "status, longitude, latitude, name", "支持营业状态筛选、地图位置和名称检索"],
                        ["parking_space", "lot_id, status, space_code", "支持按停车场查看车位和判断空闲车位"],
                        ["parking_order", "user_id, lot_id, status, plate_number, create_time", "支持订单列表、状态筛选和历史查询"],
                        ["operation_log", "operator, operate_type, create_time", "支持操作日志追踪与时间筛选"]
                    ])
                ]
            }
        ]
    }
    dump("ch4.json", ch)


def rebuild_ch5():
    ch = {
        "title": "5 智慧停车系统设计",
        "content": [
            text("系统设计需要在需求分析和数据库设计基础上确定整体架构、模块划分、业务流程和代码组织方式。城市智慧停车系统采用前后端分离架构，前端通过浏览器访问页面，后端通过 REST API 提供数据服务，数据库负责持久化业务数据。"),
            text("本章按照模板中系统设计章节的组织方式，分别从总体架构、功能模块、业务流程、登录认证和包结构等方面展开，使后续实现章节能够与设计内容一一对应。")
        ],
        "sections": [
            {
                "title": "5.1 系统总体架构设计",
                "content": [
                    text("系统总体架构分为表现层、前端层、接口层、安全层、业务层、持久层和数据层。表现层包括用户端浏览器、管理员浏览器和移动端浏览器；前端层负责页面渲染、路由、状态管理和图表展示；后端层负责接口、认证、业务处理和数据访问；数据层通过 MySQL 保存核心业务数据。"),
                    image("images/fig5-1-architecture.png", "图5-1 系统总体架构图", 9.6),
                    text("前端与后端之间通过 HTTP 接口交互。前端页面不直接访问数据库，而是调用后端控制器提供的接口；后端在服务层完成业务规则校验，再由 Mapper 访问数据库。该结构能够使页面展示和业务规则相互独立，便于后续维护。"),
                    text("系统安全边界位于后端接口层。即使前端隐藏了后台菜单，后端仍然需要通过 Spring Security 对请求进行认证和角色判断，防止普通用户绕过页面直接调用后台接口。")
                ]
            },
            {
                "title": "5.2 系统功能模块设计",
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
                ],
                "subsections": [
                    {"title": "5.2.1 用户端停车服务设计", "content": [text("用户端停车服务由停车场列表、停车场详情、车辆管理、订单管理和个人中心组成。停车场列表负责帮助用户快速找到可用停车场，详情页负责展示地址、收费标准、车位状态和地图位置，车辆管理为预约停车提供车牌数据，订单管理则展示预约、入场、出场、支付和历史记录。"), text("用户端模块之间的跳转应围绕停车流程组织。用户先进入停车场列表，再进入详情页选择车位，随后选择车辆并创建订单；订单创建后进入我的订单页面，用户可以根据状态继续入场、出场、支付或取消。")]},
                    {"title": "5.2.2 后台资源管理设计", "content": [text("后台资源管理主要包括停车场管理和车位管理。停车场管理维护停车场的基础属性，车位管理维护停车场内部的车位资源。两者之间存在主从关系，停车场是车位的上级对象，车位的 lot_id 字段指向停车场。"), text("为了提高维护效率，车位管理模块支持批量新增。管理员选择停车场、楼层区域、车位类型、前缀和数量后，系统可以一次生成多个车位编号，减少重复录入工作。")]},
                    {"title": "5.2.3 订单与支付模块设计", "content": [text("订单模块以 parking_order 表为核心，负责记录从预约到支付完成的全过程。支付模块以 payment_record 表为核心，负责保存支付金额、支付方式、交易号和支付时间。两者之间通过 order_id 和 order_no 建立关联。"), text("订单状态设计需要兼顾用户操作和管理操作。用户可以主动取消预约、模拟入场、出场计费和支付；管理员可以在后台查看订单，并在需要时进行手动入场、手动出场和备注处理。")]},
                    {"title": "5.2.4 统计分析与日志模块设计", "content": [text("统计分析模块从订单、停车场和车位数据中汇总运营指标，包括今日收入、今日订单、在场车辆、用户数量、收入趋势、订单趋势、订单状态分布和停车场利用率等。该模块主要服务于管理员决策。"), text("日志模块通过 AOP 切面对后台关键操作进行记录。相比在每个业务方法中手动写日志，AOP 方式能够减少重复代码，并保证新增、修改、删除、登录等操作具有统一日志格式。")]},
                    {"title": "5.2.5 系统配置模块设计", "content": [text("系统配置模块用于维护可变业务参数，例如预约超时时长、默认小时费率、每个用户最大车辆数和系统公告。将这些参数保存在数据库中，可以避免每次修改业务参数都重新打包部署项目。"), text("配置读取时需要考虑默认值。当数据库中不存在某个配置项或配置值异常时，系统应使用程序中的默认值，避免关键业务因为配置错误而无法继续运行。")]}
                ]
            },
            {
                "title": "5.3 预约停车业务流程设计",
                "content": [
                    text("预约停车流程是系统的核心业务流程。用户从停车场列表进入详情页，选择空闲车位和已绑定车辆后提交预约。后端需要校验用户是否存在未完成订单、车辆是否属于当前用户、停车场是否营业、车位是否处于空闲状态。校验通过后，系统锁定车位并生成订单。"),
                    image("images/fig5-2-order-flow.png", "图5-2 预约停车与计费业务流程图", 7.8),
                    text("当用户到达停车场后，系统将订单状态由已预约更新为进行中，并将车位状态更新为已占用。用户离场时，系统根据入场时间、出场时间和收费标准计算金额，订单进入待支付状态。支付成功后生成支付记录，订单状态更新为已完成，并释放车位。"),
                    text("预约流程中最重要的设计点是状态一致。订单和车位虽然存储在不同表中，但它们表达的是同一停车行为的不同侧面。如果订单已取消，车位应该恢复空闲；如果订单已入场，车位应该处于占用状态；如果订单支付完成，车位也应该释放。")
                ]
            },
            {
                "title": "5.4 登录认证与权限设计",
                "content": [
                    text("系统采用 JWT 方式实现无状态认证。用户或管理员登录成功后，后端返回 token 和 userInfo，前端将 token 保存到本地并在后续请求中放入 Authorization 请求头。后端过滤器解析 token，校验签名和过期时间，并将用户身份写入安全上下文。"),
                    image("images/fig5-3-auth-flow.png", "图5-3 登录认证与权限校验流程图", 11.2),
                    text("权限控制按角色进行划分。普通用户只能访问用户端接口，管理员可以访问后台接口。当前端路由进入需要认证的页面时，会先检查本地登录状态；后端接口则通过 Spring Security 进行最终校验，避免只依赖前端判断导致越权访问。")
                ],
                "subsections": [
                    {"title": "5.4.1 前端路由守卫设计", "content": [text("前端路由守卫负责在页面跳转前判断登录状态。未登录用户访问需要认证的用户端页面时，系统跳转到用户登录页；普通用户访问后台管理页面时，系统阻止访问；管理员访问后台页面时允许进入对应模块。"), text("路由守卫属于用户体验层面的保护，能够减少误操作，但不能替代后端权限校验。真正的数据安全仍然由后端接口负责。")]},
                    {"title": "5.4.2 后端接口权限设计", "content": [text("后端接口按照 public、user 和 admin 三类路径进行权限划分。public 接口允许匿名访问，用于停车场公开查询和登录注册；user 接口要求普通用户或管理员登录；admin 接口要求管理员角色。"), text("这种路径划分方式比较清晰，便于在 SecurityConfig 中统一配置，也便于前端 API 文件按照业务角色进行组织。")]}
                ]
            },
            {
                "title": "5.5 后端包结构设计",
                "content": [
                    text("后端代码以 com.smartparking 为根包，按照业务职责进行分包。controller 包负责接口入口，service 包定义业务服务，service.impl 包提供具体实现，mapper 包负责数据库访问，entity 包映射数据表，dto 和 vo 分别承载请求数据和响应数据。security、config、common、aspect 和 task 等包提供安全、配置、通用返回、日志切面和定时任务能力。"),
                    image("images/fig5-4-package.png", "图5-4 后端包结构图", 9.2),
                    text("DTO 和 VO 的分离能够减少实体类直接暴露给前端的问题。DTO 主要用于接收前端请求，例如 LoginDTO、RegisterDTO、ReserveDTO、ParkingLotDTO 和 VehicleDTO；VO 主要用于返回前端展示，例如 OrderVO、ParkingLotVO、ParkingSpaceVO 和 DashboardSummaryVO。"),
                    text("common 包中的 Result、ResultCode 和 BusinessException 形成统一接口返回规范。controller 层不直接拼接复杂响应，而是通过统一封装返回数据，前端可以根据 code、message 和 data 处理接口结果。")
                ]
            }
        ]
    }
    dump("ch5.json", ch)


def rebuild_ch6():
    ch = load("ch6.json")
    ch["content"].append(text("为了使实现章节更接近模板的写法，本章不仅展示运行页面，还对每个页面背后的接口、数据流和业务规则进行说明。页面截图用于证明系统能够运行，文字说明用于解释系统如何完成相关功能。"))
    for sec in ch.get("sections", []):
        if sec["title"] == "6.1 开发环境与项目结构":
            sec["content"].extend([
                text("后端项目启动类为 SmartParkingApplication，配置文件位于 application.yml。数据库初始化脚本包含 smart_parking 数据库、8 张主要业务表、默认管理员、测试用户和演示停车场数据。项目使用 Maven 管理依赖，主要依赖包括 Spring Boot Web、Spring Security、Validation、MyBatis-Plus、JWT、Knife4j、Lombok、Hutool 和 EasyExcel。"),
                text("前端项目通过 Vite 启动，src 目录下按 api、layout、router、store、utils 和 views 进行划分。api 目录封装不同业务的请求方法，views 目录保存实际页面，layout 目录保存用户端和管理员端整体布局，store 目录保存认证状态。"),
                table("表6-2 前后端主要目录说明", ["项目", "目录或包", "作用"], [
                    ["后端", "controller", "提供认证、停车场、车位、订单、用户、日志、配置等 REST 接口"],
                    ["后端", "service / service.impl", "封装业务规则、状态流转和事务处理"],
                    ["后端", "mapper / entity", "完成数据库表映射和数据访问"],
                    ["后端", "security", "实现 JWT 解析、登录用户封装和权限配置"],
                    ["后端", "aspect / task", "实现操作日志切面和预约超时定时任务"],
                    ["前端", "views", "保存用户端和管理员端页面"],
                    ["前端", "api", "封装 Axios 请求方法"],
                    ["前端", "router / store", "完成路由管理和登录状态管理"]
                ])
            ])
        elif sec["title"] == "6.2 登录认证功能实现":
            sec["content"].extend([
                text("注册功能由用户端注册页面调用后端公开接口完成。用户提交用户名、手机号和密码后，后端首先校验用户名和手机号是否重复，再对密码进行 BCrypt 加密，最后保存普通用户账号。相比直接保存明文密码，加密存储能够降低数据库泄露时的安全风险。"),
                text("登录成功后，前端会将 Token 和用户信息写入 Pinia 状态，并同步保存到本地存储。请求工具 request.js 在发送请求前读取 Token 并加入请求头，当后端返回未登录或 Token 失效时，前端清理登录状态并跳转登录页。"),
                code("代码6-3 请求拦截器携带 Token 示例", "service.interceptors.request.use(config => {\n    const token = getToken()\n    if (token) {\n        config.headers.Authorization = `Bearer ${token}`\n    }\n    return config\n})")
            ])
        elif sec["title"] == "6.3 后台统计模块实现":
            sec["content"].extend([
                text("后台统计模块的数据来自 AdminDashboardController。后端分别统计今日收入、今日订单、在场车辆、用户数量、收入趋势、订单趋势、订单状态分布和停车场利用率，再由前端使用 ECharts 绘制图表。"),
                text("统计模块的实现意义在于把零散订单数据转化为运营指标。管理员不需要逐条查看订单，也可以通过趋势图判断近期收入变化，通过状态分布判断待支付或取消订单是否异常，通过停车场利用率判断哪些停车场更繁忙。")
            ])
        elif sec["title"] == "6.4 停车场管理模块实现":
            sec["content"].extend([
                text("停车场新增和编辑页面需要校验名称、地址、收费标准、总车位数和营业状态等字段。由于停车场还涉及经纬度与地图展示，因此系统在字段设计上保留 longitude 和 latitude，为后续地图选点和导航能力提供基础。"),
                text("删除停车场时需要考虑关联数据。如果停车场已经存在车位或历史订单，直接物理删除会影响订单展示和统计结果，因此系统采用软删除思路，并在业务上限制对重要数据的随意删除。")
            ])
        elif sec["title"] == "6.5 车位管理模块实现":
            sec["content"].extend([
                text("车位管理模块需要频繁处理状态字段。空闲车位可以被用户预约；已预约车位等待用户入场；已占用车位表示车辆正在停车；维护中车位不能被预约。前端通过不同标签显示状态，后端通过状态字段控制业务操作。"),
                text("批量新增车位功能能够提高初始化效率。管理员只需要输入停车场、区域、类型、编号前缀和数量，系统即可生成一组连续编号的车位，适合停车场第一次录入数据或新增区域时使用。")
            ])
        elif sec["title"] == "6.6 订单管理模块实现":
            sec["content"].extend([
                text("订单管理是系统实现中最复杂的模块。预约订单创建时，系统需要锁定车位；订单取消时，需要释放车位；订单入场时，需要将车位改为已占用；订单出场时，需要计算费用；订单支付完成后，需要生成支付记录并释放车位。"),
                text("为了防止业务状态混乱，系统将订单状态流转集中放在服务层处理。控制器只负责接收请求和返回结果，不直接修改多个表。服务层在同一业务方法中同时更新订单、车位和支付记录，使状态变化更加集中。"),
                table("表6-3 订单状态流转说明", ["状态", "含义", "允许操作"], [
                    ["已预约", "用户已提交预约，车位被锁定", "取消预约、入场"],
                    ["进行中", "车辆已经入场，正在停车", "出场计费"],
                    ["待支付", "车辆已出场，订单金额已计算", "支付"],
                    ["已完成", "支付成功，订单结束", "查看详情"],
                    ["已取消", "用户取消或预约超时", "查看详情"]
                ])
            ])
        elif sec["title"] == "6.7 用户管理、日志与系统配置实现":
            sec["content"].extend([
                text("用户管理模块与系统安全直接相关。管理员可以禁用异常账号或重置用户密码，但不能直接查看用户明文密码。重置密码后，系统仍然使用 BCrypt 加密方式保存，保证密码字段不会以明文形式出现在数据库中。"),
                text("操作日志由自定义注解和 AOP 切面完成。后台新增、修改、删除、登录等操作执行时，切面自动记录操作人、操作类型、模块、请求地址和时间。该设计减少了业务代码中重复写日志的工作量，也方便后续审计。"),
                text("系统配置模块将预约超时时长、默认收费标准和车辆绑定数量限制保存在数据库中。后端服务读取配置后应用到预约、计费和车辆管理逻辑中，使系统具备一定的参数化能力。")
            ])
        elif sec["title"] == "6.8 用户端停车服务实现":
            sec["content"].extend([
                text("用户端停车场列表页面以卡片形式展示停车场信息，用户可以根据停车场名称或地址搜索。每个停车场卡片显示营业状态、剩余车位、收费标准和地址，使用户在列表层面就能做出初步判断。"),
                text("停车场详情页面展示地图、基本信息和车位状态。用户选择车位时，系统只允许选择空闲车位，并要求用户选择已绑定车辆。预约成功后，用户可以在订单页面查看订单状态。"),
                text("用户订单页面按照状态展示停车过程。用户可以对已预约订单执行入场或取消，对进行中订单执行出场，对待支付订单执行支付。车辆管理页面为预约流程提供车辆基础数据，个人中心页面用于展示账号资料。")
            ])
        elif sec["title"] == "6.9 核心业务实现说明":
            sec["content"].extend([
                text("预约超时任务由 ReserveTimeoutTask 完成。系统定期查询已超过 expire_time 且仍处于已预约状态的订单，将其更新为已取消，并将对应车位恢复为空闲。该功能可以避免用户预约后长期不入场导致车位被无效占用。"),
                text("支付功能由 UserPaymentController 和 PaymentRecordService 共同完成。由于毕业设计环境中没有接入真实支付平台，系统采用模拟支付方式完成业务闭环，但数据库仍然保存 trade_no、pay_time 和 pay_method 等字段，为后续对接真实支付平台保留扩展空间。"),
                code("代码6-4 预约超时处理逻辑示例", "List<ParkingOrder> expiredOrders = orderMapper.selectExpiredReservedOrders(now)\nfor (ParkingOrder order : expiredOrders) {\n    order.setStatus(OrderStatus.CANCELLED)\n    order.setCancelReason(\"预约超时自动取消\")\n    orderMapper.updateById(order)\n    spaceService.release(order.getSpaceId())\n}")
            ])
    dump("ch6.json", ch)


def expand_ch7():
    ch = load("ch7.json")
    ch["content"].extend([
        text("在论文撰写过程中，本文首先分析了城市停车管理的实际问题，然后结合项目已有前后端代码和数据库脚本，对系统角色、业务模块、数据表、核心流程和运行页面进行了整理。系统实现部分不仅给出页面截图，也补充了登录认证、订单状态流转、预约超时和支付记录等关键业务逻辑。"),
        text("从完成情况来看，系统已经能够覆盖毕业设计中停车管理系统的主要功能要求。用户端能够完成停车场查询、车位预约、车辆管理和订单处理，后台端能够完成资源管理、订单监管、用户管理、日志查询、配置维护和统计分析。整体结构较清晰，具备继续扩展为真实停车场应用的基础。"),
        text("当然，系统仍然存在不足。例如当前支付为模拟支付，尚未接入微信或支付宝真实回调；地图能力主要用于展示，尚未结合距离排序和路线规划；车牌识别、闸机控制和硬件传感器尚未接入；并发预约场景下还可以进一步引入数据库锁或消息队列增强可靠性。后续研究可以围绕这些方向继续完善。")
    ])
    dump("ch7.json", ch)


if __name__ == "__main__":
    expand_meta()
    expand_ch1()
    expand_ch2()
    rebuild_ch3()
    rebuild_ch4()
    rebuild_ch5()
    rebuild_ch6()
    expand_ch7()
    print("已按购物商城模板密度扩写 smart-parking JSON")
