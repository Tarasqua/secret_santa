import json
import random
import uvicorn
import pandas as pd
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.requests import Request
from pyngrok import ngrok
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.templating import Jinja2Templates


app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)
templates = Jinja2Templates(directory="static/templates")
host = 'localhost'
port = 81
prime_df = pd.read_csv('prime.csv', names=['employee'])
random_employee_numbers = random.sample(range(len(prime_df)), len(prime_df))


@app.get("/", response_class=HTMLResponse)
def serve_home(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


def post_santa_name(pop_index: int, accepted_employees: dict, name: str):
    """Выбор и запись тайного Санты."""
    # Обработка ошибки, если больше нет участников
    try:
        employee_number = random_employee_numbers.pop(pop_index)
        santa_name = prime_df['employee'][employee_number]
    except IndexError:
        return False
    else:
        accepted_employees[name] = santa_name
        with open('accepted_employees.json', 'w', encoding='utf-8') as f:
            json.dump(accepted_employees, f, ensure_ascii=False, indent=4)
        return True


@app.get('/post_name')
def post_name(name: str):
    """Сопоставляет конкретному работнику своего тайного Санту."""
    with open('accepted_employees.json', encoding="utf8") as json_file:
        accepted_employees = json.load(json_file)
    # Проверка на то, что имя введено корректно
    if name in list(accepted_employees.keys()):
        # Проверка на то, что user не был авторизован
        if accepted_employees[name] == '':
            # Проверка на выпадение собственного имени
            if prime_df['employee'][random_employee_numbers[0]] != name:
                santa_recorded = post_santa_name(0, accepted_employees, name)
                if not santa_recorded:
                    return 'Никто больше не едет на корпоратив :('
                else:
                    return 'Вы - тайный Санта для: {}!'.format(accepted_employees[name])
            else:
                santa_recorded = post_santa_name(-1, accepted_employees, name)
                if not santa_recorded:
                    return 'Никто больше не едет на корпоратив :('
                else:
                    'Вы - тайный Санта для: {}!'.format(accepted_employees[name])
        else:
            return 'Вы уже стали тайным Сантой для {}!'.format(accepted_employees[name])
    else:
        return 'Вас нет в списке гостей :( Проверьте правильность введенного ФИО.'


# @app.get('/get_santa', response_class=HTMLResponse)
# def get_santa():
#     return HTMLResponse(content=html_, status_code=200)


if __name__ == '__main__':
    ngrok.set_auth_token('2Iqsnwl8uI8X4RjvNo985JAaVxE_4yQwC8vTiyPChLXN1RpAT')
    public_url = ngrok.connect(port).public_url
    print(public_url)
    uvicorn.run(app, host=host, port=port)
