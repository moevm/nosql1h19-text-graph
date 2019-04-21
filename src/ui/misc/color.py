from PyQt5.QtGui import QColor


def get_foreground_color(color: QColor):
    """Получить цвет текста по цвету фона

    :param color: Цвет фона
    :type color: QColor
    """
    text_color = QColor.fromHslF((color.hslHueF() + 0.5) % 1,
                                 (color.hslSaturationF() + 0.5) % 1,
                                 (color.lightnessF() + 0.5) % 1)
    return text_color
