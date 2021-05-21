import yaml
import logging
import logging.config
import sys, os

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

def get_logger(name:str, base_path='./nstrend/log_config.yaml'):
    with open(base_path, 'r', encoding='utf-8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)
    
    return logging.getLogger(name)
