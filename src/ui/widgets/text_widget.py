from PyQt5.QtWidgets import QTextBrowser
import re
import urllib.parse as parse


class TextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.collapse_ids = None
        self.source_html = None
        self.setOpenLinks(False)
        self.anchorClicked.connect(self._on_link_cliked)

    @staticmethod
    def _parse_collapses(text, collapse_ids=None):
        start = r'<!-- COLLAPSE .* -->'
        end = r'<!-- END COLLAPSE -->'
        starts = [(match.start(), match.end())
                  for match in re.finditer(start, text)]
        ends = [(match.start(), match.end())
                for match in re.finditer(end, text)]
        starts.reverse()
        ends.reverse()
        if collapse_ids is None or len(collapse_ids) != len(starts):
            collapse_ids = [True] * len(starts)
        for index, start, end_ in (
                zip(range(len(starts)-1, -1, -1), starts, ends)):
            desc = text[start[0]+14:start[1]-4]
            status = '[Открыть]' if not collapse_ids[index] else '[Закрыть]'
            link = f"""<a href='internal://collapse?id={index}'>
                            {desc} {status}
                        </a><br>"""
            if collapse_ids[index]:
                text = text[:start[0]] + '<div>' + link \
                     + text[start[1]:end_[0]-1] + '</div>' + text[end_[1]:]
            else:
                text = text[:start[0]] + '<div>' + link + '</div>' \
                     + text[end_[1]:]
        text = re.sub(end, '', text)
        return text, collapse_ids

    def setHtml(self, text):
        self.source_html = text

        text, self.collapse_ids = TextBrowser._parse_collapses(text)
        super().setHtml(text)

    def update_html(self):
        text = self.source_html
        text, self.collapse_ids = TextBrowser._parse_collapses(
            text, self.collapse_ids
        )
        super().setHtml(text)

    def _on_link_cliked(self, url):
        url = url.toString()
        parsed = parse.urlparse(url)
        if parsed.scheme == 'internal':
            if parsed.netloc == 'collapse':
                toggle_id = int(dict(parse.parse_qsl(parsed.query))['id'])
                self.collapse_ids[toggle_id] = not self.collapse_ids[toggle_id]
        self.update_html()
