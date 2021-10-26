from server import task_get, task_post

import unittest
import datetime as dt
from mock import Mock, patch

class TestApp(unittest.TestCase):
    def test_task_get(self):
        # create a mock `todo` object
        todo = Mock()
        
        # now we pass the `todo` object check for expected result `True`
        result = task_get(todo)
        self.assertTrue(result)

    def test_task_post(self):

        todo = Mock()

        # now set the attributes for the `todo` object
        todo.id = 15
        todo.summary = 'Testing'
        todo.description = 'Mock'
        todo.duedate = '2021-11-02'
        todo.status_id = 'C'
        todo.modified = '2021-10-26T12:32:02'
        
        result = task_post(todo)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
    