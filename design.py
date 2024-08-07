#https://coolors.co/palette/2d00f7-6a00f4-8900f2-a100f2-b100e8-bc00dd-d100d1-db00b6-e500a4-f20089
#from dataclasses import dataclass

#for now, i will use simple dicts and other lists, but later i will use data classes


class Design():
    
    white_style = "#fefefe"
    
    pink_style = "#6a00f4"
    purple_style = "#b100e8"
    blue_style = "#F20089"
    red_style = "#ef233c"
    
    main_pallete_style = [
        '#2D00F7',
        '#6A00F4',
        '#8900F2',
        '#A100F2',
        '#B100E8',
        '#BC00DD',
        '#D100D1',
        '#E500A4',
        '#F20089',]
    
    red_pallete_style = [ "#e01e37", "#c71f37", "#ef233c"]

    red_button_style = (
        "QPushButton {"
        "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,"
        f"stop:0 {red_pallete_style[0]}, stop:0.5 {red_pallete_style[1]}, stop:1 {red_pallete_style[2]});"
        "border-radius: 20px;"
        "font-size: 20px;"
        "color: rgba(254, 254, 254, 1);"
        "margin-top: 15px;"
        "margin-bottom: 15px;"
        "}"
    )