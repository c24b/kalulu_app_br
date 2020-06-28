import logging

def debug(loggername, level="debug", enter_message, exit_message, print=True):
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    file_handler = RotatingFileHandler(os.path.join(LOG_DIR, '{}.log'.format(loggername)), 'a', 1000000, 1)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    # show in cmd
    if print:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        logger.addHandler(stream_handler)
    def log_(level="debug", message, exit_message=None):
        def wrapper(f):
            def wrapped(*args, **kargs):
                f = getattr(sys.modules[__name__], level)
                logger.debug(message)
                r = f(*args, **kargs)
                if exit_message:
                    logger.debug(exit_message)
                return r
            return wrapped
        return wrapper
    return log_
