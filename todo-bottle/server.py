from bottle import Bottle, request, response

import db
import jsend

app = Bottle()

db.connect("todo.db")


@app.get("/task")
@app.get("/task/<task_id:int>")
def task_get(task_id=None):
    """ Fetch a single task or fetch all tasks.
    :return: jsend JSON object with key 'data' containing a single or a list of tasks
    response 200 OK - response data has content
             404 Not Found - task task_id not found
             500 Server Internal Error - most likely database error
    """
    response.headers["Content-Type"] = "application/json"
    response.headers["Cache-Control"] = "no-cache"
    try:
        if task_id is None:
            tasks = db.task.select()
            response.status = 200
            return jsend.success([dict(task) for task in tasks])
        else:
            task = db.task.select(task_id)
            if task is None:
                response.status = 404
                return jsend.fail("task {} not found".format(task_id))
            else:
                response.status = 200
                return jsend.success(dict(task))
    except Exception as e:
        response.status = 500
        return jsend.error("GET task failed", code=type(e).__name__, data=str(e))


@app.put("/task")
@app.put("/task/<task_id:int>")
def task_put(task_id=None):
    """ Update a single task. Updating all tasks not supported.
    :return: jsend JSON object with key 'data' containing the task_id of the updated task
    response 200 OK - task updated successfully
             400 no JSON content in request
             404 Not Found - task task_id not found
             405 PUT on collection not supported
             500 Server Internal Error - most likely database error
    """
    response.headers["Content-Type"] = "application/json"
    try:
        if task_id is None:
            response.status = 405
            return jsend.error("PUT on collection not supported")
        else:
            task = db.task.select(task_id)
            if task is None:
                response.status = 404
                return jsend.fail("task {} not found".format(task_id))
            else:
                data = request.json
                if data is None:
                    response.status = 400
                    return jsend.fail("no JSON content")
                else:
                    db.task.update(task_id, data["summary"], data["description"], data["duedate"], data["status_id"])
                    response.status = 200
                    return jsend.success({"id": task_id})
    except Exception as e:
        response.status = 500
        return jsend.error("PUT task failed", code=type(e).__name__, data=str(e))


@app.post("/task")
@app.post("/task/<task_id:int>")
def task_post(task_id=None):
    """ Insert a new task.
    :return: jsend JSON object with key 'data' containing the task_id of newly created task
    response 201 Created - task inserted
             400 No JSON content in request
             405 insert with predefined task_id not possible
             500 Server Internal Error - most likely database error
    """
    response.headers["Content-Type"] = "application/json"
    try:
        if task_id is None:
            data = request.json
            if data is None:
                response.status = 400
                return jsend.fail("no JSON content")
            else:
                task_id = db.task.insert(data["summary"], data["description"], data["duedate"], data["status_id"])
                response.status = 201
                return jsend.success({"id": task_id})
        else:
            response.status = 405
            return jsend.error("POST on task_id not possible")
    except Exception as e:
        response.status = 500
        return jsend.error("POST task failed", code=type(e).__name__, data=str(e))


@app.delete("/task")
@app.delete("/task/<task_id:int>")
def task_delete(task_id=None):
    """ Delete a single task. Deleting all tasks is not supported.
    :return: jsend JSON object with key 'data' containing the content of the deleted task
    response: 200 OK - task deleted successfully
              404 task task_id not found
              405 delete on collection not supported
              500 Server Internal Error - most likely database error
    """
    response.headers["Content-Type"] = "application/json"
    try:
        if task_id is None:
            response.status = 405
            return jsend.error("DELETE on collection not supported")
        else:
            task = db.task.select(task_id)
            if task is None:
                response.status = 404
                return jsend.fail("task {} not found".format(task_id))
            else:
                db.task.delete(task_id)
                response.status = 200
                return jsend.success(dict(task))
    except Exception as e:
        response.status = 500
        return jsend.error("DELETE task failed", code=type(e).__name__, data=str(e))


if __name__ == "__main__":
    app.run(host="127.0.0.10", port=8080, debug=True, reloader=True)