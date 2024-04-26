import mysql.connector
import logging
import pandas as pd

config = {
    'user': 'root',
    'password': 'test_root',
    'host': '127.0.0.1',
    'database': 'academicworld',
    'raise_on_warnings': True
}

class CS411SQLDatabase:
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = mysql.connector.connect(**self.config)
        self.cursor = self.connection.cursor(buffered = True)
        return self
    
    def __exit__(self, execution_type, execution_val, execution_tb):
        if execution_type:
            logging.exception("Exeception Occured")
        self.cursor.close()
        self.connection.close()

    def query_execution(self, query, values = None):
        try:
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            logging.exception(f"Query Invalid: {error}")
            self.connection.rollback()
            return False
        
    def retrieve_data(self, query, values = None):
        self.cursor.execute(query, values)
        return self.cursor.fetchall()
    
def retrieve_all_keywords():
    with CS411SQLDatabase(config) as db:
        query = "SELECT name FROM keyword"
        result = db.retrieve_data(query)
        keywords = [row[0] for row in result]
        
    return keywords     

def retrieve_all_favorite_keywords():
    with CS411SQLDatabase(config) as db:
        if not favorite_keyword_table(db):
            create_favorite_keywords_table(db)
        
        query = "SELECT name FROM favorite_keywords"
        result = db.retrieve_data(query)
        favorite_keywords = [row[0] for row in result]
       
    return favorite_keywords

def favorite_keyword_table (db):
    query = "SHOW TABLES LIKE 'favorite_keywords'"
    return bool(db.retrieve_data(query))

def create_favorite_keywords_table(db):
    query = ("CREATE TABLE `favorite_keywords` ("
             "`name` varchar(512) NOT NULL,"
             "PRIMARY KEY (`name`))")
    if db.query_execution(query):
        logging.info("Successful: favorite_keywords table created")

## Query 5: Users are able to add / delete favorite keyword(s) and display the favorite keyword table (MySql).
def add_favorite_keywords(keyword):
    with CS411SQLDatabase(config) as db:
        query = "INSERT INTO favorite_keywords (name) VALUES (%s)"
        values = (keyword, )
        if db.query_execution(query, values):
            logging.info("Successful: Keyword added")

def delete_favorite_keywords(keyword):
    with CS411SQLDatabase(config) as db:
        if not favorite_keyword_table(db):
            logging.error("Error: favorite_keywords table absent.")
            return
        query = "DELETE FROM favorite_keywords WHERE name = %s"
        values = (keyword, )
        if db.query_execution(query, values):
            logging.info("Successful: keyword deleted from table")
        
## Query 6: Display line graph to show trend of each favorite keywords from 1982 to 2022 
##          using score of each keyword (MySql).
def favorite_keywords_score():
    with CS411SQLDatabase(config) as db:
        if not favorite_keyword_table(db):
            logging.error("Error: favorite_keywords table absent.")
            return 
        ## for each keyword, count occurancy and display score
        query = ("SELECT favorite_keywords.name AS keyword, COUNT(*) AS count, SUM(publication_keyword.score * publication.num_citations) AS krc "
                 "FROM favorite_keywords, keyword, publication_keyword, publication "
                 "WHERE favorite_keywords.name = keyword.name AND keyword.id = publication_keyword.keyword_id AND publication_keyword.publication_id = publication.id "
                 "GROUP BY keyword "
                )
        result = db.retrieve_data(query)
        favorite_keywords_stats = pd.DataFrame(list(result)).rename(columns={0: "Keyword", 1: "Publication Count", 2: 'KRC'})
    return favorite_keywords_stats

## R13: Add Indexing into the keyword table
def add_index_to_keyword_table():
    with CS411SQLDatabase(config) as db:
        query = "ALTER TABLE faculty_keyword ADD INDEX idx_keyword_name (name);"
        if db.execute_query(query):
            logging.info("Successful: Index added to keyword table")

## R14: Add trigger on faculty_keyword to make sure score is non-negative
def add_trigger_to_faculty_keyword():
    with CS411SQLDatabase(config) as db:
        query = ("CREATE TRIGGER faculty_keyword_score_check BEFORE INSERT ON faculty_keyword"
                 "FOR EACH ROW"
                 "BEGIN"
                 "IF NEW.score < 0 THEN"
                 "SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'score cannot be negative';"
                 "END IF;"
                 "END")
        if db.execute_query(query):
            logging.info("Successful: Trigger added to faculty_keyword table ensure non-negative score")

## R15: Create view from faculty and university to show faculty from 'University of Illinois at Urbana Champaign'
def show_faculty_from_uiuc():
    with CS411SQLDatabase(config) as db:
        query = ("CREATE VIEW facutly_uiuc AS"
                 "SELECT faculty.name"
                 "FROM faculty, university"
                 "WHERE faculty.university_id == university.id AND university.name = 'University of Illinois at Urbana Champaign'")
        if db.execute_query(query):
            logging.info("Successful: View created for faculty from UIUC")
