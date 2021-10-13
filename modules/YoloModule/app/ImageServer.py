# Base on work from https://github.com/Bronkoknorb/PyImageStream
import trollius as asyncio
import tornado.ioloop
import tornado.web
import tornado.websocket
import threading
import base64
import json
import os


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
            if msg['payload'] == 'next':
                self.send_image(self.videoCapture)
                self.rules_edit_mode(self.videoCapture)

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
            self.edit = capture.RulesEdit
            rulesEdit = {'ModeName':'RulesEdit','Value':self.edit}
            newMsg = {'type':'mode','payload':rulesEdit}
            self.write_message(json.dumps(newMsg), binary=False) 


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
