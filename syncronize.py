from downloader import Downloader, StopException
from youtube_api import Youtube_API
from os import walk
import os
import shutil
import traceback
class Syncronize():
    def __init__(self, path, playlistId, onprogress, ondownloading, oncalculated, onend, 
                 extract_on_end=False):
        self.todownload = []
        self.toremove = []
        self.path = path
        self.playlistId = playlistId
        self.ondownloading = ondownloading
        self.oncalculated = oncalculated
        self.onend = onend
        self.tmppath = "/tmp"
        self.ya = Youtube_API('')
        self.downloader = Downloader(self.tmppath)
        self.extract_on_end = extract_on_end

    def calculate_missing(self):
        playlist = self.ya.get_playlist(self.playlistId)
        _, _, filenames = next(walk(self.path), (None, None, []))
        to_filename = lambda t_id: "%(title)s-%(id)s.%(ext)s" % {"ext":"mp3", "title": t_id[0], "id": t_id[1]}
        id_from_fn = lambda filename: ".".join(filename.split('.')[:-1])[-11:]
        self.todownload = [t_id for t_id in playlist if to_filename(t_id) not in filenames]
        self.toremove = [fn for fn in filenames if id_from_fn(fn) not in [t_id[1] for t_id in playlist]]


    def run(self):
        ex = None
        cancelled = False
        try:
            self.calculate_missing()
            self.oncalculated(self.todownload)
            for filename in self.toremove:
                print("Removing: {}".format(os.path.join(self.path, filename)))
                os.remove(os.path.join(self.path, filename))
            for index, (filename, id) in enumerate(self.todownload):
                self.ondownloading(index, filename, id)
                try:
                    out_path = self.downloader.download(id)
                except StopException:
                    cancelled = True
                    self.downloader.stop = False
                    break
                shutil.move(out_path, self.path)
        except Exception as e:
            ex = (e.__class__.__name__, e.args)
            traceback.print_exc()
        self.onend(extract_on_end=self.extract_on_end, cancelled=cancelled, exception=ex)

    def stop_downloading(self):
        self.downloader.stop = True

if __name__ == "__main__":
    pass