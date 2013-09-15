import db
import settings

if __name__ == '__main__':
    storage = db.Db(**settings.database)
    for entry in storage.get_entries():
        print entry['title'].encode('utf-8')
        print len(entry['title'])*'='
        print entry['pub_date']
        print entry['link']
        print
