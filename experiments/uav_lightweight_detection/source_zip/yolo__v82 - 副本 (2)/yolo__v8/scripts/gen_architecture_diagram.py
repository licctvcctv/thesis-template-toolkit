"""Generate YOLOv8s-Ghost-CBAM-WiseIoU architecture diagram in drawio format.

Output: results/architecture_diagram.drawio
Usage:  python scripts/gen_architecture_diagram.py
"""

from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "results" / "architecture_diagram.drawio"

S = {
    "conv":     "rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=10;arcSize=12;",
    "ghost":    "rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=10;fontStyle=1;arcSize=12;",
    "cbam":     "rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=10;fontStyle=1;arcSize=12;",
    "sppf":     "rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=10;arcSize=12;",
    "detect":   "rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=10;fontStyle=1;arcSize=12;",
    "concat":   "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#666666;fontSize=9;arcSize=12;",
    "ups":      "rounded=1;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#999999;fontSize=9;arcSize=12;",
    "input":    "rounded=1;whiteSpace=wrap;html=1;fillColor=#e6e6e6;strokeColor=#333333;fontSize=10;arcSize=12;",
    "c2f":      "rounded=1;whiteSpace=wrap;html=1;fillColor=#C8E6C9;strokeColor=#388E3C;fontSize=10;arcSize=12;",
    "wiou":     "rounded=1;whiteSpace=wrap;html=1;fillColor=#fce4d6;strokeColor=#c0392b;fontSize=10;fontStyle=1;arcSize=12;",
    "bn":       "rounded=1;whiteSpace=wrap;html=1;fillColor=#E0E0E0;strokeColor=#757575;fontSize=8;arcSize=8;",
    "act":      "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFCCBC;strokeColor=#BF360C;fontSize=8;arcSize=8;",
    "pool":     "rounded=1;whiteSpace=wrap;html=1;fillColor=#B3E5FC;strokeColor=#0277BD;fontSize=8;arcSize=8;",
    "split":    "rounded=1;whiteSpace=wrap;html=1;fillColor=#F3E5F5;strokeColor=#7B1FA2;fontSize=8;arcSize=8;",
    "ca":       "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFF9C4;strokeColor=#F9A825;fontSize=8;fontStyle=1;arcSize=8;",
    "sa":       "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFECB3;strokeColor=#FF8F00;fontSize=8;fontStyle=1;arcSize=8;",
    "reg_bb":   "rounded=1;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#C62828;dashed=1;dashPattern=8 4;strokeWidth=2;fontSize=13;fontStyle=1;verticalAlign=top;fontColor=#C62828;",
    "reg_neck": "rounded=1;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#2E7D32;dashed=1;dashPattern=8 4;strokeWidth=2;fontSize=13;fontStyle=1;verticalAlign=top;fontColor=#2E7D32;",
    "reg_head": "rounded=1;whiteSpace=wrap;html=1;fillColor=none;strokeColor=#E65100;dashed=1;dashPattern=8 4;strokeWidth=2;fontSize=13;fontStyle=1;verticalAlign=top;fontColor=#E65100;",
    "reg_mod":  "rounded=1;whiteSpace=wrap;html=1;fillColor=#FAFAFA;strokeColor=#BDBDBD;dashed=1;dashPattern=5 3;strokeWidth=1.5;fontSize=11;fontStyle=1;verticalAlign=top;fontColor=#424242;",
    "label":    "text;html=1;align=center;verticalAlign=middle;resizable=0;points=[];autosize=1;strokeColor=none;fillColor=none;fontSize=9;fontColor=#666666;fontStyle=2;",
    "tag":      "rounded=1;whiteSpace=wrap;html=1;fillColor=#FFCDD2;strokeColor=#C62828;fontSize=8;fontStyle=1;fontColor=#C62828;arcSize=20;",
    "edge":     "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#333333;",
    "edge_skip":"edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.5;strokeColor=#C62828;dashed=1;dashPattern=6 3;",
    "edge_thin":"edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1;strokeColor=#666666;",
    "edge_res": "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeWidth=1.2;strokeColor=#1565C0;dashed=1;dashPattern=4 2;",
}

_id = [2]


def nid():
    _id[0] += 1
    return _id[0] - 1


def node(value, x, y, w, h, style):
    i = nid()
    return i, (
        f'<mxCell id="{i}" value="{value}" style="{style}" '
        f'vertex="1" parent="1">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
        f'</mxCell>'
    )


def edge(src, tgt, style=S["edge"], label="", pts=None):
    i = nid()
    pts_xml = ""
    if pts:
        pts_xml = '<Array as="points">' + ''.join(
            f'<mxPoint x="{px}" y="{py}"/>' for px, py in pts
        ) + '</Array>'
    lbl = f'value="{label}"' if label else 'value=""'
    return (
        f'<mxCell id="{i}" {lbl} style="{style}" '
        f'edge="1" source="{src}" target="{tgt}" parent="1">'
        f'<mxGeometry relative="1" as="geometry">{pts_xml}</mxGeometry>'
        f'</mxCell>'
    )


