import collections
import json
from functools import partial
import datetime
import csv

import pandas

from coslab import tag_comparator

class TaggerResults:

    def __init__( self ):
        ## todo: think about best data structures
        self.labels = collections.defaultdict( partial( collections.defaultdict , list ) )
        self.responses = []
        self._services = []

    def save_api_response( self, image, service, response, time = datetime.datetime.now() ):
        ## if respose is already a dictionary, modify to json string
        if isinstance( response, dict ):
            response = json.dumps( response )

        self.responses.append( {'file': image, 'service': service, 'response': response, 'time': time } )

        if len( self.responses ) % 1000:
            self.export_pickle( './temp.pickle' )

    def save_label( self, image, service, label, label_num, confidence, time = datetime.datetime.now() ):
        if service not in self._services:
            self._services.append( service )
        self.labels[ image ][ service ].append( {'label': label, 'confidence': confidence, 'number': label_num, 'time': time } )

    def has_image( self, image, service ):
        if image in self.labels:
            if service in self.labels[ image ]:
                return True
        return False

    def export_pickle( self, filename ):

        import pickle

        pickle.dump( self, open( filename, 'wb') )

    def import_pickle( self, filename ):

        import pickle
        old = pickle.load( open( filename, 'rb') )
        self.labels = old.labels
        self.responses = old.responses
        del old


    def export_sql( self, filename ):

        import sqlite3

        conn = sqlite3.connect( filename )
        db = conn.cursor()

        ## initialise database
        db.execute(
            "CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, image TEXT, label TEXT, label_num INT, service TEXT, confidence REAL, timestamp TIMESTAMP )"
        )

        db.execute(
            "CREATE TABLE IF NOT EXISTS raw (id INTEGER PRIMARY KEY, image TEXT, service TEXT, response TEXT, timestamp TIMESTAMP )"
        )
        ## todo: is current timestamp OK?

        for response in self.responses:
            sql = """INSERT INTO raw(image,service,response,timestamp) VALUES (?,?,?,?)"""
            db.execute( sql, (response['file'], response['service'], response['response'], response['time'] ) )

        for image, services in self.labels.items():
            for service, labels in services.items():
                for label in labels:
                    label_text = label['label']
                    label_num = label['number']
                    confidence = label['confidence']

                    sql = """INSERT INTO results(image,label,label_num,service,confidence,timestamp) VALUES (?,?,?,?,?,?)"""
                    db.execute( sql, (image, label_text, label_num, service, confidence, response['time']  ) )

        conn.commit()
        conn.close()

    def export_csv(self, filename, comparator = tag_comparator.identity_comparator):

        df = self.to_pandas( comparator = comparator)
        df.to_csv( filename )

    def to_pandas(self, comparator = tag_comparator.identity_comparator ):

        df = pandas.DataFrame( columns=['image', 'service', 'label', 'service-confidence'] )

        if comparator:
            for service in self._services:
                df[ f'coslab-{service}' ] = []


        for image, services in self.labels.items():
                for service, labels in services.items():
                    for label in labels:
                        label_text = label['label'].lower()
                        confidence = label['confidence']

                        if comparator:
                            coslab_scores = []
                            for compare_with in self._services:
                                score = tag_comparator.compare_image_tags( self, image, label_text, compare_with, comparator )
                                coslab_scores.append( score )
                            df.loc[ len(df) ] = [image,service,label_text,confidence] + coslab_scores
                        else:
                            df.loc[ len(df) ] = (image,service,label_text,confidence)

        return df

