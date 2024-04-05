# client.py
import argparse
import logging
import os
import requests


# Set logger
log = logging.getLogger()
log.setLevel('INFO')
handler = logging.FileHandler('books.log')
handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)

# Read env vars related to API connection
BOOKS_API_URL = os.getenv("BOOKS_API_URL", "http://localhost:8000")


def print_book(book):
    for k in book.keys():
        print(f"{k}: {book[k]}")
    print("="*50)


def list_books(rating):
    suffix = "/book"
    endpoint = BOOKS_API_URL + suffix
    params = {
        "rating": rating
    }
    response = requests.get(endpoint, params=params)
    if response.ok:
        json_resp = response.json()
        for book in json_resp:
            print_book(book)
    else:
        print(f"Error: {response}")


def get_book_by_id(id):
    suffix = f"/book/{id}"
    endpoint = BOOKS_API_URL + suffix
    response = requests.get(endpoint)
    if response.ok:
        json_resp = response.json()
        print_book(json_resp)
    else:
        print(f"Error: {response}")


def update_book(id):
    # libro actual
    suffix = f"/book/{id}"
    endpoint = BOOKS_API_URL + suffix
    response = requests.get(endpoint)

    # verificamos que el libro exista
    if not response.ok:
        print(f"Error: {response}")
        return

    # Imprimimos el libro actual
    book_data = response.json()
    print("Current book details:")
    print_book(book_data)

    # nuestro diccionario con los nuevos datos
    update_data = {}

    # flag para saber si hubo cambios
    flag = False

    for key, value in book_data.items():
        if key == "_id":  # Omitimos que se pueda actualizar el id
            continue

        # para asegurarnos de que los inputs sen correctos [y,n,ENTER]
        while True:
            update = input(f"Do you want to update the value of '{key}'? (y/n): ").lower()
            if update in {'y', 'n', ''}:
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

        if update == 'y':
            flag = True
            new_value = input(f"Enter new value for <{key}>: ")
            # Validar el tipo de dato del campo antes de agregarlo a los datos de actualización
            if key in ["num_pages", "ratings_count", "text_reviews_count"]:
                try:
                    new_value = int(new_value)
                except ValueError:
                    print(f"Error: '{key}' must be a int value.")
                    continue
            elif key == "average_rating":
                try:
                    new_value = float(new_value)
                except ValueError:
                    print(f"Error: '{key}' must be a float/int value.")
                    continue
            elif key == "authors":
                # Usamos el split para separar los autores que se pasan y que se agreguen correctamente al array
                new_value = [author.strip() for author in new_value.split(',')]
            update_data[key] = new_value  # actualizamos los valores
        else:
            # si no quiere actualizar ese campo se mantiene el valor existente
            update_data[key] = value

    if flag:
        # Hacemos el put si hubo update de dato
        response = requests.put(endpoint, json=update_data)
        if response.ok:
            updated_book = response.json()
            print("\nBook updated successfully:\n")
            print_book(updated_book)
        else:
            print("Error:", response)
    else:
        print("No changes were made.")


def delete_book(id):
    suffix = f"/book/{id}"
    endpoint = BOOKS_API_URL + suffix
    response = requests.get(endpoint)

    if response.ok:
        print(f"Deleting book with id: {id}>>>\n")
        json_resp = response.json()
        print_book(json_resp)
        # deleting book
        response = requests.delete(endpoint)
        response.raise_for_status()
        print("\nBook deleted successfullyyy...\n")
    else:
        print(f"Error: {response}")


def main():
    log.info(f"Welcome to books catalog. App requests to: {BOOKS_API_URL}")

    parser = argparse.ArgumentParser()

    list_of_actions = ["search", "get", "update", "delete"]
    parser.add_argument("action", choices=list_of_actions,
                        help="Action to be user for the books library")
    parser.add_argument("-i", "--id",
                        help="Provide a book ID which related to the book action", default=None)
    parser.add_argument("-r", "--rating",
                        help="Search parameter to look for books with average rating equal or above the param (0 to 5)", default=None)

    args = parser.parse_args()

    if args.id and not args.action in ["get", "update", "delete"]:
        log.error(f"Can't use arg id with action {args.action}")
        exit(1)

    if args.rating and args.action != "search":
        log.error(f"Rating arg can only be used with search action")
        exit(1)

    if args.action == "search":
        list_books(args.rating)
    elif args.action == "get" and args.id:
        get_book_by_id(args.id)
    elif args.action == "update":
        update_book(args.id)
    elif args.action == "delete":
        delete_book(args.id)


if __name__ == "__main__":
    main()
