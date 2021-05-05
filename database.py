import sqlite3
import json

class Database:

    def __init__( self, filename ):

        self.conn = sqlite3.connect( filename )
        self.db = self.conn.cursor()

        ## todo: some day maybe ORM models here?

        ## initialise database
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY, image TEXT, label TEXT, label_num INT, service TEXT, confidence REAL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP )"
        )

        self.db.execute(
            "CREATE TABLE IF NOT EXISTS raw (id INTEGER PRIMARY KEY, image TEXT, service TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, response TEXT )"
        )

    def save_api_response( self, image, service, response ):
        ## if respose is already a dictionary, modify to json string
        if isinstance( response, dict ):
            response = json.dumps( response )
            
        sql = """INSERT INTO raw(image,service,response) VALUES (?,?,?)"""
        self.db.execute( sql, (image, service, response ) )
        self.conn.commit()

    def save_label( self, image, service, label, label_num, confidence ):
        sql = """INSERT INTO results(image,label,label_num,service,confidence) VALUES (?,?,?,?,?)"""
        self.db.execute( sql, (image, label, label_num, service, confidence) )
        self.conn.commit()
