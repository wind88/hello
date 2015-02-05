#!/usr/bin/env python
# encoding:utf-8

"""
测试 python env.py -f a.txt
参数
"""

import sys

if __name__ == '__main__':
    print sys.argv[1:]
    print __doc__
    execfile('conf.py')
    print str
