# API KEY 9yVa2T2OlmILdgFdNSz2xz5uxxCcgOZn8vX2hoNV

import firebase_admin
from firebase_admin import credentials, firestore

credential = credentials.Certificate("Database/food_and_fitness_database_service_key.json")
firebase_admin.initialize_app(credential)

db = firestore.client()


class Database:
    def __init__(self, collection_name="", initial_document="", current_date=""):
        if collection_name == "database" and initial_document != "user_weight":
            self.main_reference = db.collection(f"{collection_name}").document(f"{initial_document}").collection(
                f"{current_date}")
        else:
            self.main_reference = db.collection(f"{collection_name}")

    @staticmethod
    def get_info_for_graphs(document_name, date_range):
        items = {}
        collections = db.collection("database").document(f"{document_name}").collections()
        for collection in collections:
            if collection.id in date_range:
                items[collection.id] = []
                for doc in collection.stream():
                    items[collection.id].append(doc.to_dict())

        return items

    @staticmethod
    def get_user_profile_info():
        items = []
        collections = db.collection("database").document("user_profile").collections()
        for collection in collections:
            for doc in collection.stream():
                items.append(doc)

        return items

    # read all documents and their fields from the main_reference collection
    def get_from_database(self):
        return self.main_reference.stream()  # returns a generator object

    # read all documents and their fields from a specific date collection
    @staticmethod
    def search_specific_date(collection_name, initial_document, specific_date, return_value):
        # create a reference for a specific date, rather than the current date
        specific_date_items = db.collection(f"{collection_name}").document(f"{initial_document}").collection(
                f"{specific_date}").stream()
        # check to see what value needs to be returned
        if return_value == "length":
            return len(list(specific_date_items))  # return length of the list of items
        elif return_value == "items":
            return specific_date_items  # return the items

    # read all documents and their fields that meet the required conditions
    def search(self, field_name, where_cond):
        # return items where the field name is equal to the condition specified
        return self.main_reference.where(f"{field_name}", u"==", f"{where_cond}").stream()

    # add item to database as a document with specified field information
    def add_to_database(self, item_name, item_info):
        # field information is added as a dictionary, making it easy to unpack and use
        self.main_reference.document(f"{item_name}").set(item_info)

    # edit item in database with newly specified field information
    def edit_database(self, edit_item, edit_info):
        # .set() will override any previously inputted information to prevent duplicates
        self.main_reference.document(f"{edit_item}").set(edit_info)

    # delete items in the database (documents only)
    def remove_from_database(self, item_name):
        self.main_reference.document(f"{item_name}").delete()
