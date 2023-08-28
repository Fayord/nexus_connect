export environment="DEV"
export LOG_LEVEL="DEBUG"
# which python

# uvicorn main:app --workers 1 --host 0.0.0.0 --port 9300 
uvicorn main:app --workers 1 --host 0.0.0.0 --port 9300 --reload