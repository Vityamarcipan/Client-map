
from flask import Flask, render_template, request, redirect, jsonify
import sqlite3, requests
import os 
app=Flask(__name__)
DB='clients.db'

def init():
    con=sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS clients(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,address TEXT,phone TEXT,comment TEXT,lat REAL,lon REAL)""")
    con.close()
init()

@app.route('/')
def index():
    con=sqlite3.connect(DB)
    rows=con.execute("SELECT name,address,phone,comment,lat,lon FROM clients").fetchall()
    con.close()
    return render_template("index.html",clients=rows)

@app.route('/add',methods=['POST'])
def add():
    name=request.form['name']
    address=request.form['address']
    phone=request.form['phone']
    comment=request.form['comment']
    r=requests.get("https://nominatim.openstreetmap.org/search",
        params={"q":address,"format":"json","limit":1},
        headers={"User-Agent":"ClientMapApp"})
    data=r.json()
    lat=lon=None
    if data:
        lat=float(data[0]["lat"]); lon=float(data[0]["lon"])
    con=sqlite3.connect(DB)
    con.execute("INSERT INTO clients(name,address,phone,comment,lat,lon) VALUES(?,?,?,?,?,?)",
                (name,address,phone,comment,lat,lon))
    con.commit(); con.close()
    return redirect('/')

@app.route('/markers')
def markers():
    con=sqlite3.connect(DB)
    rows=con.execute("SELECT name,address,phone,comment,lat,lon FROM clients WHERE lat IS NOT NULL").fetchall()
    con.close()
    return jsonify([{"name":r[0],"address":r[1],"phone":r[2],"comment":r[3],"lat":r[4],"lon":r[5]} for r in rows])

if name == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
