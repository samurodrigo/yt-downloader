import sys
from pathlib import Path

import yt_dlp


class YouTubeDownloader:

    def __init__(self):

        self.base_dir = self._resolver_base_dir()

        self.ffmpeg_dir = (
            self.base_dir / "bin"
        )

        self.ffmpeg_path = (
            self.ffmpeg_dir / "ffmpeg.exe"
        )

    def _resolver_base_dir(self):

        if getattr(sys, "frozen", False):

            meipass = getattr(
                sys,
                "_MEIPASS",
                None
            )

            if meipass:

                return Path(meipass)

            return Path(
                sys.executable
            ).resolve().parent

        return (
            Path(__file__)
            .resolve()
            .parent
            .parent
        )

    def baixar(
        self,
        video,
        pasta_destino,
        progress_hook=None,
        logger=None,
    ):

        pasta = Path(
            pasta_destino
        )

        pasta.mkdir(
            parents=True,
            exist_ok=True
        )

        # =====================================================
        # MP3
        # =====================================================

        if video.selected_format == "mp3":

            formato = (
                "bestaudio/best"
            )

            saida_extensao = "mp3"

            qualidade = (
                video.selected_quality
            )

            if qualidade == "best":

                bitrate = "192"

            else:

                bitrate = str(
                    qualidade
                )

            postprocessors = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": bitrate,
                }
            ]

        # =====================================================
        # MP4
        # =====================================================

        else:

            saida_extensao = "mp4"

            qualidade = (
                video.selected_quality
            )

            if qualidade == "best":

                formato = (
                    "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                    "best[ext=mp4]"
                )

            else:

                formato = (
                    f"bestvideo[height<={qualidade}][ext=mp4]"
                    "+bestaudio[ext=m4a]/"
                    f"best[height<={qualidade}][ext=mp4]"
                )

            postprocessors = []

        # =====================================================
        # OPÇÕES DO YT-DLP
        # =====================================================

        opcoes = {

            "format": formato,

            "outtmpl": str(
                pasta / f"%(title)s.{saida_extensao}"
            ),

            "ffmpeg_location": str(
                self.ffmpeg_path
                if self.ffmpeg_path.exists()
                else self.ffmpeg_dir
            ),

            "merge_output_format": "mp4",

            "noplaylist": True,

            "postprocessors": postprocessors,

            "quiet": True,

            "no_warnings": True,
        }

        # Progress hook
        if progress_hook:

            opcoes["progress_hooks"] = [
                progress_hook
            ]

        # Logger
        if logger:

            opcoes["logger"] = logger

        # =====================================================
        # DOWNLOAD
        # =====================================================

        with yt_dlp.YoutubeDL(
            opcoes
        ) as ydl:

            resultado = ydl.download([
                video.url
            ])

        return resultado