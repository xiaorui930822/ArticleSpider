# -*- coding: utf-8 -*-
__author__ = 'xurui'
__date__ = '2018/8/9 0009 15:22'

import redis
redis_cli = redis.StrictRedis()
redis_cli.incr("jobbole_count")