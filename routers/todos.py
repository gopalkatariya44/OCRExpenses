import sys

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter, status, Request, Form
from pydantic import BaseModel, Field

import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from routers.auth import get_current_user, get_user_exception

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

sys.path.append('..')

router = APIRouter(
    tags=['Todos'],
    responses={
        status.HTTP_404_NOT_FOUND: {
            'description': 'Not found'
        }
    }
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory='templates')


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Todo(BaseModel):
    title: str
    amount: float
    description: Optional[str]


@router.get('/', response_class=HTMLResponse)
async def read_all_by_user(request: Request,
                           db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todos = (db.query(models.Todos)
             .filter(models.Todos.owner_id == user.get('id'))
             .order_by(models.Todos.id).all())
    expense_temp = (db.query(models.ExpenseTemp)
                    .filter(models.ExpenseTemp.owner_id == user.get('id'))
                    .filter(models.ExpenseTemp.is_added == False)
                    .order_by(models.ExpenseTemp.id).all())
    t = 0
    for i in todos:
        t += i.amount
    return templates.TemplateResponse('todo/home.html', {
        'request': request,
        'todos': todos,
        'user': user,
        'total': round(t, 2),
        'expense_temp': expense_temp
    })


@router.get('/add-todo', response_class=HTMLResponse)
async def add_new_todo(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse('todo/add_todo.html', {'request': request, 'user': user})


@router.post('/add-todo', response_class=HTMLResponse)
async def create_todo_commit(request: Request,
                             title: str = Form(...),
                             description: str = Form(...),
                             amount: float = Form(...),
                             db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo_model = models.Todos()
    todo_model.title = title
    todo_model.description = description
    todo_model.amount = amount
    todo_model.owner_id = user.get('id')
    # print(todo_model.__dict__)
    # for i in range(1, 40):
    #     tm = models.Todos()
    #     tm.title = f"Todo {i}"
    #     tm.description = f"Todo description {i}"
    #     tm.priority = 1 if i % 2 == 0 else 4
    #     tm.complete = False if i % 2 == 0 else True
    #     tm.owner_id = user.get('id')
    #     db.add(tm)
    #     db.commit()
    db.add(todo_model)
    db.commit()

    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


@router.get('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo(todo_id: int,
                    request: Request,
                    db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo = (db.query(models.Todos).filter(models.Todos.id == todo_id)
            .filter(models.Todos.owner_id == user.get('id')).first())
    return templates.TemplateResponse('todo/edit_todo.html', {'request': request, 'todo': todo, 'user': user})


@router.post('/edit-todo/{todo_id}', response_class=HTMLResponse)
async def edit_todo_commit(request: Request,
                           todo_id: int,
                           title: str = Form(...),
                           description: str = Form(...),
                           amount: float = Form(...),
                           db: Session = Depends(get_db)
                           ):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo_model = (db.query(models.Todos).filter(models.Todos.id == todo_id)
                  .filter(models.Todos.owner_id == user.get('id')).first())
    todo_model.title = title
    todo_model.description = description
    todo_model.amount = amount
    print(todo_model.__dict__)

    db.add(todo_model)
    db.commit()

    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


@router.get('/delete/{todo_id}', response_class=HTMLResponse)
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo_model = (db.query(models.Todos).filter(models.Todos.id == todo_id)
                  .filter(models.Todos.owner_id == user.get('id')).first())
    if todo_model is None:
        return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)
    (db.query(models.Todos).filter(models.Todos.id == todo_id)
     .filter(models.Todos.owner_id == user.get('id')).delete())
    db.commit()

    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)

# @router.get('/complete/{todo_id}', response_class=HTMLResponse)
# async def complete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
#     user = await get_current_user(request)
#     if user is None:
#         return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
#
#     todo_model = (db.query(models.Todos).filter(models.Todos.id == todo_id)
#                   .filter(models.Todos.owner_id == user.get('id')).first())
#     todo_model.complete = not todo_model.complete
#
#     db.add(todo_model)
#     db.commit()
#
#     return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
