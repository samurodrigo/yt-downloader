from core.downloader import YouTubeDownloader
from models.video import Video


url = input(
    "Cole a URL de um vídeo do YouTube: "
).strip()


video = Video(
    id="teste",
    title="Teste",
    url=url,
)

video.selected_format = "mp4"
video.selected_quality = "best"


downloader = YouTubeDownloader()


def progresso(dados):

    status = dados.get(
        "status"
    )

    if status == "downloading":

        percentual = dados.get(
            "_percent_str",
            "?"
        )

        velocidade = dados.get(
            "_speed_str",
            "?"
        )

        eta = dados.get(
            "_eta_str",
            "?"
        )

        print(
            f"\r"
            f"{percentual} "
            f"| {velocidade} "
            f"| ETA {eta}",
            end="",
            flush=True
        )

    elif status == "finished":

        print()
        print(
            "Download concluído."
        )


resultado = downloader.baixar(
    video,
    "downloads",
    progress_hook=progresso,
)


print()
print(
    "Resultado:",
    resultado
)