## @package PyHoot.__main__
# Main file
## @file __main__.py Implementation of @ref PyHoot.__main__

import argparse
import logging
import os
import signal
import socket

from . import base, compat, constants, server


def parse_args():
    """parse argu"""
    LOG_STR_LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }
    parser = argparse.ArgumentParser(
        prog="Package Name",
        description=(
            'Package description.'
        ),
    )
    parser.add_argument(
        "--address",
        default=["%s:80" % socket.gethostbyname(socket.gethostname())],
        nargs="+",
        help="""This argument is the address or addresses we will connect to.
         Default %(default)s""",
    )
    parser.add_argument(
        "--buff-size",
        default=constants.BUFF_SIZE,
        type=int,
        help="The buff size for each time. Default %(default)d"
    )
    parser.add_argument(
        "--base",
        default=os.path.dirname(__file__),
        type=str,
        help="The base directory"
    )
    c = []
    if os.name != 'nt':
        c.append("poll")
    c.append("select")
    parser.add_argument(
        "--io-mode",
        default=c[0],
        choices=c,
        help="""The Asynchronous I/O protocol that will be used.
        Default %(default)s"""
    )
    parser.add_argument(
        '--log-level',
        dest='log_level_str',
        default='INFO',
        choices=LOG_STR_LEVELS.keys(),
        help='The log level that will be used for logging',
    )
    parser.add_argument(
        '--log-file',
        dest='log_file',
        metavar='FILE',
        required=False,
        help='The logfile to write to, otherwise will write to console.',
    )
    args = parser.parse_args()
    args.log_level = LOG_STR_LEVELS[args.log_level_str]
    args.base = os.path.normpath(os.path.realpath(args.base))
    address_list = []
    for a in args.address:
        a = a.split(":")
        if len(a) != 2:
            raise ValueError(
                """The argument '--address' needs to be in the next format:
                    server_address:server_port"""
            )
        address_list.append((a[0], int(a[1])),)
    args.address = address_list
    return args


def main():
    """This is the main function: Parsing arguments, setting up servers and
     starting them"""
    compat.__init__()
    args = parse_args()
    close_file = []
    if args.log_file:
        close_file.append(open(args.log_file, 'a'))
        logger = base.setup_logging(
            stream=close_file[0],
            level=args.log_level,
        )
    else:
        logger = base.setup_logging(
            level=args.log_level,
        )
    logger.info("Parsed arguments and created logger")
    Server = server.Server(args.buff_size, args.base, args.io_mode)

    def terminate_handler(signo, frame):
        """The settings of the signals and handlers for a nice shutdown"""
        Server.terminate()
    signal.signal(signal.SIGINT, terminate_handler)
    signal.signal(signal.SIGTERM, terminate_handler)
    for address_list in args.address:
        # FIXME: Only one server is set up, the first one
        Server.add_server(address_list)
    Server.start_server()
    for f in close_file:
        f.close()


if __name__ == "__main__":
    main()
