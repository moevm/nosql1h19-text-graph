from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QTextBrowser
import re
import urllib.parse as parse


class CollapsibleHtml:
    def __init__(self):
        self.collapse_ids = None
        self.source_html = None

    def _parse_collapses(self, text, collapse_ids=None):
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

    def _on_link_cliked(self, url):
        if isinstance(url, QUrl):
            url = url.toString()
        parsed = parse.urlparse(url)
        if parsed.scheme == 'internal':
            if parsed.netloc == 'collapse':
                toggle_id = int(dict(parse.parse_qsl(parsed.query))['id'])
                self.collapse_ids[toggle_id] = not self.collapse_ids[toggle_id]

    def _get_html(self, text=None):
        if text is not None:
            self.source_html = text
            text, self.collapse_ids = self._parse_collapses(text)
            return text
        else:
            text = self.source_html
            text, self.collapse_ids = self._parse_collapses(
                text, self.collapse_ids)
            return text


class TextBrowser(QTextBrowser, CollapsibleHtml):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setOpenLinks(False)
        self.anchorClicked.connect(self._on_link_cliked)

    def setHtml(self, text):
        super().setHtml(self._get_html(text))

    def _on_link_cliked(self, url):
        super()._on_link_cliked(url)
        super().setHtml(self._get_html())

