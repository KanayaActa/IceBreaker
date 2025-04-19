# IceBreaker

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```sh
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app

# test
pytest

# unit test
pytest tests/test_project.py
```
