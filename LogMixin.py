import logging, logging.config
import yaml
class LogMixin(object):
    __loggerConfigured = False
    @property
    def logger(self):
        if not self.__loggerConfigured:
            with open('log_config.yaml', 'rt') as f:
                config = yaml.load(f.read())
                logging.config.dictConfig(config)
            self.__loggerConfigured = True
        name = '.'.join([self.__class__.__name__])
        return logging.getLogger(name)