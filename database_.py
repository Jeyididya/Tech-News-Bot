import sqlite3

class CONNECTER:
    def __init__(self,database_name):
        self.conn=sqlite3.connect(database_name,check_same_thread=False)
        self.categories=["business","entertainment","general","health","science","sports","technology"]
        self.create_tables()
        self.insert_categories()
    
    def create_tables(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS users (ID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                        UserName TEXT,\
                                        sort_by TEXT,\
                                        end_point TEXT,\
                                        UNIQUE (UserName) ON CONFLICT IGNORE \
                                                )")
        self.conn.execute("CREATE TABLE IF NOT EXISTS categories(ID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                        category TEXT,\
                                        UNIQUE (category) ON CONFLICT IGNORE\
                                        );")
        self.conn.execute("CREATE TABLE IF NOT EXISTS keywords (ID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                        keyword TEXT,\
                                        UNIQUE (keyword) ON CONFLICT IGNORE \
                                        );")
        self.conn.execute("CREATE TABLE IF NOT EXISTS user_keywords (ID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                        keyword_id INTEGER,\
                                        user_id INTEGER,\
                                        FOREIGN KEY(user_id) REFERENCES users(ID), \
                                        FOREIGN KEY(keyword_id) REFERENCES keyboards(ID) \
                                        );")
        self.conn.execute("CREATE TABLE IF NOT EXISTS user_categories (ID INTEGER PRIMARY KEY AUTOINCREMENT,\
                                        category_id INTEGER,\
                                        user_id INTEGER,\
                                        FOREIGN KEY(user_id) REFERENCES users(ID), \
                                        FOREIGN KEY(category_id) REFERENCES categories(ID)\
                                        );")
    def insert_categories(self):
        for i in self.categories:
            self.conn.execute("INSERT INTO categories VALUES(NULL,'{}')".format(i))
        self.conn.commit()


    def add_users_to_database(self,user,data):
        self.conn.execute("INSERT INTO users VAlUES(NULL,'{}','{}','{}')".format(user,data["sortby"],data["endpoint"]))
        self.conn.commit()


    def add_keyword_to_database(self,user,data):
        cat_=self.conn.cursor().execute("SELECT * from users where UserName='{}'".format(user))
        user_id,_,_,_=cat_.fetchone()

        for i in data["keyword"]:
            used_cursor1=self.conn.execute("INSERT INTO keywords VAlUES(NULL,'{}')".format(i))
            keyword_id=used_cursor1.lastrowid
            self.conn.execute("INSERT INTO user_keywords VAlUES(NULL,'{}','{}')".format(keyword_id,user_id))
        self.conn.commit()
    def add_category_to_database(self,user,data):
        cat_=self.conn.cursor().execute("SELECT * from users where UserName='{}'".format(user))
        user_id,_,_,_=cat_.fetchone()
        for category in data["category"]:
            cat_=self.conn.cursor().execute("SELECT * from categories where category='{}'".format(category))
            category_id,_=cat_.fetchone()
            self.conn.execute("INSERT INTO user_categories VAlUES(NULL,'{}','{}')".format(category_id,user_id))
        self.conn.commit()

    def get_keywords(self,user):
        keywords=[]
        for i in self.conn.execute("SELECT * from users where UserName='{}'".format(user)): 
            id,username,sortby,endpoint=i
            for i in self.conn.execute("SELECT * from user_keywords where user_id={}".format(id)): 
                _,key_id,_=i
                for i in self.conn.execute("SELECT * from keywords where ID={}".format(key_id)):
                    keywords.append(i)
        return keywords
    def get_category(self,user):
        category=[]
        for i in self.conn.execute("SELECT * from users where UserName='{}'".format(user)): 
            id,username,sortby,endpoint=i
            for i in self.conn.execute("SELECT * from user_categories where user_id={}".format(id)): 
                _,key_id,_=i
                for i in self.conn.execute("SELECT * from categories where ID={}".format(key_id)):
                    category.append(i)
        return category
    
    def get_user(self,user):
        for i in self.conn.execute("SELECT * from users where UserName='{}'".format(user)):
            return (i)
            print("users.",i)