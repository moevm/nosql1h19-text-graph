from .abstract import AbstractReportItem
from api import Describer, Plotter


class StatsReport(AbstractReportItem):
    def __init__(self, processor, parent=None):
        self.name = 'Общая статистика'
        super().__init__(processor, parent)

    def create_html(self):
        describer = Describer(None, self.processor)
        return describer.describe_results(accs=False, all_algs=True)


class LenghtDispGraph(AbstractReportItem):
    def __init__(self, processor, parent=None):
        self.name = 'Распределение длин фрагментов'
        super().__init__(processor, parent)

    def create_html(self):
        plotter = Plotter(self.processor)
        fig = plotter.fragments_length_plot()
        fig_base = Plotter.fig_to_base64_tag(fig)
        return f"""
            <center>
                {fig_base}
            </center>"""
