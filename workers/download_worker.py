from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)

from core.downloader import YouTubeDownloader


class DownloadWorker(QObject):

    # Progresso de um vídeo
    progress = Signal(object)

    # Mensagens para o log
    log = Signal(str)

    # Download de um vídeo concluído
    video_finished = Signal(object)

    # Todos os downloads terminaram
    finished = Signal(object)

    # Erro geral
    error = Signal(str)

    def __init__(
        self,
        videos,
        pasta_destino,
    ):

        super().__init__()

        self.videos = videos
        self.pasta_destino = pasta_destino

        self.downloader = (
            YouTubeDownloader()
        )

    @Slot()
    def run(self):

        resultados = []

        total = len(
            self.videos
        )

        self.log.emit(
            f"Iniciando download de "
            f"{total} vídeo(s)..."
        )

        for indice, video in enumerate(
            self.videos,
            start=1
        ):

            try:

                self.log.emit(
                    ""
                )

                self.log.emit(
                    f"[{indice}/{total}] "
                    f"Baixando: {video.title}"
                )

                self.log.emit(
                    f"Formato: "
                    f"{video.selected_format.upper()}"
                )

                self.log.emit(
                    f"Qualidade: "
                    f"{video.selected_quality}"
                )

                resultado = (
                    self.downloader.baixar(
                        video,
                        self.pasta_destino,
                        progress_hook=self.progress_hook,
                    )
                )

                dados_resultado = {
                    "video": video,
                    "success": True,
                    "result": resultado,
                    "index": indice,
                    "total": total,
                }

                resultados.append(
                    dados_resultado
                )

                self.video_finished.emit(
                    dados_resultado
                )

                self.log.emit(
                    f"✓ [{indice}/{total}] "
                    f"Concluído: {video.title}"
                )

            except Exception as erro:

                dados_resultado = {
                    "video": video,
                    "success": False,
                    "error": str(erro),
                    "index": indice,
                    "total": total,
                }

                resultados.append(
                    dados_resultado
                )

                self.log.emit(
                    f"✗ [{indice}/{total}] "
                    f"Erro: {video.title}"
                )

                self.log.emit(
                    str(erro)
                )

                self.video_finished.emit(
                    dados_resultado
                )

        self.log.emit(
            ""
        )

        self.log.emit(
            "Download finalizado."
        )

        self.finished.emit(
            resultados
        )

    def progress_hook(self, dados):

        self.progress.emit(
            dados
        )