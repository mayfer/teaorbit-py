#!/usr/bin/env python

# disable .pyc files
import sys
sys.dont_write_bytecode = True

import daemon
from optparse import make_option, OptionParser
from messenger import Connection
import os
import sys

import tornado
from tornado import httpserver
from sockjs.tornado import SockJSRouter, SockJSConnection

STATIC_URL = '/static/'
FILE_ROOT = os.path.dirname(__file__)



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("templates/index.html", STATIC_URL=STATIC_URL)

class ChatroomHandler(tornado.web.RequestHandler):
    def get(self, room_name):
        self.render("templates/index.html", STATIC_URL=STATIC_URL, room_name=room_name)

def runloop(addr, port, xheaders, no_keep_alive, use_reloader, daemonize=False):
    router = SockJSRouter(Connection, '/updates')
    handlers = router.urls + [
        (r'/', MainHandler),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(FILE_ROOT, 'static/')}),
        (r'/(?P<room_name>.*)', ChatroomHandler),
    ]
    tornado_app = tornado.web.Application(handlers)

    # start tornado web server in single-threaded mode
    # instead auto pre-fork mode with bind/start.
    http_server = httpserver.HTTPServer(tornado_app, xheaders=xheaders, no_keep_alive=no_keep_alive)
    http_server.listen(int(port), address=addr)

    main_loop = tornado.ioloop.IOLoop.instance()

    if use_reloader:
        # Use tornado reload to handle IOLoop restarting.
        from tornado import autoreload
        autoreload.start()
        for (path, dirs, files) in os.walk(os.path.join(FILE_ROOT, 'templates')):
            for item in files:
                tornado.autoreload.watch(os.path.join(path, item))

    try:
        print "*** [success] Runing on :{port}".format(port=port)
        if daemonize is True:
            log = open('tornado.log', 'a+')
            ctx = daemon.DaemonContext(stdout=log, stderr=log, working_directory='.')
            ctx.open()
        main_loop.start()

    except KeyboardInterrupt:
        print "Stopped"
        sys.exit(0)


def init():
    option_list = (
        make_option('--reload', action='store_true',
            dest='use_reloader', default=True,
            help="Tells Tornado to use auto-reloader."),
        make_option('--admin', action='store_true',
            dest='admin_media', default=False,
            help="Serve admin media."),
        make_option('--adminmedia', dest='admin_media_path', default='',
            help="Specifies the directory from which to serve admin media."),
        make_option('--noxheaders', action='store_false',
            dest='xheaders', default=True,
            help="Tells Tornado to NOT override remote IP with X-Real-IP."),
        make_option('--nokeepalive', action='store_true',
            dest='no_keep_alive', default=False,
            help="Tells Tornado to NOT keep alive http connections."),
        make_option('--daemonize', action='store_true',
            dest='daemonize', default=False,
            help="Run tornado in the background."),
        make_option('--port', action='store',
            dest='port', default='8001',
            help="Port to listen."),
    )
    parser = OptionParser(option_list=option_list)
    (options, args) = parser.parse_args()

    help = "Starts a Tornado Web."
    addr = '0.0.0.0'

    if not options.port.isdigit():
        raise CommandError("%r is not a valid port number." % port)

    runloop(addr, options.port, options.xheaders, options.no_keep_alive, options.use_reloader, options.daemonize)


if __name__ == "__main__":
    init()

