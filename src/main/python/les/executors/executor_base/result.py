#!/usr/bin/env python

class Result(object):

  def __init__(self, task_id, solution):
    self._task_id = task_id
    self._solution = solution

  def __str__(self):
    return '%s[task_id=%d]' % (self.__class__.__name__, self._task_id)

  def get_task_id(self):
    return self._task_id

  def get_solution(self):
    return self._solution
