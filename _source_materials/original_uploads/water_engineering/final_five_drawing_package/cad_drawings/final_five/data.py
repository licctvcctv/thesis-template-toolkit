PROJECT_NAME = "汕尾电厂配套煤码头工程初步设计"
DESIGN_STAGE = "本科毕业设计-初步设计"
DESIGNER = "港口航道与海岸工程"
ADVISOR = "孙克俐"

SHIP = {
    "dwt": "5万DWT",
    "length_m": 225.0,
    "beam_m": 32.5,
    "draft_m": 11.5,
}

HYDRO = {
    "design_high_m": 1.91,
    "design_low_m": 0.22,
    "extreme_high_m": 3.56,
    "extreme_low_m": -0.35,
    "front_depth_m": -12.50,
}

GENERAL = {
    "berth_length_m": 260.0,
    "structural_length_m": 250.0,
    "deck_elevation_m": 3.60,
    "turning_diameter_m": 270.0,
    "channel_width_m": 98.0,
    "berthing_water_width_m": 40.0,
    "stockyard_length_m": 250.0,
    "stockyard_width_m": 100.0,
    "stockyard_capacity_t": "15万t",
    "annual_working_days": 321,
    "daily_working_hours": 21,
}

HIGH_PILE = {
    "scheme_name": "高桩梁板式码头结构方案",
    "bent_count": 32,
    "bent_spacing_m": 8.0,
    "deck_width_m": 18.0,
    "pile_rows_m": [2.0, 10.0, 18.0],
    "front_mid_pile": "PHC800",
    "rear_pile": "PHC600",
    "beam_size": "横梁1.2m x 1.8m",
    "track_gauge_m": 10.5,
    "fender": "DA-A800H x 1500",
}

CAISSON = {
    "scheme_name": "重力式沉箱码头结构方案",
    "unit_count": 13,
    "unit_length_m": 20.0,
    "unit_width_m": 12.0,
    "unit_height_m": 14.0,
    "chamber_cols": 4,
    "chamber_rows": 2,
    "rubble_replacement_m": 4.0,
    "rubble_bed_m": 2.0,
    "wall_thickness_m": 0.45,
    "breast_wall_h_m": 2.0,
    "breast_wall_w_m": 2.5,
}

SOIL_LAYERS = [
    ("① 灰色淤泥~淤泥质土", 3.5, "承载力约60kPa，软弱层"),
    ("② 灰黄色粘土", 2.5, "软可塑~硬可塑"),
    ("③ 灰色~深灰色淤泥质土", 4.0, "压缩性大"),
    ("④ 粘土~粉质粘土", 5.0, "承载力约150kPa"),
    ("⑤ 粗砾砂", 7.0, "中密~密实，桩端过渡层"),
    ("⑧ 强风化花岗岩", 8.0, "承载力约600kPa，桩端持力层"),
]

NORM_NOTES = {
    "general": "泊位、水域、航道和回旋水域尺度按《海港总体设计规范》JTS 165-2025，并结合任务书设计船型和水位取值。",
    "structure": "码头结构布置、稳定和构造按《码头结构设计规范》JTS 167-2018，并结合地基条件进行方案比选。",
    "pile": "高桩方案按桩基承载、排架布置、上部梁板体系和耐久性要求进行表达。",
    "caisson": "重力式方案按软土地基换填加固后进行沉箱抗滑、抗倾、基床承载和构造表达。",
}
