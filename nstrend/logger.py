import yaml
import logging
import logging.config

class Logger:
    def __init__(self):
        self.base_path = './nstrend/log_config.yaml'

    def get_scrape_logger(self):
        with open(self.base_path, 'r', encoding='utf-8') as f:
            config = yaml.load(f)
            logging.config.dictConfig(config)
            return logging.getLogger('scrape')

    def get_main_logger(self):
        with open(self.base_path, 'r', encoding='utf-8') as f:
            config = yaml.load(f)
            logging.config.dictConfig(config)
            return logging.getLogger('main')
