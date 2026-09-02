from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QCheckBox,
    QComboBox,
    QFrame,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap

from core.formats import FormatManager
from workers.thumbnail_worker import ThumbnailWorker


class VideoItem(QFrame):

    selected_changed = Signal(object)

    def __init__(self, video, parent=None):
        super().__init__(parent)

        self.video = video

        self.thumbnail_thread = None
        self.thumbnail_worker = None

        self.criar_interface()
        self.atualizar_qualidades()
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
                background-color: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
            }

            QLabel {
                border: none;
            }

            QComboBox {
                padding: 5px;
                border: 1px solid #bbbbbb;
                border-radius: 4px;
                background: white;
            }
        """)

        layout_principal = QHBoxLayout()

        layout_principal.setContentsMargins(
            10,
            10,
            10,
            10
        )

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
            160,
            90
        )

        self.thumbnail.setAlignment(
            Qt.AlignCenter
        )

        self.thumbnail.setStyleSheet("""
            background-color: #202020;
            color: #aaaaaa;
            border-radius: 4px;
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
            font-weight: bold;
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

            layout_info.addWidget(
                self.label_duracao
            )

        layout_info.addStretch()

        layout_principal.addLayout(
            layout_info,
            stretch=1
        )

        # Opções
        layout_opcoes = QVBoxLayout()

        label_formato = QLabel(
            "Formato"
        )

        self.combo_formato = QComboBox()

        self.combo_formato.addItems([
            "MP4",
            "MP3",
        ])

        self.combo_formato.setCurrentText(
            "MP4"
        )

        self.combo_formato.currentTextChanged.connect(
            self.formato_alterado
        )

        label_qualidade = QLabel(
            "Qualidade"
        )

        self.combo_qualidade = QComboBox()

        self.combo_qualidade.currentIndexChanged.connect(
            self.qualidade_alterada
        )

        layout_opcoes.addWidget(
            label_formato
        )

        layout_opcoes.addWidget(
            self.combo_formato
        )

        layout_opcoes.addWidget(
            label_qualidade
        )

        layout_opcoes.addWidget(
            self.combo_qualidade
        )

        layout_opcoes.addStretch()

        layout_principal.addLayout(
            layout_opcoes
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

    def atualizar_qualidades(self):

        self.combo_qualidade.blockSignals(
            True
        )

        self.combo_qualidade.clear()

        formato = (
            self.combo_formato.currentText()
        )

        if formato == "MP4":

            self.combo_qualidade.addItem(
                "Melhor disponível",
                "best"
            )

            qualidades = (
                FormatManager
                .get_video_qualities(
                    self.video.formats
                )
            )

            for qualidade in qualidades:

                nome = (
                    FormatManager
                    .format_video_quality(
                        qualidade
                    )
                )

                self.combo_qualidade.addItem(
                    nome,
                    str(qualidade)
                )

        else:

            self.combo_qualidade.addItem(
                "Melhor áudio disponível",
                "best"
            )

            qualidades = (
                FormatManager
                .get_audio_qualities(
                    self.video.formats
                )
            )

            for qualidade in qualidades:

                nome = (
                    FormatManager
                    .format_audio_quality(
                        qualidade
                    )
                )

                self.combo_qualidade.addItem(
                    nome,
                    str(qualidade)
                )

        self.combo_qualidade.setCurrentIndex(
            0
        )

        self.video.selected_quality = (
            self.combo_qualidade.itemData(0)
        )

        self.combo_qualidade.blockSignals(
            False
        )

    def formato_alterado(self, formato):

        if formato == "MP3":
            self.video.selected_format = "mp3"
        else:
            self.video.selected_format = "mp4"

        self.atualizar_qualidades()

    def qualidade_alterada(self, index):

        valor = (
            self.combo_qualidade.itemData(
                index
            )
        )

        if valor is not None:

            self.video.selected_quality = (
                valor
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