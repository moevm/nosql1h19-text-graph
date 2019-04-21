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

def describe_link(link, start_id=None, end_id=None):
    """Описание связи в HTML

    :param link: Связь из запроса через db.cypher_query
    :param start_id: id первой вершины
    :param end_id: id второй вершины
    """

    text = f"""
        <h1>Описание связи</h1>
        <h2>Процент пересечения: {link['intersection']:.2f}%</h2>
    """
    if start_id and end_id:
        text += f"""
        <b>Фрагмент 1: {start_id}</b>
        <b>Фрагмент 2: {end_id}</b>
        """
    return text
