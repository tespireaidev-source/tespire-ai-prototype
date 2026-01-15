from fastapi import FastAPI
app =FastAPI(title="Tespire AI Prototype")
@app.get("/")
def root():
    return {"messege" : "Tespire AI backend is running"}