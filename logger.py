import logging
import logging.config
import yaml

logger_config = (
"""
version: 1
formatters:
  simple:
    format: '%(asctime)s - %(name)s - %(levelname)s File: %(filename)s - Line: %(lineno)d <##> %(message)s'
handlers:
  console:
    class : logging.StreamHandler
    level : DEBUG
    formatter: simple
    stream: ext://sys.stderr
  file:
    class : logging.handlers.TimedRotatingFileHandler
    level : DEBUG
    formatter: simple
    when: midnight
    filename: {base}/{module}.log

loggers:
  strmmon:
      level: DEBUG
      handlers: [console, file]
  control.events:
      level: DEBUG
      handlers: [console, file]
  root:
      level: INFO
      handlers: [console, file]
"""
)

def logging_setup(base,module):
    lg = logger_config.format(base=base, module=module)
    logging.config.dictConfig(yaml.load(lg, Loader=yaml.FullLoader))
