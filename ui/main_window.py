from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QScrollArea,
    QFileDialog,
)

from PySide6.QtCore import (
    Qt,
    QThread,
)

from core.youtube import YouTubeAnalyzer
from workers.analyze_worker import AnalyzeWorker
from workers.download_worker import DownloadWorker
from ui.video_item import VideoItem
import os


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Meu Downloader"
        )

        self.resize(
            1000,
            700
        )

        # =====================================================
        # OBJETOS PRINCIPAIS
        # =====================================================

        self.analyzer = YouTubeAnalyzer()

        # Thread da análise
        self.thread = None
        self.worker = None

        # Thread do download
        self.download_thread = None
        self.download_worker = None

        # Lista de itens de vídeo
        self.video_items = []

        # =====================================================
        # INTERFACE
        # =====================================================
        self.pasta_destino = os.path.dirname(
            os.path.abspath(__file__)
        )

        self.criar_interface()


    # =========================================================
    # INTERFACE
    # =========================================================

    def criar_interface(self):

        # =====================================================
        # WIDGET PRINCIPAL
        # =====================================================

        central = QWidget()

        self.setCentralWidget(
            central
        )

        layout_principal = QVBoxLayout()

        layout_principal.setContentsMargins(
            15,
            15,
            15,
            15
        )

        layout_principal.setSpacing(
            10
        )

        central.setLayout(
            layout_principal
        )

        # =====================================================
        # TÍTULO
        # =====================================================

        titulo = QLabel(
            "Meu Downloader"
        )

        titulo.setAlignment(
            Qt.AlignCenter
        )

        titulo.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            padding: 10px;
        """)

        layout_principal.addWidget(
            titulo
        )

        # =====================================================
        # ÁREA DA URL
        # =====================================================

        layout_url = QHBoxLayout()

        self.campo_url = QLineEdit()

        self.campo_url.setPlaceholderText(
            "Cole aqui a URL de um vídeo ou playlist do YouTube..."
        )

        self.botao_analisar = QPushButton(
            "Analisar"
        )

        self.botao_analisar.setMinimumWidth(
            120
        )

        layout_url.addWidget(
            self.campo_url
        )

        layout_url.addWidget(
            self.botao_analisar
        )

        layout_principal.addLayout(
            layout_url
        )

        # =====================================================
        # CABEÇALHO DA ÁREA DE VÍDEOS
        # =====================================================

        layout_cabecalho_videos = QHBoxLayout()

        label_resultados = QLabel(
            "Vídeos"
        )

        label_resultados.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
        """)

        layout_cabecalho_videos.addWidget(
            label_resultados
        )

        layout_cabecalho_videos.addStretch()

        self.label_selecionados = QLabel(
            "0 selecionados"
        )

        self.label_selecionados.setStyleSheet("""
            font-weight: bold;
            color: #555555;
        """)

        layout_cabecalho_videos.addWidget(
            self.label_selecionados
        )

        layout_principal.addLayout(
            layout_cabecalho_videos
        )

        # =====================================================
        # CONTROLES DE SELEÇÃO
        # =====================================================

        layout_selecao = QHBoxLayout()

        self.botao_selecionar_todos = QPushButton(
            "Selecionar todos"
        )

        self.botao_desmarcar_todos = QPushButton(
            "Desmarcar todos"
        )

        layout_selecao.addWidget(
            self.botao_selecionar_todos
        )

        layout_selecao.addWidget(
            self.botao_desmarcar_todos
        )

        layout_selecao.addStretch()

        layout_principal.addLayout(
            layout_selecao
        )

        # =====================================================
        # LISTA DE VÍDEOS
        # =====================================================

        self.scroll_videos = QScrollArea()

        self.scroll_videos.setWidgetResizable(
            True
        )

        self.container_videos = QWidget()

        self.layout_videos = QVBoxLayout(
            self.container_videos
        )

        self.layout_videos.setAlignment(
            Qt.AlignTop
        )

        self.layout_videos.setSpacing(
            8
        )

        self.scroll_videos.setWidget(
            self.container_videos
        )

        layout_principal.addWidget(
            self.scroll_videos,
            stretch=1
        )

        # =====================================================
        # PASTA DE DESTINO
        # =====================================================

        layout_pasta = QHBoxLayout()

        label_pasta = QLabel(
            "Salvar em:"
        )

        self.campo_pasta = QLineEdit()

        self.campo_pasta.setText(
            self.pasta_destino
        )

        self.campo_pasta.setPlaceholderText(
            "Selecione a pasta onde os arquivos serão salvos..."
        )

        self.botao_pasta = QPushButton(
            "Selecionar"
        )

        layout_pasta.addWidget(
            label_pasta
        )

        layout_pasta.addWidget(
            self.campo_pasta
        )

        layout_pasta.addWidget(
            self.botao_pasta
        )

        layout_principal.addLayout(
            layout_pasta
        )

        # =====================================================
        # ÁREA DE DOWNLOAD
        # =====================================================

        layout_download = QVBoxLayout()

        layout_download_topo = QHBoxLayout()

        self.label_download = QLabel(
            "Nenhum vídeo selecionado"
        )

        self.label_download.setStyleSheet("""
            font-weight: bold;
            font-size: 14px;
        """)

        self.botao_download = QPushButton(
            "Iniciar download"
        )

        self.botao_download.setMinimumWidth(
            160
        )

        self.botao_download.setEnabled(
            False
        )

        layout_download_topo.addWidget(
            self.label_download
        )

        layout_download_topo.addStretch()

        layout_download_topo.addWidget(
            self.botao_download
        )

        layout_download.addLayout(
            layout_download_topo
        )

        # =====================================================
        # BARRA DE PROGRESSO
        # =====================================================

        self.barra_progresso = QProgressBar()

        self.barra_progresso.setRange(
            0,
            100
        )

        self.barra_progresso.setValue(
            0
        )

        self.barra_progresso.setVisible(
            False
        )

        layout_download.addWidget(
            self.barra_progresso
        )

        layout_principal.addLayout(
            layout_download
        )

        # =====================================================
        # LOG
        # =====================================================

        label_log = QLabel(
            "Log"
        )

        label_log.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
        """)

        layout_principal.addWidget(
            label_log
        )

        self.log = QTextEdit()

        self.log.setReadOnly(
            True
        )

        self.log.setMaximumHeight(
            150
        )

        layout_principal.addWidget(
            self.log
        )

        # =====================================================
        # EVENTOS
        # =====================================================

        self.botao_analisar.clicked.connect(
            self.analisar
        )

        self.botao_selecionar_todos.clicked.connect(
            self.selecionar_todos
        )

        self.botao_desmarcar_todos.clicked.connect(
            self.desmarcar_todos
        )

        self.botao_download.clicked.connect(
            self.iniciar_download
        )

        self.botao_pasta.clicked.connect(
            self.selecionar_pasta
        )

    # =========================================================
    # ANÁLISE
    # =========================================================

    def analisar(self):

        url = self.campo_url.text().strip()

        if not url:

            self.log.append(
                "Informe uma URL."
            )

            return

        self.botao_analisar.setEnabled(
            False
        )

        self.botao_analisar.setText(
            "Analisando..."
        )

        self.log.clear()

        self.log.append(
            "Analisando URL..."
        )

        self.log.append(
            "A interface continuará disponível durante a análise."
        )

        # =====================================================
        # THREAD
        # =====================================================

        self.thread = QThread()

        self.worker = AnalyzeWorker(
            self.analyzer,
            url
        )

        self.worker.moveToThread(
            self.thread
        )

        # =====================================================
        # SINAIS
        # =====================================================

        self.thread.started.connect(
            self.worker.run
        )

        self.worker.finished.connect(
            self.analise_concluida
        )

        self.worker.error.connect(
            self.analise_erro
        )

        # =====================================================
        # ENCERRAMENTO
        # =====================================================

        self.worker.finished.connect(
            self.thread.quit
        )

        self.worker.error.connect(
            self.thread.quit
        )

        self.worker.finished.connect(
            self.worker.deleteLater
        )

        self.worker.error.connect(
            self.worker.deleteLater
        )

        self.thread.finished.connect(
            self.thread.deleteLater
        )

        self.thread.finished.connect(
            self.thread_finalizada
        )

        # =====================================================
        # INICIAR
        # =====================================================

        self.thread.start()

    # =========================================================
    # ANÁLISE CONCLUÍDA
    # =========================================================

    def analise_concluida(
        self,
        resultado
    ):

        self.log.append(
            "✓ Análise concluída."
        )

        self.mostrar_videos(
            resultado["videos"]
        )

    # =========================================================
    # ERRO NA ANÁLISE
    # =========================================================

    def analise_erro(
        self,
        mensagem
    ):

        self.log.append(
            "✗ Erro durante a análise:"
        )

        self.log.append(
            mensagem
        )

    # =========================================================
    # THREAD DA ANÁLISE FINALIZADA
    # =========================================================

    def thread_finalizada(self):

        self.botao_analisar.setEnabled(
            True
        )

        self.botao_analisar.setText(
            "Analisar"
        )

        self.thread = None
        self.worker = None

    # =========================================================
    # DURAÇÃO
    # =========================================================

    def formatar_duracao(
        self,
        segundos
    ):

        if segundos is None:
            return "--:--"

        minutos, segundos = divmod(
            segundos,
            60
        )

        horas, minutos = divmod(
            minutos,
            60
        )

        if horas > 0:

            return (
                f"{horas:02d}:"
                f"{minutos:02d}:"
                f"{segundos:02d}"
            )

        return (
            f"{minutos:02d}:"
            f"{segundos:02d}"
        )

    # =========================================================
    # MOSTRAR VÍDEOS
    # =========================================================

    def mostrar_videos(
        self,
        videos
    ):

        # =====================================================
        # REMOVER VÍDEOS ANTIGOS
        # =====================================================

        for item in self.video_items:

            self.layout_videos.removeWidget(
                item
            )

            item.deleteLater()

        self.video_items.clear()

        # =====================================================
        # ADICIONAR NOVOS VÍDEOS
        # =====================================================

        for video in videos:

            item = VideoItem(
                video
            )

            item.selected_changed.connect(
                self.atualizar_contador
            )

            self.layout_videos.addWidget(
                item
            )

            self.video_items.append(
                item
            )

        self.log.append(
            f"{len(videos)} vídeo(s) carregado(s)."
        )

        self.atualizar_contador()

    # =========================================================
    # SELECIONAR TODOS
    # =========================================================

    def selecionar_todos(self):

        for item in self.video_items:

            item.checkbox.setChecked(
                True
            )

        self.atualizar_contador()

    # =========================================================
    # DESMARCAR TODOS
    # =========================================================

    def desmarcar_todos(self):

        for item in self.video_items:

            item.checkbox.setChecked(
                False
            )

        self.atualizar_contador()

    # =========================================================
    # ATUALIZAR CONTADOR
    # =========================================================

    def atualizar_contador(
        self,
        video=None
    ):

        quantidade = sum(
            1
            for item in self.video_items
            if item.video.selected
        )

        self.label_selecionados.setText(
            f"{quantidade} selecionado(s)"
        )

        # =====================================================
        # NENHUM
        # =====================================================

        if quantidade == 0:

            self.label_download.setText(
                "Nenhum vídeo selecionado"
            )

            self.botao_download.setEnabled(
                False
            )

        # =====================================================
        # UM
        # =====================================================

        elif quantidade == 1:

            self.label_download.setText(
                "1 vídeo pronto para download"
            )

            self.botao_download.setEnabled(
                True
            )

        # =====================================================
        # VÁRIOS
        # =====================================================

        else:

            self.label_download.setText(
                f"{quantidade} vídeos prontos para download"
            )

            self.botao_download.setEnabled(
                True
            )

    # =========================================================
    # SELECIONAR PASTA
    # =========================================================

    def selecionar_pasta(self):

        pasta = QFileDialog.getExistingDirectory(
            self,
            "Selecionar pasta de destino"
        )

        if pasta:

            self.campo_pasta.setText(
                pasta
            )

    # =========================================================
    # INICIAR DOWNLOAD
    # =========================================================

    def iniciar_download(self):

        # =====================================================
        # OBTER VÍDEOS SELECIONADOS
        # =====================================================

        selecionados = [
            item.video
            for item in self.video_items
            if item.video.selected
        ]

        if not selecionados:

            self.log.append(
                "Nenhum vídeo selecionado."
            )

            return

        # =====================================================
        # VERIFICAR PASTA
        # =====================================================

        pasta = (
            self.campo_pasta.text()
            .strip()
        )

        if not pasta:

            self.log.append(
                "Selecione uma pasta de destino."
            )

            return

        # =====================================================
        # PREPARAR INTERFACE
        # =====================================================

        self.botao_download.setEnabled(
            False
        )

        self.botao_selecionar_todos.setEnabled(
            False
        )

        self.botao_desmarcar_todos.setEnabled(
            False
        )

        self.botao_analisar.setEnabled(
            False
        )

        self.campo_url.setEnabled(
            False
        )

        self.campo_pasta.setEnabled(
            False
        )

        self.botao_pasta.setEnabled(
            False
        )

        self.barra_progresso.setVisible(
            True
        )

        self.barra_progresso.setValue(
            0
        )

        self.label_download.setText(
            "Preparando download..."
        )

        # =====================================================
        # LOG
        # =====================================================

        self.log.append(
            ""
        )

        self.log.append(
            "========================================"
        )

        self.log.append(
            f"Iniciando {len(selecionados)} vídeo(s)..."
        )

        self.log.append(
            f"Destino: {pasta}"
        )

        self.log.append(
            "========================================"
        )

        # =====================================================
        # CRIAR THREAD
        # =====================================================

        self.download_thread = QThread()

        self.download_worker = DownloadWorker(
            selecionados,
            pasta
        )

        self.download_worker.moveToThread(
            self.download_thread
        )

        # =====================================================
        # INÍCIO
        # =====================================================

        self.download_thread.started.connect(
            self.download_worker.run
        )

        # =====================================================
        # PROGRESSO
        # =====================================================

        self.download_worker.progress.connect(
            self.download_progresso
        )

        # =====================================================
        # LOG
        # =====================================================

        self.download_worker.log.connect(
            self.log.append
        )

        # =====================================================
        # VÍDEO CONCLUÍDO
        # =====================================================

        self.download_worker.video_finished.connect(
            self.video_download_concluido
        )

        # =====================================================
        # TODOS CONCLUÍDOS
        # =====================================================

        self.download_worker.finished.connect(
            self.download_concluido
        )

        # =====================================================
        # ERRO
        # =====================================================

        self.download_worker.error.connect(
            self.download_erro
        )

        # =====================================================
        # ENCERRAMENTO
        # =====================================================

        self.download_worker.finished.connect(
            self.download_thread.quit
        )

        self.download_worker.error.connect(
            self.download_thread.quit
        )

        self.download_worker.finished.connect(
            self.download_worker.deleteLater
        )

        self.download_worker.error.connect(
            self.download_worker.deleteLater
        )

        self.download_thread.finished.connect(
            self.download_thread.deleteLater
        )

        self.download_thread.finished.connect(
            self.download_thread_finalizada
        )

        # =====================================================
        # INICIAR THREAD
        # =====================================================

        self.download_thread.start()

    # =========================================================
    # PROGRESSO DO DOWNLOAD
    # =========================================================

    def download_progresso(
        self,
        dados
    ):

        status = dados.get(
            "status"
        )

        # -----------------------------------------------------
        # Download em andamento
        # -----------------------------------------------------

        if status == "downloading":

            percentual = dados.get(
                "_percent_str",
                "0%"
            )

            try:

                valor = float(
                    percentual
                    .replace(
                        "%",
                        ""
                    )
                    .strip()
                )

            except (
                ValueError,
                AttributeError
            ):

                valor = 0

            self.barra_progresso.setValue(
                int(valor)
            )

            velocidade = dados.get(
                "_speed_str",
                ""
            )

            eta = dados.get(
                "_eta_str",
                ""
            )

            self.label_download.setText(
                f"Baixando... "
                f"{percentual} | "
                f"{velocidade} | "
                f"ETA {eta}"
            )

        # -----------------------------------------------------
        # Download concluído pelo yt-dlp
        # -----------------------------------------------------

        elif status == "finished":

            self.barra_progresso.setValue(
                100
            )

            self.label_download.setText(
                "Processando arquivo..."
            )

    # =========================================================
    # VÍDEO CONCLUÍDO
    # =========================================================

    def video_download_concluido(
        self,
        resultado
    ):

        video = resultado[
            "video"
        ]

        if resultado[
            "success"
        ]:

            self.log.append(
                f"✓ Download concluído: "
                f"{video.title}"
            )

        else:

            self.log.append(
                f"✗ Falha no download: "
                f"{video.title}"
            )

    # =========================================================
    # TODOS OS DOWNLOADS CONCLUÍDOS
    # =========================================================

    def download_concluido(
        self,
        resultados
    ):

        total = len(
            resultados
        )

        sucessos = sum(
            1
            for resultado in resultados
            if resultado["success"]
        )

        erros = (
            total - sucessos
        )

        self.barra_progresso.setValue(
            100
        )

        self.label_download.setText(
            f"Download finalizado: "
            f"{sucessos}/{total}"
        )

        self.log.append(
            ""
        )

        self.log.append(
            "========================================"
        )

        self.log.append(
            "DOWNLOAD FINALIZADO"
        )

        self.log.append(
            f"Downloads concluídos: {sucessos}"
        )

        self.log.append(
            f"Downloads com erro: {erros}"
        )

        self.log.append(
            "========================================"
        )

    # =========================================================
    # ERRO DO DOWNLOAD
    # =========================================================

    def download_erro(
        self,
        mensagem
    ):

        self.log.append(
            "✗ Erro no download:"
        )

        self.log.append(
            mensagem
        )

    # =========================================================
    # THREAD DO DOWNLOAD FINALIZADA
    # =========================================================

    def download_thread_finalizada(
        self
    ):

        self.botao_analisar.setEnabled(
            True
        )

        self.botao_selecionar_todos.setEnabled(
            True
        )

        self.botao_desmarcar_todos.setEnabled(
            True
        )

        self.campo_url.setEnabled(
            True
        )

        self.campo_pasta.setEnabled(
            True
        )

        self.botao_pasta.setEnabled(
            True
        )

        self.botao_download.setEnabled(
            True
        )

        self.download_thread = None

        self.download_worker = None