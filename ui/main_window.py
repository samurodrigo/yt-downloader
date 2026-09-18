import sys
from pathlib import Path
import html
import os

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
    QSizePolicy,
    QCheckBox,
    QComboBox,
    QDialog,
)

from PySide6.QtWebEngineWidgets import QWebEngineView

from PySide6.QtCore import (
    Qt,
    QThread,
    QUrl,
)

from core.youtube import YouTubeAnalyzer
from workers.analyze_worker import AnalyzeWorker
from workers.download_worker import DownloadWorker
from ui.video_item import VideoItem


class LogDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Logs")
        self.resize(700, 420)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.texto = QTextEdit()
        self.texto.setReadOnly(True)
        self.texto.setStyleSheet("""
            QTextEdit {
                background: #ffffff;
                border: 1px solid #dfe7ee;
                border-radius: 8px;
                color: #374151;
            }
        """)

        botao_limpar = QPushButton("Limpar")
        botao_limpar.setStyleSheet("""
            QPushButton {
                background: #e5e7eb;
                border: none;
                border-radius: 8px;
                color: #374151;
                font-weight: 600;
                padding: 8px 12px;
            }
        """)
        botao_limpar.clicked.connect(self.texto.clear)

        layout.addWidget(self.texto)
        layout.addWidget(botao_limpar, alignment=Qt.AlignRight)


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
        self.monetization_url = os.getenv(
            "YT_DOWNLOADER_MONETIZATION_URL",
            ""
        ).strip()

        self.log_dialog = LogDialog(self)
        self.log = self.log_dialog.texto

        # =====================================================
        # INTERFACE
        # =====================================================
        self.pasta_destino = str(
            self._resolver_pasta_inicial()
        )

        self.criar_interface()

    def _resolver_pasta_inicial(self):

        if getattr(sys, "frozen", False):

            base_dir = Path(
                sys.executable
            ).resolve().parent

        else:

            base_dir = Path.cwd()

        pasta_inicial = base_dir / "downloads"

        pasta_inicial.mkdir(
            parents=True,
            exist_ok=True
        )

        return pasta_inicial


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
            12
        )

        central.setLayout(
            layout_principal
        )

        central.setStyleSheet("""
            QWidget {
                background-color: #edf3f7;
                color: #1f2937;
            }
            QLineEdit, QComboBox, QTextEdit, QPushButton {
                border-radius: 8px;
            }
        """)

        # =====================================================
        # TÍTULO
        # =====================================================

        row_title = QHBoxLayout()

        icon_app = QLabel("◉")
        icon_app.setFixedSize(24, 24)
        icon_app.setAlignment(Qt.AlignCenter)
        icon_app.setStyleSheet("""
            background: #e8f1ff;
            color: #2b6df7;
            border-radius: 12px;
            font-size: 14px;
            font-weight: bold;
        """)

        titulo = QLabel("Meu Downloader")
        titulo.setAlignment(Qt.AlignLeft)
        titulo.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #1f2937;
        """)

        row_title.addWidget(icon_app)
        row_title.addWidget(titulo)
        row_title.addStretch()

        title_buttons = QHBoxLayout()
        title_buttons.setSpacing(8)

        self.botao_logs = QPushButton("Logs")
        self.botao_logs.setFixedHeight(30)
        self.botao_logs.setStyleSheet("""
            QPushButton {
                background: #dbeafe;
                border: none;
                border-radius: 8px;
                color: #1d4ed8;
                font-weight: 600;
                padding: 0 12px;
            }
        """)

        button_min = QPushButton("—")
        button_min.setFixedSize(30, 30)
        button_min.setStyleSheet("""
            QPushButton {
                background: #e5e7eb;
                border: none;
                border-radius: 8px;
                color: #374151;
                font-weight: bold;
            }
        """)

        button_close = QPushButton("✕")
        button_close.setFixedSize(30, 30)
        button_close.setStyleSheet("""
            QPushButton {
                background: #fca5a5;
                border: none;
                border-radius: 8px;
                color: #991b1b;
                font-weight: bold;
            }
        """)

        title_buttons.addWidget(self.botao_logs)
        title_buttons.addWidget(button_min)
        title_buttons.addWidget(button_close)
        row_title.addLayout(title_buttons)

        layout_principal.addLayout(row_title)

        # =====================================================
        # ÁREA DA URL
        # =====================================================

        layout_url = QHBoxLayout()
        layout_url.setSpacing(10)

        self.campo_url = QLineEdit()
        self.campo_url.setPlaceholderText(
            "https://music.youtube.com/playlist?list=..."
        )
        self.campo_url.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                border: 1px solid #d1d5db;
                padding: 10px 12px;
                font-size: 14px;
            }
        """)

        self.botao_analisar = QPushButton("Analisar")
        self.botao_analisar.setMinimumWidth(110)
        self.botao_analisar.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 8px;
            }
        """)

        layout_url.addWidget(self.campo_url)
        layout_url.addWidget(self.botao_analisar)

        layout_principal.addLayout(layout_url)

        # =====================================================
        # CORPO PRINCIPAL DA JANELA
        # =====================================================

        layout_corpo = QHBoxLayout()
        layout_corpo.setSpacing(16)
        layout_corpo.setContentsMargins(0, 0, 0, 0)

        self.container_conteudo = QWidget()
        self.container_conteudo.setObjectName("containerConteudo")
        self.container_conteudo.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )
        self.container_conteudo.setStyleSheet("""
            QWidget#containerConteudo {
                background: transparent;
            }
        """)

        layout_conteudo = QVBoxLayout(self.container_conteudo)
        layout_conteudo.setContentsMargins(0, 0, 0, 0)
        layout_conteudo.setSpacing(10)

        self.painel_direito = QWidget()
        self.painel_direito.setObjectName("painelDireito")
        self.painel_direito.setFixedWidth(290)
        self.painel_direito.setStyleSheet("""
            QWidget#painelDireito {
                background: transparent;
            }
        """)

        layout_direito = QVBoxLayout(self.painel_direito)
        layout_direito.setContentsMargins(0, 0, 0, 0)
        layout_direito.setSpacing(12)

        layout_corpo.addWidget(self.container_conteudo, stretch=3)
        layout_corpo.addWidget(self.painel_direito, stretch=0)

        layout_principal.addLayout(layout_corpo)

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
            font-weight: 600;
            color: #4b5563;
        """)

        layout_cabecalho_videos.addWidget(
            self.label_selecionados
        )

        layout_conteudo.addLayout(
            layout_cabecalho_videos
        )

        # =====================================================
        # CONTROLES DE SELEÇÃO
        # =====================================================

        layout_selecao = QHBoxLayout()

        self.botao_selecionar_todos = QPushButton(
            "Selecionar todos"
        )
        self.botao_selecionar_todos.setStyleSheet("""
            QPushButton {
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 7px 12px;
            }
        """)

        self.botao_desmarcar_todos = QPushButton(
            "Desmarcar todos"
        )
        self.botao_desmarcar_todos.setStyleSheet("""
            QPushButton {
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 7px 12px;
            }
        """)

        layout_selecao.addWidget(
            self.botao_selecionar_todos
        )

        layout_selecao.addWidget(
            self.botao_desmarcar_todos
        )

        layout_selecao.addStretch()

        layout_conteudo.addLayout(
            layout_selecao
        )

        # =====================================================
        # LISTA DE VÍDEOS
        # =====================================================

        self.scroll_videos = QScrollArea()
        self.scroll_videos.setWidgetResizable(True)
        self.scroll_videos.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)

        self.container_videos = QWidget()

        self.layout_videos = QVBoxLayout(self.container_videos)
        self.layout_videos.setAlignment(Qt.AlignTop)
        self.layout_videos.setSpacing(8)

        self.scroll_videos.setWidget(self.container_videos)

        layout_conteudo.addWidget(self.scroll_videos, stretch=1)

        # =====================================================
        # CONFIGURAÇÕES DO PAINEL DIREITO
        # =====================================================

        painel_config = QWidget()
        painel_config.setObjectName("painelConfig")
        painel_config.setStyleSheet("""
            QWidget#painelConfig {
                background: #f8fafc;
                border: 1px solid #dfe7ee;
                border-radius: 12px;
            }
        """)

        layout_painel_config = QVBoxLayout(painel_config)
        layout_painel_config.setContentsMargins(12, 12, 12, 12)
        layout_painel_config.setSpacing(10)

        label_config = QLabel("Configurações")
        label_config.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout_painel_config.addWidget(label_config)

        layout_pasta = QVBoxLayout()
        layout_pasta.setSpacing(6)

        label_pasta = QLabel("Salvar em")
        label_pasta.setStyleSheet("font-size: 12px; color: #4b5563;")

        self.campo_pasta = QLineEdit()
        self.campo_pasta.setText(self.pasta_destino)
        self.campo_pasta.setPlaceholderText("Selecione a pasta...")
        self.campo_pasta.setStyleSheet("""
            QLineEdit {
                background: #ffffff;
                border: 1px solid #d1d5db;
                padding: 8px 10px;
            }
        """)

        self.botao_pasta = QPushButton("Selecionar")
        self.botao_pasta.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 600;
            }
        """)

        layout_pasta.addWidget(label_pasta)
        layout_pasta.addWidget(self.campo_pasta)
        layout_pasta.addWidget(self.botao_pasta)

        layout_painel_config.addLayout(layout_pasta)

        self.label_download = QLabel("Nenhum vídeo selecionado")
        self.label_download.setStyleSheet("""
            QLabel {
                color: #374151;
                font-size: 12px;
                font-weight: 600;
            }
        """)
        self.label_download.setWordWrap(True)
        layout_painel_config.addWidget(self.label_download)

        self.barra_progresso = QProgressBar()
        self.barra_progresso.setRange(0, 100)
        self.barra_progresso.setValue(0)
        self.barra_progresso.setVisible(False)
        self.barra_progresso.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bfdbfe;
                border-radius: 6px;
                background: #e5e7eb;
                text-align: center;
            }
            QProgressBar::chunk {
                background: #2563eb;
                border-radius: 5px;
            }
        """)
        layout_painel_config.addWidget(self.barra_progresso)

        self.botao_download = QPushButton("Iniciar download")
        self.botao_download.setMinimumHeight(42)
        self.botao_download.setEnabled(False)
        self.botao_download.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background: #93c5fd;
                color: #dbeafe;
            }
        """)

        layout_painel_config.addWidget(self.botao_download)

        layout_direito.addWidget(painel_config)

        # =====================================================
        # OPÇÕES
        # =====================================================

        painel_opcoes = QWidget()
        painel_opcoes.setObjectName("painelOpcoes")
        painel_opcoes.setStyleSheet("""
            QWidget#painelOpcoes {
                background: #f8fafc;
                border: 1px solid #dfe7ee;
                border-radius: 12px;
            }
        """)

        layout_painel_opcoes = QVBoxLayout(painel_opcoes)
        layout_painel_opcoes.setContentsMargins(12, 12, 12, 12)
        layout_painel_opcoes.setSpacing(10)

        label_opcoes = QLabel("Opções")
        label_opcoes.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout_painel_opcoes.addWidget(label_opcoes)

        self.formato_global = QComboBox()
        self.formato_global.addItem("MP4", "mp4")
        self.formato_global.addItem("MP3", "mp3")
        self.formato_global.currentIndexChanged.connect(
            self.atualizar_qualidade_global
        )

        self.qualidade_global = QComboBox()
        self.atualizar_qualidade_global()

        linhas = [
            ("Formato de download", self.formato_global),
            ("Qualidade", self.qualidade_global),
        ]

        for texto, combo in linhas:
            linha = QVBoxLayout()
            linha.setSpacing(6)

            label = QLabel(texto)
            label.setStyleSheet("font-size: 12px; color: #374151;")

            combo.setStyleSheet("""
                QComboBox {
                    background: #ffffff;
                    border: 1px solid #d1d5db;
                    border-radius: 6px;
                    padding: 6px 8px;
                }
            """)

            linha.addWidget(label)
            linha.addWidget(combo)
            layout_painel_opcoes.addLayout(linha)

        layout_direito.addWidget(painel_opcoes)

        # =====================================================
        # PRO
        # =====================================================

        painel_pro = QWidget()
        painel_pro.setObjectName("painelPro")
        painel_pro.setStyleSheet("""
            QWidget#painelPro {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #dbeafe, stop:1 #e0f2fe);
                border: 1px solid #bfdbfe;
                border-radius: 12px;
            }
        """)

        layout_painel_pro = QVBoxLayout(painel_pro)
        layout_painel_pro.setAlignment(Qt.AlignCenter)
        layout_painel_pro.setContentsMargins(12, 12, 12, 12)

        badge = QLabel("✦")
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet("font-size: 28px; color: #f59e0b;")

        pro_label = QLabel("Atualize para o Pro")
        pro_label.setAlignment(Qt.AlignCenter)
        pro_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #1f2937;")

        pro_sub = QLabel("Mais velocidade, sem limites,\ne recursos extras.")
        pro_sub.setAlignment(Qt.AlignCenter)
        pro_sub.setStyleSheet("font-size: 11px; color: #475569; line-height: 1.3;")

        botao_pro = QPushButton("Saiba mais")
        botao_pro.setStyleSheet("""
            QPushButton {
                background: #ffffff;
                color: #1d4ed8;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: bold;
            }
        """)

        layout_painel_pro.addWidget(badge)
        layout_painel_pro.addWidget(pro_label)
        layout_painel_pro.addWidget(pro_sub)
        layout_painel_pro.addWidget(botao_pro)

        layout_direito.addWidget(painel_pro)

        layout_direito.addStretch()

        self.area_anuncios_inferior = QWidget()
        self.area_anuncios_inferior.setVisible(False)

        # =====================================================
        # EVENTOS
        # =====================================================

        self.botao_logs.clicked.connect(
            self.abrir_logs
        )

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

    def abrir_logs(self):

        self.log_dialog.show()
        self.log_dialog.raise_()
        self.log_dialog.activateWindow()

    def atualizar_qualidade_global(self):

        formato = self.formato_global.currentData() or "mp4"

        self.qualidade_global.blockSignals(True)
        self.qualidade_global.clear()

        if formato == "mp3":
            self.qualidade_global.addItem("Melhor áudio", "best")
            for valor, texto in [
                ("320", "320 kbps"),
                ("192", "192 kbps"),
                ("128", "128 kbps"),
            ]:
                self.qualidade_global.addItem(texto, valor)
        else:
            self.qualidade_global.addItem("Melhor disponível", "best")
            for valor in ["2160", "1440", "1080", "720", "480", "360", "240"]:
                self.qualidade_global.addItem(f"{valor}p", valor)

        self.qualidade_global.setCurrentIndex(0)
        self.qualidade_global.blockSignals(False)

    def _carregar_area_monetizacao(
        self,
        view,
        titulo,
        descricao,
    ):

        if self.monetization_url:

            view.setUrl(
                QUrl(
                    self.monetization_url
                )
            )

            return

        mensagem = html.escape(
            descricao
        )

        view.setHtml(
            f"""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    html, body {{
                        margin: 0;
                        width: 100%;
                        height: 100%;
                        font-family: Arial, sans-serif;
                        background: linear-gradient(135deg, #f7f9fc 0%, #eef3f8 100%);
                        color: #2d3748;
                    }}
                    .wrap {{
                        box-sizing: border-box;
                        width: 100%;
                        height: 100%;
                        padding: 16px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }}
                    .card {{
                        width: 100%;
                        height: 100%;
                        border: 1px dashed #b8c3d1;
                        border-radius: 12px;
                        background: rgba(255, 255, 255, 0.9);
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        text-align: center;
                        padding: 20px;
                        box-sizing: border-box;
                    }}
                    .title {{
                        font-size: 18px;
                        font-weight: 700;
                        margin-bottom: 8px;
                    }}
                    .text {{
                        font-size: 13px;
                        line-height: 1.5;
                        max-width: 620px;
                    }}
                </style>
            </head>
            <body>
                <div class="wrap">
                    <div class="card">
                        <div class="title">{html.escape(titulo)}</div>
                        <div class="text">{mensagem}</div>
                    </div>
                </div>
            </body>
            </html>
            """
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

        formato = self.formato_global.currentData() or "mp4"
        qualidade = self.qualidade_global.currentData() or "best"

        for video in selecionados:
            video.selected_format = formato
            video.selected_quality = qualidade

        self.download_worker = DownloadWorker(
            selecionados,
            pasta,
            formato=formato,
            qualidade=qualidade,
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