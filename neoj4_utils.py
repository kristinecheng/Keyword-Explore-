from neo4j import GraphDatabase
import pandas as pd

class Neo4jConnect:
    def __init__(self, url, user, password):
        self.__url = url
        self.__user = user
        self.__password = password
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__url, auth = (self.__user, self.__password))
        except Exception as e:
            print("Failed to create the driver: ", e)
        
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
    
    def query_validation(self, query, db = None):
        assert self.__driver is not None, "Initialize dirver fail"
        session = None
        respond = None
        try:
            if db is not None:
                session = self.__driver.session(database = db)
            else:
                self.__driver.session()
            respond = list(session.run(query))
        except Exception as e:
            print("Query not valid: ", e)
        finally:
            if session is not None:
                session.close()
        return respond
    
## Connect to neo4j local server (change user name and password)
connection = Neo4jConnect(url = 'bolt://localhost:7687', user = 'neo4j', password = 'test_root')

## Query 1: Display the 10 most cited research paper with selected keyword.
def get_top_10_cited_research_paper_by_keyword(keyword):
    query = f'''
        MATCH (i1:INSTITUTE) <- [:AFFILIATION_WITH] - (f1:FACULTY) -[:PUBLISH] -> (p:PUBLICATION) - [l:LABEL_BY] -> (k:KEYWORD)
        WHERE k.name = "{keyword}"
        RETURN p.title, SUM(p.numCitations) AS count
        ORDER BY count DESC
        LIMIT 10
    '''
    result = connection.query_validation(query, db = 'academicworld')
    dataframe = pd.DataFrame([dict(_) for _ in result]).rename(columns = {'p.title': 'publication'})
    return dataframe

## Query 2: By selecting the keyword, display the top professor that has highest KRC score.
def get_top_10_faculty_by_keywords(keyword):
    query = f'''
        MATCH (i:INSTITUTE) <- [:AFFILIATION_WITH] - (f:FACULTY) - [:PUBLISH] -> (p:PUBLICATION) - [l:LABEL_BY] -> (k:KEYWORD)
        WHERE k.name = '{keyword}'
        RETURN f.name, i.name, SUM(l.score * p.numCitations) AS total_score
        ORDER BY total_score DESC
        LIMIT 10
        '''
    result = connection.query_validation(query, db = 'academicworld')
    dataframe = pd.DataFrame([dict(_) for _ in result]).rename(columns = {'f.name': 'faculty', 'i.name': 'school'})
    return dataframe

## Query 3: By selecting the university, it will display the top 10 keywords of the school and the KRC score into pie chart.
def get_top_10_keywords_by_School(university):
    query = f'''
        MATCH (i1:INSTITUTE) <- [:AFFILIATION_WITH] - (f1:FACULTY) - [:PUBLISH] -> (p:PUBLICATION) - [l:LABEL_BY] -> (k:KEYWORD)
        WHERE i1.name = '{university}'
        RETURN k.name, SUM(l.score * p.numCitations) AS total_score
        ORDER BY total_score DESC
        LIMIT 10
        '''
    result = connection.query_validation(query, db = 'academicworld')
    dataframe = pd.DataFrame([dict(_) for _ in result]).rename(columns = {'k.name': 'keyword', 'total_score': 'krc score'})
    return dataframe

## Get all keywords for selection
def get_all_keywords():
    query = '''
            MATCH (k:KEYWORD)
            RETURN k.name as name
            ORDER BY name
            '''
    result = connection.query_validation(query, db = 'academicworld')
    keywords = [keyword['name'] for keyword in result]
    return keywords

## Get all universities for selection 
def get_all_universities():
    query = '''
            MATCH (n:INSTITUTE)
            RETURN n.name as name
            ORDER BY name
            '''
    result = connection.query_validation(query, db='academicworld')
    universities = [record['name'] for record in result]
    return universities
