import sqlite3

class Source:
    def __init__(self, description: str, year: int, month: int, date: int, author: str, path: str, link: str, citation: str, width: str, title: str, tags: list, countries: list):
        self.description = description
        self.year = year
        self.month = month
        self.date = date
        self.author = author
        self.path = path
        self.link = link
        self.citation = citation
        self.width = width
        self.title = title
        self.tags = tags
        self.countries = countries

    def add(self):
        self.conn = sqlite3.connect("sources.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "INSERT INTO SOURCES (DESCRIPTION, YEAR, MONTH, DATE, AUTHOR, PATH, LINK, CITATION, WIDTH, TITLE) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (self.description, self.year, self.month, self.date, self.author, self.path, self.link, self.citation, self.width, self.title)
        )

        self.conn.commit()

        for country in self.countries:
            self.cursor.execute("INSERT INTO SRC_COUNS (SRC_ID, COUN_ID) VALUES (?, ?)", (self.id, country))
        for tag in self.tags:
            self.cursor.execute("INSERT INTO SRC_TAGS (SRC_ID, TAG_ID) VALUES (?, ?)", (self.id, tag))

        self.conn.commit()

        self.conn.close()

    def __repr__(self):
        return f"Source({self.description}, {self.year}, {self.month}, {self.date}, {self.author}, {self.path}, {self.link}, {self.citation}, {self.width}, {self.title})"
    
if __name__ == "__main__":
    title = input("Enter title: ")
    description = input("Enter description: ")
    year = int(input("Enter year: "))
    month = int(input("Enter month: "))
    date = int(input("Enter date: "))
    author = input("Enter author: ")
    path = input("Enter path: ")
    link = input("Enter link: ")
    citation = input("Enter citation: ")
    width = input("Enter width: ")
    tags = input("Enter tags (comma separated): ").split(',')
    countries = input("Enter countries (comma separated): ").split(',')
    tags = [tag.strip() for tag in tags]
    countries = [country.strip() for country in countries]
    source = Source(description, year, month, date, author, path, link, citation, width, title, tags, countries)
    source.add()
    print("Source added successfully!")