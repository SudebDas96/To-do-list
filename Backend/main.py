from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from database import db
from models import Task

app = FastAPI()

# -------- Allow Frontend (HTML/JS) to access API ------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- Helper to convert DB docs to JSON ----------
def fix_id(task):
    task["id"] = str(task["_id"])
    del task["_id"]
    return task

# ----------- Routes ----------------
@app.get("/")
async def home():
    return {"message": "MongoDB Todo App Running 🚀"}

@app.get("/tasks")
async def get_tasks():
    tasks = await db.tasks.find().to_list(100)
    return [fix_id(t) for t in tasks]
from typing import List

@app.post("/tasks/bulk")
async def add_multiple_tasks(tasks: List[Task]):
    result = await db.tasks.insert_many([task.dict() for task in tasks])
    return {"inserted_ids": [str(id) for id in result.inserted_ids]}

@app.post("/tasks")
async def create_task(task: Task):
    result = await db.tasks.insert_one(task.dict())
    return {"message": "Task added", "id": str(result.inserted_id)}

@app.patch("/tasks/{task_id}")
async def toggle_task(task_id: str):
    task = await db.tasks.find_one({"_id": ObjectId(task_id)})
    new_status = not task["is_done"]

    await db.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": {"is_done": new_status}})
    return {"message": "Updated"}

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    await db.tasks.delete_one({"_id": ObjectId(task_id)})
    return {"message": "Deleted"}

@app.get("/test-db")
async def test_db():
    try:
        doc_count = await db.tasks.count_documents({})
        return {"status": "Connected 🎉", "tasks_in_db": doc_count}
    except Exception as e:
        return {"status": "Failed ❌", "error": str(e)}

