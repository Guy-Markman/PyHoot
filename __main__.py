# Changes since last commit:
# Added logger
import argparse
import logging
import signal

import base
import constants
import Server


def parse_args():
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
        default=["localhost:80"],
        nargs="+",
        help="The address(es) we will connect to, default %(default)s",
    )
    parser.add_argument(
        "--buff-size",
        default=constants.BUFF_SIZE,
        type=int,
        help="Buff size for each time, default %(default)d"
    )
    parser.add_argument(
        "--base",
        default=".",
        type=str,
        help="Base directory"
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
    args = parse_args()

    if args.log_file:
        logger = base.setup_logging(
            stream=open(args.log_file, 'a'),
            level=args.log_level,
        )
    else:
        logger = base.setup_logging(
            level=args.log_level,
        )
    logger.info("Parsed args and created logger")
    server = Server.Server(args.buff_size, args.base)

    # Signals set and handlers for nice shutdown
    def terminate_handler(signo, frame):
        server.terminate()
    signal.signal(signal.SIGINT, terminate_handler)
    signal.signal(signal.SIGTERM, terminate_handler)
    for address_list in args.address:
        server.add_server(address_list)
    server.start_server()


if __name__ == "__main__":
    main()
