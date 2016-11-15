"""
alias penin='kill -SIGUSR1 $(ps a | grep "python3 sync" | head -1 | cut -d " " -f1)'
alias penout='kill -SIGUSR2 $(ps a | grep "python3 sync" | head -1 | cut -d " " -f1)'
"""
from threading import Thread
from flask import Flask, request
import time
from notifier import Notifier
import json
from syncronize import Syncronize
import os, sys
import threading
import signal
from queue import Queue
import datetime
import argparse

poll_count = 0

def main():
    parser = argparse.ArgumentParser()
    #parser.add_argument("--ipython", help="run ipython",
    #                action="store_true")
    parser.add_argument("list_id", help="Youtube playlist id")
    parser.add_argument("pendrive_dir", help="Youtube playlist id")
    parser.add_argument("device_name", help="Youtube playlist id")
    #subparsers = parser.add_subparsers(help='sub-command help')
    #subparsers.add_parser('pid', help="get pid of running instance").set_defaults(func=cmd_pid)
    args = parser.parse_args()
    #if hasattr(args, 'func'):
    #    args.func(args)
    #    sys.exit()
    LIST_ID = args.list_id

    def getScriptPath():
        return os.path.dirname(os.path.realpath(sys.argv[0]))
    
    PORT = 8181
    PENDRIVE_DIR = args.pendrive_dir
    DEVICE_NAME = args.device_name

    store = {"sync_status": 'listo', "penin": False, "todownload": '', 
            "current": {"index":0, "filename":"pepe", "id":"adsfdf"}}

    def oncalculated(todownload):
        store["todownload"] = len(todownload) + 1
        store["sync_status"] = "downloading"
        global poll_count
        poll_count += 1

    def ondownloading(index, filename, id):
        store["current"] = {"index": index, "filename": filename, "id": id}
        store["todownload"] -= 1
        global poll_count
        poll_count += 1

    def onend(extract_on_end=False, cancelled=False, exception=None):
        print("onend")
        store["sync_status"] = 'listo'
        store["todownload"] = 0
        store["cancelled"] = cancelled
        if not cancelled:
            store["current"] = {}
        if extract_on_end:
            #os.system("sudo eject /dev/disk/by-label/luks")
            print("PLEASE EJECT")
        store["exception"] = exception
        if not exception and not cancelled:
            store['lastsync'] = datetime.datetime.now().strftime("%H:%M:%S")
        global poll_count
        poll_count += 1


    s = Syncronize(PENDRIVE_DIR, LIST_ID, None, ondownloading, oncalculated, onend)
    from functools import partial
    def onchange(isattached):
        print("hi")
        store['penin'] = isattached
        global poll_count
        poll_count += 1
    notifier = Notifier(DEVICE_NAME, onchange)
    signal.signal(signal.SIGUSR1, lambda sig, frame: notifier.simulate(True))
    signal.signal(signal.SIGUSR2, lambda sig, frame: notifier.simulate(False))
    store['penin'] = notifier.isattached()
    threading.Thread(target=notifier.run).start()
    #s.run()
    app = Flask(__name__)

    @app.route('/')
    def root():
        return "welcome :D"

    @app.route('/sync')
    def sync():
        if store["sync_status"] == "listo":
            if store['penin']:
                if notifier.isattached():
                    store["sync_status"] == "calculating"
                    store["cancelled"] = False
                    global poll_count
                    poll_count += 1
                    t1 = threading.Thread(target=s.run)
                    t1.start()
                    return 'OK'
                else:
                    print("NOTIFIER ONREMOVE FAIL")
                    store['penin'] = False
                    return 'El pendrive no esta!'
            else:
                return 'El pendrive no esta!'
        else:
            return 'No estoy listo!'

    @app.route('/stop')
    def stop():
        if store["sync_status"] != "listo":
            s.stop_downloading()
        return 'OK'

    @app.route('/extract')
    def extract():
        if store["penin"] == True:
            s.stop_downloading(extract_on_end=True)

    import _threading_local
    @app.route('/poll')
    def poll():
        #queues = _threading_local.current_thread().ident)
        pc = request.args.get("poll_count")
        if not pc:
            return json.dumps({'error': 'need poll_count'})
        n = int(pc)
        while n == poll_count:
            time.sleep(0.5)
        s = store.copy()
        s.update({'poll_count': poll_count})
        return json.dumps(s)

    app.run(host="0.0.0.0", port=PORT, use_reloader=False, debug=False, threaded=True)
if __name__ == "__main__":
    main()