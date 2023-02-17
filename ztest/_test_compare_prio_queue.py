# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : _test_compare_prio_queue.py
# ------------------------------------------------------------------------------
#
# File          : _test_compare_prio_queue.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
import heapq,time
import random
_s=time.time()
l=[]
l.append((2,'task2'))
l.append((5,'task5'))
l.append((0,'task0'))
l.append((1,'task1'))
heapq.heapify(l)

# operation
# print(l[0])
# print(heapq.heappop(l))
# print(l[0])
# print(heapq.heapreplace(l,(0,'Task0')))
# print(l[0])
# update

# for i in range(100):
#     _p=random.randint(0,240)
#     heapq.heappush(l, (_p, 'Task%s'%_p))
#     print(l[0])
# print(l[0])
# l.remove((0,'task0'))
# print(l[0])
print(l[0])
l[l.index((0,'task0'))]=(7,'task7')
heapq.heapify(l)
print(l[0])
print('--->',(time.time()-_s)*1000)