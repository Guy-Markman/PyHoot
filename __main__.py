"""main file"""
import argparse
import logging
import os
import signal

from . import base, compat, constants, server


def parse_args():
    """parse args"""
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
        default=["localhost:8080"],
        nargs="+",
        help="The address(es) we will connect to, default %(default)s",
    )
    parser.add_argument(
        "--buff-size",
        default=constants.BUFF_SIZE,
        type=int,
        help="Buff size for each time, default %(default)d"
    )
    print os.path.dirname(__file__)
    parser.add_argument(
        "--base",
        default=os.path.dirname(__file__),
        type=str,
        help="Base directory"
    )
    c = []
    if os.name != 'nt':
        c.append("poll")
    c.append("select")
    parser.add_argument(
        "--io-mode",
        default=c[0],
        choices=c,
        help="IO that will be used, default %(default)s"
    )
    parser.add_argument(
        '--log-level',
        dest='log_level_str',
        default='INFO',
        choices=LOG_STR_LEVELS.keys(),
        help='Log level',
    )
    parser.add_argument(
        '--log-file',
        dest='log_file',
        metavar='FILE',
        required=False,
        help='Logfile to write to, otherwise will log to console.',
    )
    args = parser.parse_args()
    args.log_level = LOG_STR_LEVELS[args.log_level_str]
    args.base = os.path.normpath(os.path.realpath(args.base))
    address_list = []
    for a in args.address:
        a = a.split(":")
        if len(a) != 2:
            raise ValueError(
                """--Address need to be in the next format:
                    server_address:server_port"""
            )
        address_list.append((a[0], int(a[1])),)
    args.address = address_list
    return args


def main():
    """main function. Parsing args, setting up servers and starting them"""
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
    logger.info("Parsed args and created logger")
    Server = server.Server(args.buff_size, args.base, args.io_mode)

    def terminate_handler(signo, frame):
        """Signals set and handlers for nice shutdown"""
        Server.terminate()
    signal.signal(signal.SIGINT, terminate_handler)
    signal.signal(signal.SIGTERM, terminate_handler)
    for address_list in args.address:
        Server.add_server(address_list)
    Server.start_server()
    for f in close_file:
        f.close()


if __name__ == "__main__":
    main()
