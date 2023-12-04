import sqlite3
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt
from rich.prompt import Confirm
from consolemenu import SelectionMenu


def display() -> int:

    options = ["Add a movie", "View the movies", "Edit a movie"]

    menu = SelectionMenu.get_selection(options)

    return menu


def edit(db: sqlite3.Connection) -> None:
    c = db.cursor()
    c.execute("select name from movies")

    make_table(db)

    editor = input("Enter the name of the movie you would like to edit: ")

    for i in c:
        if str(i[0]).lower() == editor.lower():
            editor = i[0]

    col = Prompt.ask(
        "Which part would you like to edit? ", choices=["date", "watched", "review"]
    )
    val = Prompt.ask("Enter the new value")
    try:
        sql = f'UPDATE movies \
                SET {col} = "{val}" \
                WHERE name = "{editor}"'

        c.execute(sql)
        db.commit()

    except sqlite3.OperationalError:
        print("There was an error updating the data. Please try again.")

    edit_again = Confirm.ask("Would you like to edit more?")

    if edit_again:
        edit(db)

    else:
        return


def connect(file: str) -> sqlite3.Connection:
    db = sqlite3.connect(file)
    c = db.cursor()
    sql = "CREATE TABLE IF NOT EXISTS movies( \
            name TEXT PRIMARY KEY NOT NULL, \
            date TEXT, \
            watched TEXT, \
            review TEXT)"

    c.execute(sql)

    db.commit()

    return db


def insert(db: sqlite3.Connection) -> None:
    c = db.cursor()

    movie = input("What is the title of the movie: ")
    watched = Confirm.ask("Did you watch it? ")

    if watched:
        watched = "yes"
        date = input("When did you watch it? ")
        rating = input("What do you give it out of 10? ")
    else:
        watched = "no"
        date, rating = "-"

    sql = f'INSERT INTO movies(name, date, watched, review) VALUES("{movie}", "{date}", "{watched}", "{rating}/10")'

    c.execute(sql)

    db.commit()


def make_table(db: sqlite3.Connection) -> None:
    table = Table(title="Movies")

    table.add_column("Date", justify="right", no_wrap=True)
    table.add_column("Name", justify="center", no_wrap=True)
    table.add_column("Watched", justify="center", no_wrap=True)
    table.add_column("Rating", justify="left", no_wrap=True)

    c = db.cursor()
    sql = "SELECT * FROM movies"
    c.execute(sql)

    for i in c:
        table.add_row(i[1], i[0], i[2], i[3])

    console = Console()
    console.print(table)

    input("Press enter to continue")
    return


def main():
    db = connect("data/kathy.db")

    menu = display()

    while True:
        if menu == 0:
            insert(db)
            menu = display()
        elif menu == 1:
            make_table(db)
            menu = display()
        elif menu == 2:
            edit(db)
            menu = display()
        elif menu == 3:
            quit()


if __name__ == "__main__":
    main()
