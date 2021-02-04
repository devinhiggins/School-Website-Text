from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
# username and password must be percent-escaped
# with urllib.parse.quote_plus() in Python3
# from urllib.parse import quote_plus


# username = quote_plus('myTableau')
# password = quote_plus('Schooltext2020')

# connect to MongoDB
client = MongoClient(host='40.87.64.150',
                     port=21319,
                     username="myTableau",
                     password="Schooltext2020",
                     authSource="schooltext"
                     )
# db=client.admin
db = client.schooltext
# Issue the serverStatus command and print the results
# serverStatusResult=db.command("serverStatus")
# pprint(serverStatusResult)
schools = db.schools
pprint(schools.find_one())
