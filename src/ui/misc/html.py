def encapsulate_html(body):
    """Метод, оборачивающий тело HTML в остальной код.
    Тут применяются разные стили и т.п.

    :param body: Тело HTML
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    </style>
    </head>
    <body>""" + body + """
    </body>
    </html>
    """
