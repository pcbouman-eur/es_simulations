# -*- coding: utf-8 -*-
"""
Logging configuration in a separate file to avoid import cycles
"""
import logging as log

log.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=log.INFO)
# use log.info(), log.warning(), and log.error() for printing messages
