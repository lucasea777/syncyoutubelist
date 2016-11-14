from __future__ import unicode_literals
import youtube_dl, os

class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

class StopException(BaseException):
    pass

class Downloader():
    def __init__(self, path):
        self.stop = False
        self.path = path
        self.ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3'
                }],
                'logger': MyLogger(),
                'progress_hooks': [self._my_hook],
                'outtmpl': os.path.join(path, "%(title)s-%(id)s.%(ext)s")
            }

    def _my_hook(self, d):
        #print(d)
        if self.stop:
            raise StopException()
        if d['status'] == 'finished':
            print('Done downloading, now converting ...')


    def download(self, id):
        """
        >>> download()
        """
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            #r = ydl.download([id])
            r = ydl.extract_info(id)
            r.update({"ext":"mp3"})
            return os.path.join(self.path, "%(title)s-%(id)s.%(ext)s" % r)

if __name__ == "__main__":
    import doctest
    import threading
    downloader = Downloader("/tmp/v")
    def th():
        r = downloader.download("BmTvoWWZLbA")
    t1 = threading.Thread(target=th)
    t1.start()
    #doctest.testmod()