from flask import Flask, render_template
import pymongo

app = Flask(__name__)

# MongoDB connection
client = pymongo.MongoClient("mongodb+srv://mongodb_pro:NbQEQy3Ao3yP63RV@cluster0.oxclotd.mongodb.net/")
db = client["MCA"]
mycollection = db["attendance"]

@app.route('/')
def index():
    all_records = mycollection.find()
    records_list = list(all_records)
    return render_template('index.html', records=records_list)

if __name__ == '__main__':
    app.run(debug=True)
