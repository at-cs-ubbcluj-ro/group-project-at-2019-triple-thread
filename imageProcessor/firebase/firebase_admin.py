import os
import time
from datetime import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime

# project id is unique for a firebase project
project_id = "myparking-d6282"
# the user id is associated with a google account, should be send on the socket with the images, for now it's static
user_id = "1johKUqM3WMSUMHqBz9YyPrO3x63"
ROOT_DIR = os.path.split(os.environ['VIRTUAL_ENV'])[0]

class FirebaseAdmin:
    def __init__(self):
        # import credentials json
        cred = credentials.Certificate(ROOT_DIR + '/firebase/myparking-d6282-664bd8c817e6.json')
        # initialize firebase
        firebase_admin.initialize_app(cred, {
            'projectId': project_id,
        })
        self.db = firestore.client()

    def get_db(self):
        return self.db

    def save_record(self, plate_number, user=user_id):
        accepted_LPs = self.get_plates(user)
        if plate_number in accepted_LPs:
            print("licence plate granted:" + plate_number + " for user " + user)
            doc_ref = self.db.collection(u'parkinghistory').document()

            from google.cloud import firestore as fs
            timestamp = fs.SERVER_TIMESTAMP

            """
            ts = datetime.datetime.now()
            from google.cloud._helpers import _datetime_to_pb_timestamp
            timestamp = _datetime_to_pb_timestamp(ts)
            """
            doc_ref.set({
                u'plate': plate_number,
                u'time': timestamp,
                u'user': user
            })
        else:
            print("Licence plate rejected")

    def get_plates(self, user=user_id):
        # get a collection
        users_ref = self.db.collection(u'plates')
        docs = users_ref.get()

        # get all plates of the current user
        accepted_LPs = []
        for doc in docs:
            dict_doc = doc.to_dict()
            if dict_doc["user"] == user:
                accepted_LPs.append(doc.to_dict()["plate"])
        return accepted_LPs


