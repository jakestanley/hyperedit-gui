import time
import vlc

from pathlib import Path

_SINGLETON = None

class PlayerService:
    def __init__(self):
        if _SINGLETON is not None:
            raise Exception("PlayerService MUST not be instantiated more than once")
        pass

    # TODO: use a thread
    def Preview(self, video_path, srts):
        video_path = Path(video_path)
        player = vlc.MediaPlayer(str(video_path))

        player.play()
        for srt in srts:
            start = srt[1]
            end = srt[2]
            duration = end - start
            player.set_time(int(start * 1000))
            time.sleep(duration)

        player.stop()

def GetPlayerService():
    global _SINGLETON
    if _SINGLETON is None:
        _SINGLETON = PlayerService()
    return _SINGLETON
