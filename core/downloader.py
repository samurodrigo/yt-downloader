from pathlib import Path

import yt_dlp


class YouTubeDownloader:

    def __init__(self):

        self.base_dir = (
            Path(__file__)
            .resolve()
            .parent
            .parent
        )

        self.ffmpeg_dir = (
            self.base_dir / "bin"
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

            qualidade = (
                video.selected_quality
            )

            if qualidade == "best":

                formato = (
                    "bestvideo+bestaudio/"
                    "best"
                )

            else:

                formato = (
                    f"bestvideo[height<={qualidade}]"
                    "+bestaudio/"
                    f"best[height<={qualidade}]"
                )

            postprocessors = []

        # =====================================================
        # OPÇÕES DO YT-DLP
        # =====================================================

        opcoes = {

            "format": formato,

            "outtmpl": str(
                pasta / "%(title)s.%(ext)s"
            ),

            "ffmpeg_location": str(
                self.ffmpeg_dir
            ),

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