def build():
    cells = []
    N = {}

    def add(name, value, x, y, w, h, style):
        i, xml = node(value, x, y, w, h, style)
        N[name] = i
        cells.append(xml)
        return i

    def con(src_name, tgt_name, style=S["edge"], label="", pts=None):
        cells.append(edge(N[src_name], N[tgt_name], style, label, pts))

    # ── REGION BOXES ──────────────────────────────────────────────
    add("reg_bb",   "Backbone",          18,  12, 200, 440, S["reg_bb"])
    add("reg_neck", "Neck（FPN + PAN）", 248, 12, 360, 440, S["reg_neck"])
    add("reg_head", "Head",              638, 12, 150, 440, S["reg_head"])

    # ── BACKBONE (compact vertical stack) ─────────────────────────
    bx = 55                 # block x
    bw, bwn = 130, 110      # wide / narrow width
    bh, bhn = 28, 25        # tall / short height
    gap = 4                 # vertical gap

    y = 30
    def bb(name, val, w, h, st):
        nonlocal y
        xc = bx + (bw - w) // 2
        add(name, val, xc, y, w, h, st)
        y += h + gap

    bb("input",   "Input&lt;br&gt;640×640×3", bw, 34, S["input"])
    bb("b_cv1",   "Conv 3→32 s2",     bwn, bhn, S["conv"])
    bb("b_cv2",   "Conv 32→64 s2",    bwn, bhn, S["conv"])
    bb("b_g1",    "C2f_Ghost 64",     bw,  bh,  S["ghost"])
    bb("b_cv3",   "Conv 64→128 s2",   bwn, bhn, S["conv"])
    bb("b_g2",    "C2f_Ghost 128",    bw,  bh,  S["ghost"])   # P3 skip
    y_p3 = y - bh - gap  # remember P3 y
    bb("b_cv4",   "Conv 128→256 s2",  bwn, bhn, S["conv"])
    bb("b_g3",    "C2f_Ghost 256",    bw,  bh,  S["ghost"])   # P4 skip
    y_p4 = y - bh - gap
    bb("b_cv5",   "Conv 256→512 s2",  bwn, bhn, S["conv"])
    bb("b_g4",    "C2f_Ghost 512",    bw,  bh,  S["ghost"])
    bb("b_sppf",  "SPPF 512",         bwn, bhn, S["sppf"])
    bb("b_cbam",  "CBAM ⭐ 512",      bw,  30,  S["cbam"])
    y_cbam = y - 30 - gap

    # Backbone vertical chain
    seq = ["input","b_cv1","b_cv2","b_g1","b_cv3","b_g2",
           "b_cv4","b_g3","b_cv5","b_g4","b_sppf","b_cbam"]
    for a, b in zip(seq, seq[1:]):
        con(a, b)

    # P-level labels
    add("lp3", "P3/8",  188, y_p3+2,  35, 16, S["label"])
    add("lp4", "P4/16", 188, y_p4+2,  35, 16, S["label"])
    add("lp5", "P5/32", 188, y_cbam+4,35, 16, S["label"])

    # Innovation tags
    add("tag1", "创新1: Ghost轻量化", 25, y+2, 115, 18, S["tag"])
    add("tag2", "创新2: CBAM注意力",  50, y_cbam+32, 105, 18, S["tag"])

    # ── NECK — FPN (top-down) ─────────────────────────────────────
    #    Row layout:  [Ups/Conv] → [Concat] → [C2f]
    nx1, nx2, nx3 = 275, 370, 475
    nw = 85
    nh = 26

    # FPN row 1:  CBAM → Ups → Concat(+P4) → C2f(256)
    fy1 = y_p4 + 40   # slightly below P4
    add("f_ups1", "Upsample",  nx1, fy1, nw, nh, S["ups"])
    add("f_cat1", "Concat",    nx2, fy1, nw, nh, S["concat"])
    add("f_c2f1", "C2f 256",   nx3, fy1, nw+10, nh, S["c2f"])
    con("f_ups1", "f_cat1")
    con("f_cat1", "f_c2f1")

    # FPN row 2:  C2f(256) → Ups → Concat(+P3) → C2f(128)
    fy2 = y_p3 + 3
    add("f_ups2", "Upsample",  nx1, fy2, nw, nh, S["ups"])
    add("f_cat2", "Concat",    nx2, fy2, nw, nh, S["concat"])
    add("f_c2f2", "C2f 128",   nx3, fy2, nw+10, nh, S["c2f"])
    con("f_ups2", "f_cat2")
    con("f_cat2", "f_c2f2")

    # FPN vertical: CBAM→Ups1
    cbam_mid_x = bx + bw
    con("b_cbam", "f_ups1", S["edge_skip"], "",
        [(cbam_mid_x, y_cbam+15), (255, y_cbam+15), (255, fy1+nh//2)])
    # C2f1 → Ups2
    con("f_c2f1", "f_ups2", S["edge"],  "",
        [(560, fy1+nh//2), (560, fy1-12), (260, fy1-12), (260, fy2+nh//2)])

    # Skip: backbone → neck concat
    con("b_g3", "f_cat1", S["edge_skip"], "P4",
        [(bx+bw, y_p4+bh//2), (230, y_p4+bh//2), (230, fy1+nh//2)])
    con("b_g2", "f_cat2", S["edge_skip"], "P3",
        [(bx+bw, y_p3+bh//2), (230, y_p3+bh//2), (230, fy2+nh//2)])

    # ── NECK — PAN (bottom-up) ────────────────────────────────────

    # PAN row 1:  C2f(128) → Conv → Concat(+FPN_C2f256) → C2f(256)
    py1 = fy1 + 50
    add("p_cv1",  "Conv 128 s2", nx1, py1, nw, nh, S["conv"])
    add("p_cat1", "Concat",      nx2, py1, nw, nh, S["concat"])
    add("p_c2f1", "C2f 256",     nx3, py1, nw+10, nh, S["c2f"])
    con("p_cv1",  "p_cat1")
    con("p_cat1", "p_c2f1")

    # PAN row 2:  C2f(256) → Conv → Concat(+CBAM) → C2f(512)
    py2 = py1 + 48
    add("p_cv2",  "Conv 256 s2", nx1, py2, nw, nh, S["conv"])
    add("p_cat2", "Concat",      nx2, py2, nw, nh, S["concat"])
    add("p_c2f2", "C2f 512",     nx3, py2, nw+10, nh, S["c2f"])
    con("p_cv2",  "p_cat2")
    con("p_cat2", "p_c2f2")

    # PAN vertical: C2f_P3→Conv1, C2f_P4_pan→Conv2
    con("f_c2f2", "p_cv1", S["edge"], "",
        [(560, fy2+nh//2), (560, py1-10), (260, py1-10), (260, py1+nh//2)])
    con("p_c2f1", "p_cv2", S["edge"], "",
        [(560, py1+nh//2), (560, py2-10), (260, py2-10), (260, py2+nh//2)])

    # Lateral: FPN C2f(256) → PAN Concat1
    con("f_c2f1", "p_cat1", S["edge"], "",
        [(560, fy1+nh), (560, py1+nh//2)])

    # Long skip: CBAM → PAN Concat2
    con("b_cbam", "p_cat2", S["edge_skip"], "P5",
        [(cbam_mid_x, y_cbam+25), (240, y_cbam+25), (240, py2+nh//2)])

    # ── HEAD — Detect ─────────────────────────────────────────────
    hx, hw, hh = 665, 105, 36

    add("det_p3", "Detect&lt;br&gt;P3 80×80", hx, fy2-5,  hw, hh, S["detect"])
    add("det_p4", "Detect&lt;br&gt;P4 40×40", hx, py1-5,  hw, hh, S["detect"])
    add("det_p5", "Detect&lt;br&gt;P5 20×20", hx, py2-5,  hw, hh, S["detect"])

    con("f_c2f2", "det_p3")
    con("p_c2f1", "det_p4")
    con("p_c2f2", "det_p5")

    # ── MODULE DETAILS (below main diagram) ───────────────────────
    dy = y + 45   # start right below backbone

    # Conv detail
    add("mod_conv", "Conv 模块",  18, dy, 175, 65, S["reg_mod"])
    add("md_cv", "Conv2d",   33, dy+25, 48, 24, S["conv"])
    add("md_bn", "BN",       89, dy+25, 32, 24, S["bn"])
    add("md_si", "SiLU",     129,dy+25, 40, 24, S["act"])
    con("md_cv", "md_bn", S["edge_thin"])
    con("md_bn", "md_si", S["edge_thin"])

    # C2f_Ghost detail
    add("mod_c2fg", "C2f_Ghost 模块", 205, dy, 230, 110, S["reg_mod"])
    add("md_fg1", "Conv",              215, dy+24, 45, 22, S["conv"])
    add("md_fg2", "Split",             268, dy+24, 42, 22, S["split"])
    add("md_fg3", "Ghost&lt;br&gt;BN",320, dy+22, 50, 26, S["ghost"])
    add("md_fg4", "Ghost&lt;br&gt;BN",320, dy+54, 50, 26, S["ghost"])
    add("md_fg5", "...",               375, dy+40, 15, 16, S["label"])
    add("md_fg6", "Concat",            268, dy+66, 42, 22, S["concat"])
    add("md_fg7", "Conv",              215, dy+66, 45, 22, S["conv"])
    con("md_fg1", "md_fg2", S["edge_thin"])
    con("md_fg2", "md_fg3", S["edge_thin"])
    con("md_fg3", "md_fg4", S["edge_thin"])
    con("md_fg2", "md_fg6", S["edge_thin"])
    con("md_fg4", "md_fg6", S["edge_thin"])
    con("md_fg6", "md_fg7", S["edge_thin"])

    # GhostBottleneck detail
    add("mod_gb", "GhostBottleneck", 205, dy+118, 230, 62, S["reg_mod"])
    add("md_g1", "GhostConv", 218, dy+142, 60, 22, S["ghost"])
    add("md_g2", "DWConv",    290, dy+142, 50, 22, S["conv"])
    add("md_g3", "GhostConv", 352, dy+142, 60, 22, S["ghost"])
    con("md_g1", "md_g2", S["edge_thin"])
    con("md_g2", "md_g3", S["edge_thin"])
    add("md_gp", "⊕", 416, dy+143, 18, 20,
        "ellipse;whiteSpace=wrap;html=1;fillColor=#E8EAF6;strokeColor=#283593;fontSize=9;fontStyle=1;")
    con("md_g3", "md_gp", S["edge_thin"])
    cells.append(edge(N["md_g1"], N["md_gp"], S["edge_res"], "",
        [(248, dy+167), (248, dy+176), (425, dy+176), (425, dy+158)]))

    # CBAM detail
    add("mod_cbam", "CBAM（创新2）", 448, dy, 180, 85, S["reg_mod"])
    add("md_ci", "输入",        460, dy+26, 38, 20, S["input"])
    add("md_ca", "通道注意力",   460, dy+54, 58, 22, S["ca"])
    add("md_sa", "空间注意力",   530, dy+54, 58, 22, S["sa"])
    add("md_co", "输出",        598, dy+26, 38, 20, S["input"])
    con("md_ci", "md_ca", S["edge_thin"])
    con("md_ca", "md_sa", S["edge_thin"])
    con("md_sa", "md_co", S["edge_thin"])

    # SPPF detail
    add("mod_sppf", "SPPF 模块", 448, dy+93, 180, 62, S["reg_mod"])
    add("md_s1", "Conv",     460, dy+118, 34, 22, S["conv"])
    add("md_s2", "MaxPool",  500, dy+118, 45, 22, S["pool"])
    add("md_s3", "MaxPool",  551, dy+118, 45, 22, S["pool"])
    add("md_s4", "Concat",   602, dy+118, 40, 22, S["concat"])
    con("md_s1", "md_s2", S["edge_thin"])
    con("md_s2", "md_s3", S["edge_thin"])
    con("md_s3", "md_s4", S["edge_thin"])

    # Wise-IoU detail
    add("mod_wiou", "Wise-IoU（创新3）", 640, dy, 155, 110, S["reg_mod"])
    add("md_wi", "CIoU",               658, dy+28, 48, 22, S["conv"])
    add("md_wb", "β 动态聚焦",          720, dy+28, 60, 22, S["wiou"])
    add("md_wm", "×", 700, dy+62, 18, 18,
        "ellipse;whiteSpace=wrap;html=1;fillColor=#FFCDD2;strokeColor=#C62828;fontSize=9;fontStyle=1;")
    add("md_wl", "Loss", 730, dy+60, 42, 22, S["wiou"])
    con("md_wi", "md_wm", S["edge_thin"])
    con("md_wb", "md_wm", S["edge_thin"])
    con("md_wm", "md_wl", S["edge_thin"])
    add("md_weq", "β=clip(IoU/IoU̅,0.5,2)", 650, dy+88, 130, 14, S["label"])

    # ── TITLE ─────────────────────────────────────────────────────
    add("title",
        "图1  改进 YOLOv8s-Ghost-CBAM-WiseIoU 算法网络结构图&lt;br&gt;"
        "Fig.1 Architecture of YOLOv8s-Ghost-CBAM-WiseIoU improved algorithm",
        150, dy+170, 520, 36,
        "text;html=1;align=center;verticalAlign=middle;resizable=0;points=[];"
        "autosize=1;strokeColor=none;fillColor=none;fontSize=12;fontStyle=1;fontColor=#333333;")

    return cells


def main():
    _id[0] = 2  # reset counter
    cells = build()
    inner = "\n        ".join(cells)
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" agent="gen_architecture_diagram.py" version="24.0.0" type="device">
  <diagram id="arch" name="YOLOv8s-Improved Architecture">
    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="0" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {inner}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(xml, encoding="utf-8")
    print(f"Saved: {OUT}")


if __name__ == "__main__":
    main()
