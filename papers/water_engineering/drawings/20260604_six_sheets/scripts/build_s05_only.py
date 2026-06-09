from build_six_cad_sheets import Sheet, acad_app
from s05_components import draw_s05_components


def main():
    app = acad_app()
    sheet = Sheet(app, "S-05_典型构件尺寸图.dwg", 6, "典型构件尺寸图", "1:50")
    draw_s05_components(sheet)
    print(sheet.save())


if __name__ == "__main__":
    main()
