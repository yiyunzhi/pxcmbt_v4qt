# -*- coding: utf-8 -*-

# ------------------------------------------------------------------------------
#                                                                            --
#                PHOENIX CONTACT GmbH & Co., D-32819 Blomberg                --
#                                                                            --
# ------------------------------------------------------------------------------
# Project       : 
# Sourcefile(s) : priority_queue.py
# ------------------------------------------------------------------------------
#
# File          : priority_queue.py
#
# Author(s)     : Gaofeng Zhang
#
# Status        : in work
#
# Description   : siehe unten
#
#
# ------------------------------------------------------------------------------
class Prioritizable:
    """
    handle lexicographic order of keys
    """

    def __init__(self, k1, k2):
        """
        :param k1: key value
        :param k2: key value
        """
        self.k1 = k1
        self.k2 = k2

    def __repr__(self):
        return 'k1=%s,k2=%s' % (self.k1, self.k2)

    def __lt__(self, other):
        """
        lexicographic 'lower than'
        :param other: comparable keys
        :return: lexicographic order
        """
        return self.k1 < other.k1 or (self.k1 == other.k1 and self.k2 < other.k2)

    def __le__(self, other):
        """
        lexicographic 'lower than or equal'
        :param other: comparable keys
        :return: lexicographic order
        """
        return self.k1 < other.k1 or (self.k1 == other.k1 and self.k2 <= other.k2)


class PriorityNode:
    """
    handle lexicographic order of vertices
    """

    def __init__(self, priority, vertex):
        """
        :param priority: the priority of a
        :param vertex:
        """
        self.priority = priority
        self.vertex = vertex

    def __le__(self, other):
        """
        :param other: comparable node
        :return: lexicographic order
        """
        return self.priority <= other.priority

    def __lt__(self, other):
        """
        :param other: comparable node
        :return: lexicographic order
        """
        return self.priority < other.priority


import heapq


class VertexPriorityQueue:
    def __init__(self, data_list: list = None):
        self.heapData = data_list if data_list else []
        self.verticesInHeap = []
        heapq.heapify(self.heapData)

    def top(self):
        if len(self.heapData) == 0: return None
        return self.heapData[0].vertex

    def top_key(self):
        if len(self.heapData) == 0: return Prioritizable(float('inf'), float('inf'))
        return self.heapData[0].priority

    def pop(self):
        """
        Pop the smallest item off the heap, maintaining the heap invariant.
        """
        _popped = heapq.heappop(self.heapData)
        self.verticesInHeap.remove(_popped.vertex)
        return _popped

    def insert(self, vertex, priority):
        """
        Push item onto heap, maintaining the heap invariant.
        """
        _item = PriorityNode(priority, vertex)
        self.heapData.append(_item)
        self.verticesInHeap.append(vertex)
        heapq.heapify(self.heapData)

    def remove(self, vertex):
        _filter = filter(lambda x: x.vertex == vertex, self.heapData)
        for x in _filter:
            self.heapData.remove(x)
        self.verticesInHeap.remove(vertex)

    def update(self, vertex, priority):
        _filter = filter(lambda x: x.vertex == vertex, self.heapData)
        for x in _filter:
            x.priority = priority
        if [_filter]:
            heapq.heapify(self.heapData)


class PriorityQueueOld:
    def __init__(self):
        self.heap = []
        self.verticesInHeap = []

    def top(self):
        return self.heap[0].vertex

    def top_key(self):
        if len(self.heap) == 0: return Prioritizable(float('inf'), float('inf'))
        return self.heap[0].priority

    def pop(self):
        """!!!THIS CODE WAS COPIED AND MODIFIED!!! Source: Lib/heapq.py"""
        """Pop the smallest item off the heap, maintaining the heap invariant."""
        _last_elt = self.heap.pop()  # raises appropriate IndexError if heap is empty
        self.verticesInHeap.remove(_last_elt)
        if self.heap:
            _return_item = self.heap[0]
            self.heap[0] = _last_elt
            self._siftup(0)
        else:
            _return_item = _last_elt
        return _return_item

    def insert(self, vertex, priority):
        _item = PriorityNode(priority, vertex)
        self.verticesInHeap.append(vertex)
        """!!!THIS CODE WAS COPIED AND MODIFIED!!! Source: Lib/heapq.py"""
        """Push item onto heap, maintaining the heap invariant."""
        self.heap.append(_item)
        self._siftdown(0, len(self.heap) - 1)

    def remove(self, vertex):
        self.verticesInHeap.remove(vertex)
        for index, priority_node in enumerate(self.heap):
            if priority_node.vertex == vertex:
                self.heap[index] = self.heap[len(self.heap) - 1]
                self.heap.remove(self.heap[len(self.heap) - 1])
                break
        self.build_heap()

    def update(self, vertex, priority):
        for index, priority_node in enumerate(self.heap):
            if priority_node.vertex == vertex:
                self.heap[index].priority = priority
                break
        self.build_heap()

    # !!!THIS FUNCTION WAS COPIED AND MODIFIED!!! Source: Lib/heapq.py
    def build_heap(self):
        """Transform list into a heap, in-place, in O(len(x)) time."""
        _n = len(self.heap)
        # Transform bottom-up.  The largest index there's any point to looking at
        # is the largest with a child index in-range, so must have 2*i + 1 < n,
        # or i < (n-1)/2.  If n is even = 2*j, this is (2*j-1)/2 = j-1/2 so
        # j-1 is the largest, which is n//2 - 1.  If n is odd = 2*j+1, this is
        # (2*j+1-1)/2 = j so j-1 is the largest, and that's again n//2-1.
        for i in reversed(range(_n // 2)):
            self._siftup(i)

    # !!!THIS FUNCTION WAS COPIED AND MODIFIED!!! Source: Lib/heapq.py
    # 'heap' is a heap at all indices >= startpos, except possibly for pos.  pos
    # is the index of a leaf with a possibly out-of-order value.  Restore the
    # heap invariant.
    def _siftdown(self, start_pos, pos):
        _new_item = self.heap[pos]
        # Follow the path to the root, moving parents down until finding a place
        # newitem fits.
        while pos > start_pos:
            _parent_pos = (pos - 1) >> 1
            _parent = self.heap[_parent_pos]
            if _new_item < _parent:
                self.heap[pos] = _parent
                pos = _parent_pos
                continue
            break
        self.heap[pos] = _new_item

    def _siftup(self, pos):
        _end_pos = len(self.heap)
        _start_pos = pos
        _new_item = self.heap[pos]
        # Bubble up the smaller child until hitting a leaf.
        _child_pos = 2 * pos + 1  # leftmost child position
        while _child_pos < _end_pos:
            # Set childpos to index of smaller child.
            _right_pos = _child_pos + 1
            if _right_pos < _end_pos and not self.heap[_child_pos] < self.heap[_right_pos]:
                _child_pos = _right_pos
            # Move the smaller child up.
            self.heap[pos] = self.heap[_child_pos]
            pos = _child_pos
            _child_pos = 2 * pos + 1
        # The leaf at pos is empty now.  Put newitem there, and bubble it up
        # to its final resting place (by sifting its parents down).
        self.heap[pos] = _new_item
        self._siftdown(_start_pos, pos)
