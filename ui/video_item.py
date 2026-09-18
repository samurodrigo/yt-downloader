from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QFrame,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap

from workers.thumbnail_worker import ThumbnailWorker


class VideoItem(QFrame):

    selected_changed = Signal(object)

    def __init__(self, video, parent=None):
        super().__init__(parent)

        self.video = video

        self.thumbnail_thread = None
        self.thumbnail_worker = None

        self.criar_interface()
        self.carregar_thumbnail()

    def criar_interface(self):

        self.setFrameShape(
            QFrame.StyledPanel
        )

        self.setFrameShadow(
            QFrame.Raised
        )

        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dfe7ee;
                border-radius: 12px;
            }

            QLabel {
                border: none;
                color: #1f2937;
            }

            QComboBox {
                padding: 5px 8px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: white;
                color: #374151;
            }
        """)

        self.setFixedHeight(118)

        layout_principal = QHBoxLayout()

        layout_principal.setContentsMargins(
            10,
            8,
            10,
            8
        )
        layout_principal.setSpacing(10)

        self.setLayout(
            layout_principal
        )

        # Checkbox
        self.checkbox = QCheckBox()

        self.checkbox.setChecked(
            self.video.selected
        )

        self.checkbox.stateChanged.connect(
            self.checkbox_alterado
        )

        layout_principal.addWidget(
            self.checkbox
        )

        # Thumbnail
        self.thumbnail = QLabel(
            "Carregando..."
        )

        self.thumbnail.setFixedSize(
            140,
            84
        )

        self.thumbnail.setAlignment(
            Qt.AlignCenter
        )

        self.thumbnail.setStyleSheet("""
            background-color: #1f2937;
            color: #d1d5db;
            border-radius: 8px;
            font-size: 11px;
        """)

        layout_principal.addWidget(
            self.thumbnail
        )

        # Informações
        layout_info = QVBoxLayout()

        self.titulo = QLabel(
            self.video.title
        )

        self.titulo.setWordWrap(
            True
        )

        self.titulo.setStyleSheet("""
            font-size: 15px;
            font-weight: 700;
            color: #111827;
        """)

        layout_info.addWidget(
            self.titulo
        )

        canal = (
            self.video.channel
            or "Canal desconhecido"
        )

        self.label_canal = QLabel(
            f"Canal: {canal}"
        )
        self.label_canal.setStyleSheet("color: #4b5563; font-size: 12px;")

        layout_info.addWidget(
            self.label_canal
        )

        if self.video.duration:

            duracao = self.formatar_duracao(
                self.video.duration
            )

            self.label_duracao = QLabel(
                f"Duração: {duracao}"
            )
            self.label_duracao.setStyleSheet("color: #4b5563; font-size: 12px;")

            layout_info.addWidget(
                self.label_duracao
            )

        layout_info.addStretch()

        layout_principal.addLayout(
            layout_info,
            stretch=1
        )


    def formatar_duracao(self, segundos):

        minutos, segundos = divmod(
            segundos,
            60
        )

        horas, minutos = divmod(
            minutos,
            60
        )

        if horas:

            return (
                f"{horas:02d}:"
                f"{minutos:02d}:"
                f"{segundos:02d}"
            )

        return (
            f"{minutos:02d}:"
            f"{segundos:02d}"
        )

    def checkbox_alterado(self, estado):

        selecionado = bool(estado)

        self.video.selected = selecionado

        self.selected_changed.emit(
            self.video
        )

    def carregar_thumbnail(self):

        if not self.video.thumbnail:

            self.thumbnail.setText(
                "Sem thumbnail"
            )

            return

        self.thumbnail_thread = QThread()

        self.thumbnail_worker = (
            ThumbnailWorker(
                self.video.thumbnail
            )
        )

        self.thumbnail_worker.moveToThread(
            self.thumbnail_thread
        )

        self.thumbnail_thread.started.connect(
            self.thumbnail_worker.run
        )

        self.thumbnail_worker.finished.connect(
            self.thumbnail_carregada
        )

        self.thumbnail_worker.error.connect(
            self.thumbnail_erro
        )

        self.thumbnail_worker.finished.connect(
            self.thumbnail_thread.quit
        )

        self.thumbnail_worker.error.connect(
            self.thumbnail_thread.quit
        )

        self.thumbnail_worker.finished.connect(
            self.thumbnail_worker.deleteLater
        )

        self.thumbnail_worker.error.connect(
            self.thumbnail_worker.deleteLater
        )

        self.thumbnail_thread.finished.connect(
            self.thumbnail_thread.deleteLater
        )

        self.thumbnail_thread.finished.connect(
            self.thumbnail_thread_finalizada
        )

        self.thumbnail_thread.start()

    def thumbnail_carregada(self, dados):

        pixmap = QPixmap()

        if not pixmap.loadFromData(dados):

            self.thumbnail.setText(
                "Thumbnail inválida"
            )

            return

        pixmap = pixmap.scaled(
            160,
            90,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.thumbnail.setPixmap(
            pixmap
        )

    def thumbnail_erro(self, mensagem):

        self.thumbnail.setText(
            "Sem thumbnail"
        )

    def thumbnail_thread_finalizada(self):

        self.thumbnail_thread = None
        self.thumbnail_worker = None