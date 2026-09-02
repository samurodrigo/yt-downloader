from PySide6.QtCore import QObject, Signal, Slot
import urllib.request


class ThumbnailWorker(QObject):

    finished = Signal(bytes)
    error = Signal(str)

    def __init__(self, url):
        super().__init__()

        self.url = url

    @Slot()
    def run(self):

        try:
            request = urllib.request.Request(
                self.url,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            with urllib.request.urlopen(
                request,
                timeout=10
            ) as resposta:

                dados = resposta.read()

            self.finished.emit(dados)

        except Exception as erro:

            self.error.emit(str(erro))