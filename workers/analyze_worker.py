from PySide6.QtCore import QObject, Signal, Slot


class AnalyzeWorker(QObject):

    finished = Signal(object)
    error = Signal(str)

    def __init__(self, analyzer, url):
        super().__init__()

        self.analyzer = analyzer
        self.url = url

    @Slot()
    def run(self):

        try:
            resultado = self.analyzer.analisar(self.url)

            self.finished.emit(resultado)

        except Exception as erro:
            self.error.emit(str(erro))