def my_hook(d):
    if d['status'] == 'finished':
        pass
    else:
        print(d['filename'], d['_percent_str'], d['_eta_str'])

class MyLogger:
    def debug(self, msg):
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
  