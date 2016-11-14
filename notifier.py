import pyinotify
import os

class Notifier(): #todo subclass!!
    def __init__(self, devname, onchange):
        wm = pyinotify.WatchManager()  # Watch Manager
        mask = pyinotify.IN_DELETE | pyinotify.IN_CREATE  # watched events
        self.devname = devname
        self.simulation_status = None
        self.onchange = onchange

        class EventHandler(pyinotify.ProcessEvent):
            def process_IN_CREATE(self, event):
                print("Creating:", event.pathname)
                if event.name == devname:
                    self.simulation_status = None
                    onchange(True)

            def process_IN_DELETE(self, event):
                print("Removing:", event.pathname)
                if event.name == devname:
                    self.simulation_status = None
                    onchange(False)

        handler = EventHandler()
        self.notifier = pyinotify.Notifier(wm, handler)
        wdd = wm.add_watch('/dev/disk/by-label/', mask, rec=True)

    def isattached(self):
        if self.simulation_status != None:
            return self.simulation_status
        return os.path.exists(os.path.join('/dev/disk/by-label/', self.devname))

    def simulate(self, isattached):
        self.simulation_status = isattached
        self.onchange(isattached)

    def run(self):
        self.notifier.loop()

if __name__ == '__main__':
    notifier = Notifier('luks', lambda x: print(x))
    notifier.run()