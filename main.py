from datetime import date

from fastapi import FastAPI

app = FastAPI()


@app.get("/info")
def get_info():
    today = date.today()
    next_year = today.year + 1
    new_year_date = date(next_year, 1, 1)

    days_left = (new_year_date - today).days

    return {"days_before_new_year": days_left}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=4200)
