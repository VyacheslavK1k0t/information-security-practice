from fastapi import FastAPI
 
app = FastAPI(title="Electronic Dean's Office")
 
 
@app.get("/")
def root():
    return {"message": "Hello World"}