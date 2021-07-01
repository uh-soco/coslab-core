import collections
import json
from functools import partial

class Output:

    def __init__( self ):
        ## todo: think about best data structures
        self.labels = collections.defaultdict( partial( collections.defaultdict , list ) )
        self.responses = []

    def save_api_response( self, image, service, response ):
        ## if respose is already a dictionary, modify to json string
        if isinstance( response, dict ):
            response = json.dumps( response )

        self.responses.append( {'file': image, 'service': service, 'response': response } )

    def save_label( self, image, service, label, label_num, confidence ):
        self.labels[ image ][ service ].append( {'label': label, 'confidence': confidence, 'number': label_num } )
    def export_pickle( self, filename ):

        import pickle

        pickle.dump( self, open( filename, 'wb') )


    def export_sql( self, filename ):

        import sqlite3

        conn = sqlite3.connect( filename )
        db = conn.cursor()

        ## initialise database
        db.execute(
            "CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, image TEXT, label TEXT, label_num INT, service TEXT, confidence REAL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP )"
        )

        db.execute(
            "CREATE TABLE IF NOT EXISTS raw (id INTEGER PRIMARY KEY, image TEXT, service TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, response TEXT )"
        )
        ## todo: is current timestamp OK?

        for response in self.responses:
            sql = """INSERT INTO raw(image,service,response) VALUES (?,?,?)"""
            db.execute( sql, (response['file'], response['service'], response['response'] ) )

        for image, service in self.labels.items():
            for service, labels in service.items():
                for label in labels:
                    label_text = label['label']
                    label_num = label['number']
                    confidence = label['confidence']

                    sql = """INSERT INTO results(image,label,label_num,service,confidence) VALUES (?,?,?,?,?)"""
                    db.execute( sql, (image, label_text, label_num, service, confidence ) )

        conn.commit()
        conn.close()
