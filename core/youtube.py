import yt_dlp

from urllib.parse import urlparse, parse_qs

from models.video import Video


class YouTubeLogger:

    def debug(self, mensagem):
        pass

    def info(self, mensagem):
        pass

    def warning(self, mensagem):
        pass

    def error(self, mensagem):
        pass


class YouTubeAnalyzer:

    def __init__(self):

        self.ydl_options = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "ignoreerrors": True,
            "logger": YouTubeLogger(),
        }

    # =========================================================
    # ANALISAR URL
    # =========================================================

    def analisar(self, url: str):

        url = url.strip()

        # -----------------------------------------------------
        # Detectar playlist
        # -----------------------------------------------------

        playlist_id = self._obter_playlist_id(
            url
        )

        if playlist_id:

            return self._analisar_playlist(
                playlist_id
            )

        # -----------------------------------------------------
        # Vídeo individual
        # -----------------------------------------------------

        return self._analisar_video_individual(
            url
        )

    # =========================================================
    # OBTER ID DA PLAYLIST
    # =========================================================

    def _obter_playlist_id(
        self,
        url
    ):

        try:

            parsed = urlparse(
                url
            )

            parametros = parse_qs(
                parsed.query
            )

            playlist_ids = parametros.get(
                "list"
            )

            if playlist_ids:

                return playlist_ids[0]

        except Exception:

            pass

        return None

    # =========================================================
    # ANALISAR PLAYLIST
    # =========================================================

    def _analisar_playlist(
        self,
        playlist_id
    ):

        playlist_url = (
            "https://www.youtube.com/playlist?list="
            + playlist_id
        )

        opcoes = {
            **self.ydl_options,

            # Apenas lista os vídeos.
            "extract_flat": True,

            # Garante que a playlist inteira
            # seja considerada.
            "noplaylist": False,
        }

        with yt_dlp.YoutubeDL(
            opcoes
        ) as ydl:

            info = ydl.extract_info(
                playlist_url,
                download=False
            )

        if not info:

            raise Exception(
                "Não foi possível analisar "
                "a playlist."
            )

        videos = []

        entradas = info.get(
            "entries",
            []
        )

        total = len(
            entradas
        )

        print(
            f"Playlist encontrada: "
            f"{total} item(ns)"
        )

        # =====================================================
        # ANALISAR CADA ITEM
        # =====================================================

        for indice, item in enumerate(
            entradas,
            start=1
        ):

            if not item:

                print(
                    f"[{indice}/{total}] "
                    f"Item indisponível."
                )

                continue

            video_id = item.get(
                "id"
            )

            if not video_id:

                continue

            print(
                f"[{indice}/{total}] "
                f"Analisando vídeo {video_id}..."
            )

            try:

                video = self._obter_detalhes_video(
                    video_id
                )

                if video:

                    videos.append(
                        video
                    )

                    print(
                        f"[{indice}/{total}] "
                        f"OK: {video.title}"
                    )

            except Exception as erro:

                print(
                    f"[{indice}/{total}] "
                    f"Ignorado: {erro}"
                )

        return {
            "type": "playlist",

            "title": info.get(
                "title",
                "Playlist"
            ),

            "channel": info.get(
                "uploader"
            ),

            "videos": videos,
        }

    # =========================================================
    # ANALISAR VÍDEO INDIVIDUAL
    # =========================================================

    def _analisar_video_individual(
        self,
        url
    ):

        video = self._obter_detalhes_url(
            url
        )

        if not video:

            raise Exception(
                "Não foi possível obter "
                "as informações do vídeo."
            )

        return {
            "type": "video",

            "title": video.title,

            "channel": video.channel,

            "videos": [
                video
            ],
        }

    # =========================================================
    # OBTER DETALHES PELO ID
    # =========================================================

    def _obter_detalhes_video(
        self,
        video_id
    ):

        url = (
            "https://www.youtube.com/watch?v="
            + video_id
        )

        return self._obter_detalhes_url(
            url
        )

    # =========================================================
    # OBTER DETALHES DE UM VÍDEO
    # =========================================================

    def _obter_detalhes_url(
        self,
        url
    ):

        opcoes = {
            **self.ydl_options,

            # Aqui precisamos dos formatos completos.
            "extract_flat": False,

            # Não queremos que o yt-dlp
            # tente interpretar uma playlist.
            "noplaylist": True,
        }

        try:

            with yt_dlp.YoutubeDL(
                opcoes
            ) as ydl:

                info = ydl.extract_info(
                    url,
                    download=False
                )

            if not info:

                return None

            return self._criar_video(
                info
            )

        except Exception as erro:

            mensagem = str(
                erro
            ).lower()

            if (
                "private video" in mensagem
                or "vídeo privado" in mensagem
            ):

                print(
                    f"Vídeo privado ignorado."
                )

                return None

            if (
                "video unavailable" in mensagem
                or "video removed" in mensagem
                or "vídeo indisponível" in mensagem
                or "vídeo removido" in mensagem
            ):

                print(
                    "Vídeo indisponível ignorado."
                )

                return None

            raise

    # =========================================================
    # CRIAR OBJETO VIDEO
    # =========================================================

    def _criar_video(
        self,
        info
    ):

        return Video(

            id=info.get(
                "id",
                ""
            ),

            title=info.get(
                "title",
                "Sem título"
            ),

            url=(
                info.get(
                    "webpage_url"
                )
                or info.get(
                    "original_url"
                )
                or ""
            ),

            channel=info.get(
                "uploader"
            ),

            duration=info.get(
                "duration"
            ),

            thumbnail=info.get(
                "thumbnail"
            ),

            formats=info.get(
                "formats",
                []
            ),
        )