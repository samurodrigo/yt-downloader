class FormatManager:

    @staticmethod
    def get_video_qualities(formats):

        qualities = set()

        for formato in formats:

            height = formato.get("height")

            if not height:
                continue

            # Precisamos de um stream que contenha vídeo
            if formato.get("vcodec") == "none":
                continue

            qualities.add(height)

        return sorted(
            qualities,
            reverse=True
        )

    @staticmethod
    def get_audio_qualities(formats):

        qualities = set()

        for formato in formats:

            # Ignorar streams sem áudio
            if formato.get("acodec") == "none":
                continue

            abr = formato.get("abr")

            if abr:
                qualities.add(
                    round(abr)
                )

        return sorted(
            qualities,
            reverse=True
        )

    @staticmethod
    def format_video_quality(height):

        if height >= 2160:
            return f"{height}p (4K)"

        if height >= 1440:
            return f"{height}p (2K)"

        return f"{height}p"

    @staticmethod
    def format_audio_quality(abr):

        return f"{abr} kbps"