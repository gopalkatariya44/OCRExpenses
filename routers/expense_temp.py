import re
import shutil
import sys
import tempfile

from typing import Optional
from fastapi import Depends, HTTPException, APIRouter, status, Request, Form, UploadFile, File
from pydantic import BaseModel, Field

import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session

from ocr import SmartExpenseTask
from routers.auth import get_current_user, get_user_exception

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

sys.path.append('..')

router = APIRouter(
    prefix='/expense-temp',
    tags=['Expense Temp'],
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


# class Todo(BaseModel):
#     title: str
#     amount: float
#     description: Optional[str]

@router.post('/add', response_class=HTMLResponse)
async def create_todo_commit(request: Request,
                             file: UploadFile = File(...),
                             db: Session = Depends(get_db)):
    user = await get_current_user(request)
    print(user)
    print(file.filename)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    temp_dir = tempfile.mkdtemp()
    try:
        file_path = f"{temp_dir}/{file.filename}"
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        set = SmartExpenseTask()

        data = set.main(file.filename, file_path)

        expense_temp_model = models.ExpenseTemp()
        expense_temp_model.title = data['title']
        expense_temp_model.amount = float(re.sub(r'[^0-9.]', '', data['amount']))
        expense_temp_model.owner_id = user.get('id')
        db.add(expense_temp_model)
        db.commit()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


@router.get('/{expense_temp_id}', response_class=HTMLResponse)
async def edit_todo(expense_temp_id: int,
                    request: Request,
                    db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo = (db.query(models.ExpenseTemp).filter(models.ExpenseTemp.id == expense_temp_id)
            .filter(models.ExpenseTemp.owner_id == user.get('id')).first())
    return templates.TemplateResponse('todo/edit_expense_temp.html', {'request': request, 'todo': todo, 'user': user})


@router.post('/{expense_temp_id}', response_class=HTMLResponse)
async def edit_todo_commit(request: Request,
                           expense_temp_id: int,
                           title: str = Form(...),
                           description: str = Form(...),
                           amount: float = Form(...),
                           db: Session = Depends(get_db)
                           ):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    expense_temp_model = (db.query(models.ExpenseTemp).filter(models.ExpenseTemp.id == expense_temp_id)
                          .filter(models.ExpenseTemp.owner_id == user.get('id')).first())
    expense_temp_model.is_added = True
    db.add(expense_temp_model)
    db.commit()

    expense_model = models.Todos()
    expense_model.title = title
    expense_model.description = description
    expense_model.amount = amount
    expense_model.owner_id = user.get('id')

    db.add(expense_model)
    db.commit()

    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)


@router.get('/delete/{expense_temp_id}', response_class=HTMLResponse)
async def delete_todo(request: Request, expense_temp_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)

    todo_model = (db.query(models.ExpenseTemp).filter(models.ExpenseTemp.id == expense_temp_id)
                  .filter(models.ExpenseTemp.owner_id == user.get('id')).first())
    if todo_model is None:
        return RedirectResponse(url='/todos', status_code=status.HTTP_302_FOUND)
    (db.query(models.ExpenseTemp).filter(models.ExpenseTemp.id == expense_temp_id)
     .filter(models.ExpenseTemp.owner_id == user.get('id')).delete())
    db.commit()

    return RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
