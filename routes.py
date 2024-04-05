# routes.py
from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from model import Book, BookUpdate

router = APIRouter()


@router.post("/", response_description="Post a new book", status_code=status.HTTP_201_CREATED, response_model=Book)
def create_book(request: Request, book: Book = Body(...)):
    book = jsonable_encoder(book)
    new_book = request.app.database["books"].insert_one(book)
    created_book = request.app.database["books"].find_one(
        {"_id": new_book.inserted_id}
    )

    return created_book


@router.get("/", response_description="Get all books", response_model=List[Book])
def list_books(request: Request, rating: float = 0):
    books = list(request.app.database["books"].find(
        {"average_rating": {"$gte": rating}}))
    return books


@router.get("/{id}", response_description="Get a single book by id", response_model=Book)
def find_book(id: str, request: Request):
    if (book := request.app.database["books"].find_one({"_id": id})) is not None:
        return book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Book with ID {id} not found")


@router.put("/{id}", response_description="Update a book by id", response_model=Book)
def update_book(id: str, request: Request, book: BookUpdate = Body(...)):
    # libro en la base de datos
    existing_book = request.app.database["books"].find_one({"_id": id})
    # Si no esta se manda el error
    if existing_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Book with ID {id} not found")

    # Actualizar el libro con la información proporcionada en el cuerpo de la solicitud
    update_data = book.__dict__
    for key, value in update_data.items():
        existing_book[key] = value

    # Actualizar el libro en la base de datos
    request.app.database["books"].replace_one({"_id": id}, existing_book)

    # Devolver el libro actualizado
    return existing_book

@router.delete("/{id}", response_description="Delete a book")
def delete_book(id: str, request: Request, response: Response):
    # Implementación para eliminar el libro con el ID proporcionado
    existing_book = request.app.database["books"].find_one({"_id": id})
    if existing_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Book with ID {id} not found")

    request.app.database["books"].delete_one({"_id": id})
    return {"message": f"Book with ID {id} has been deleted successfully"}
    