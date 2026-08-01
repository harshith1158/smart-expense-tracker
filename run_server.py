import os
import sys

project_dir = os.path.join(os.path.dirname(__file__), "expense-tracker")
if not os.path.isdir(project_dir):
    raise FileNotFoundError(f"Project directory not found: {project_dir}")

os.chdir(project_dir)
sys.path.insert(0, project_dir)

import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=False)
