import argparse
import sys

from socketio.server import SocketIOServer
from konfig import Config

from marteauweb import __version__, logger
from marteauweb.wsgiapp import main as webapp
from marteau.util import (LOG_LEVELS, configure_logger, import_string,
                          redis_available)
from marteau.fixtures import get_fixtures


def main():
    parser = argparse.ArgumentParser(description='Marteau Server')
    parser.add_argument('config', help='Config file', nargs='?')
    parser.add_argument('--version', action='store_true',
                        default=False,
                        help='Displays Marteau version and exits.')
    parser.add_argument('--log-level', dest='loglevel', default='info',
                        choices=LOG_LEVELS.keys() + [key.upper() for key in
                                                     LOG_LEVELS.keys()],
                        help="log level")
    parser.add_argument('--log-output', dest='logoutput', default='-',
                        help="log output")
    parser.add_argument('--host', help='Host', default='0.0.0.0')
    parser.add_argument('--port', help='Port', type=int, default=8080)
    args = parser.parse_args()

    if args.version:
        print(__version__)
        sys.exit(0)

    if args.config is None:
        parser.print_usage()
        sys.exit(0)

    # configure the logger
    configure_logger(logger, args.loglevel, args.logoutput)

    # loading the config file
    config = Config(args.config)

    # loading the app & the queue
    global_config = {}
    if config.has_section('marteau'):
        settings = config.get_map('marteau')
    else:
        settings = {}

    # check is redis is running
    if not redis_available():
        raise IOError('Marteau needs Redis to run.')

    # loading the fixtures plugins
    for fixture in settings.get('fixtures', []):
        import_string(fixture)

    logger.info('Loaded plugins: %s' % ', '.join(get_fixtures()))

    app = webapp(global_config, **settings)
    try:
        httpd = SocketIOServer((args.host, args.port), app,
                               resource="socket.io", policy_server=False)
        logger.info('Hammer ready, at http://%s:%s. Where are the nails ?' %
                    (args.host, args.port))
        httpd.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        logger.info('Bye!')


if __name__ == '__main__':
    sys.exit(main())
