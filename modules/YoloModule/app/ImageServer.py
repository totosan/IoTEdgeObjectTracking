# Base on work from https://github.com/Bronkoknorb/PyImageStream
import trollius as asyncio
import tornado.ioloop
import tornado.web
import tornado.websocket
import threading
import base64
import json
import os

try:
    import ptvsd
    __myDebug__ = True 
    ptvsd.enable_attach(('0.0.0.0',  5678))   
except ImportError:
    __myDebug__ = False
    
class ImageStreamHandler(tornado.websocket.WebSocketHandler):

    def initialize(self, videoCapture):
        self.clients = []
        self.videoCapture = videoCapture
        self.edit = videoCapture.RulesEdit

    def check_origin(self, origin):
        return True

    def open(self):
        self.clients.append(self)
        print("Image Server Connection::opened")

    def on_message(self, message):
        msg = json.loads(message);
        if msg['type'] == 'command':
            if 'name' in msg['payload'] and msg['payload']['name'] == 'next':
                self.send_image(self.videoCapture)
                self.rules_edit_mode(self.videoCapture)
            if 'name' in msg['payload'] and msg['payload']['name'] == 'save' and self.edit:
                print(f"Saved: {msg['payload']['content']}")
            if 'name' in msg['payload'] and msg['payload']['name'] == 'initLines':
                print(f"that are the lines: {msg['payload']['content']}")
                self.videoCapture.linesRaw = msg['payload']['content']
        if msg['type'] == 'report':
            self.get_report(msg)

    def on_close(self):
        self.clients.remove(self)
        print("Image Server Connection::closed")
        
    def send_image(self, capture):
        newMsg = {'type': 'image','payload': None}
        frame = capture.get_display_frame()
        if frame != None:
            encoded = base64.b64encode(frame)
            newMsg["payload"] = encoded.decode('ascii')
            self.write_message(json.dumps(newMsg), binary=False)       
            
    def rules_edit_mode(self, capture):
        if not self.edit == capture.RulesEdit:
            rulesEdit = {'ModeName':'RulesEdit','Value':capture.RulesEdit}
            newMsg = {'type':'mode','payload':rulesEdit}
            self.write_message(json.dumps(newMsg), binary=False)
            print(f"Send RulesEdit mode: {capture.RulesEdit}")
    
    def get_report(self, message):
        self.edit = bool(message['payload']['RulesEdit'])

class ImageServer(threading.Thread):

    def __init__(self, port, videoCapture):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.port = port
        self.videoCapture = videoCapture
        self.edit = False
    
    def get_edit(self):
        return self._edit
    
    def set_edit(self,value):
        self._edit = value
    
    edit = property(get_edit, set_edit)
    
    def run(self):
        print('ImageServer::run() : Started Image Server')
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            indexPath = os.path.join(os.path.dirname(
                os.path.realpath(__file__)), 'templates')
            app = tornado.web.Application([
                (r"/stream", ImageStreamHandler,
                 {'videoCapture': self.videoCapture}),
                (r"/(.*)", tornado.web.StaticFileHandler,
                 {'path': indexPath, 'default_filename': 'index.html'})
            ])
            app.listen(self.port)
            print('ImageServer::Started.')

            tornado.ioloop.IOLoop.instance().start()
        except Exception as e:
            print('ImageServer::exited run loop. Exception - ' + str(e))

    def close(self):
        print('ImageServer::close()')
