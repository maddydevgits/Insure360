from web3 import Web3,HTTPProvider
import json
import os
from flask import Flask,render_template,request,redirect,session
from pymongo import MongoClient
from datetime import datetime
from keras.models import load_model  
from PIL import Image, ImageOps  
import numpy as np
import urllib3

dbClient=MongoClient('mongodb://127.0.0.1:27017/')
db=dbClient['fypdb']
register_info=db['registerdb']
products_info=db['products']
applied_schemes = db['applied_schemes']

app=Flask(__name__)
app.secret_key='123'

def connectWithBlockchain():
    web3=Web3(HTTPProvider('http://127.0.0.1:7545'))
    web3.eth.defaultAccount=web3.eth.accounts[0]

    artifact_path='../build/contracts/Insure360.json'
    with open(artifact_path) as f:
        artifact_json=json.load(f)
        contract_abi=artifact_json['abi']
        contract_address=artifact_json['networks']['5777']['address']
    
    contract=web3.eth.contract(abi=contract_abi,address=contract_address)
    return contract,web3

def readDataFromThingSpeak(channelid=2458399, date='YYYY-MM-DD'):
    http = urllib3.PoolManager()
    response = http.request('GET', 'https://api.thingspeak.com/channels/' + str(channelid) + '/feeds.json?results=8000')
    response = response.data
    response = response.decode('utf-8')
    
    response = json.loads(response)
    feeds = response['feeds']
    
    # Filter feeds based on the given date
    filtered_feeds = [feed for feed in feeds if feed['created_at'].startswith(date)]
    print(filtered_feeds)
    return filtered_feeds

def readDataFromThingSpeak1(channelid=2458399):
    http = urllib3.PoolManager()
    response = http.request('GET', 'https://api.thingspeak.com/channels/' + str(channelid) + '/feeds.json?results=8000')
    response = response.data
    response = response.decode('utf-8')
    
    response = json.loads(response)
    feeds = response['feeds']
    
    return feeds

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/cs')
def censceh():
    return render_template('censche.html')

@app.route('/ss')
def stasche():
    return render_template('stasche.html')

@app.route('/schemes')
def schemes():
    return render_template('schemes.html')

@app.route('/alogin')
def alogin():
    return render_template('alogin.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/apply')
def apply():
    return render_template('apply.html')

@app.route('/claim')
def claim():
    return render_template('claim.html')

@app.route('/analyze')
def analyze():
    return render_template('analyze.html')

@app.route('/alert')
def alert():
    datafile=readDataFromThingSpeak1()
    data=[]
    for i in datafile:
        print(i)
        if float(i['field1'])>65:
            dummy=[]
            dummy.append(i['created_at'])
            dummy.append(i['entry_id'])
            dummy.append(i['field1'])
            dummy.append('Humidity High')
            data.append(dummy)
        if float(i['field2'])>35:
            dummy=[]
            dummy.append(i['created_at'])
            dummy.append(i['entry_id'])
            dummy.append(i['field2'])
            dummy.append('Temperature High')
            data.append(dummy)
        if float(i['field2'])<20:
            dummy=[]
            dummy.append(i['created_at'])
            dummy.append(i['entry_id'])
            dummy.append(i['field2'])
            dummy.append('Temperature Low')
            data.append(dummy)
        if float(i['field3'])<400:
            dummy=[]
            dummy.append(i['created_at'])
            dummy.append(i['entry_id'])
            dummy.append(i['field3'])
            dummy.append('Too Wet Soil')
            data.append(dummy)
        if float(i['field4'])>101720:
            dummy=[]
            dummy.append(i['created_at'])
            dummy.append(i['entry_id'])
            dummy.append(i['field4'])
            dummy.append('High Atmospheric Pressure')
            data.append(dummy)
    return render_template('alerts.html',data=data)

@app.route('/disease', methods=['POST', 'GET'])
def disease():
    if request.method == 'POST':
        img = request.files['image']
        if img:
            np.set_printoptions(suppress=True)
            model = load_model("static/keras_model.h5", compile=False)
            class_names = open("static/labels.txt", "r").readlines()
            data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
            image = Image.open(img).convert("RGB")
            size = (224, 224)
            image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
            image_array = np.asarray(image)
            normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
            data[0] = normalized_image_array
            prediction = model.predict(data)
            index = np.argmax(prediction)
            class_name = class_names[index]
            confidence_score = prediction[0][index]
            result = f"Class: {class_name[2:]}, Confidence Score: {confidence_score}"
            print(result)
            return render_template('analyze.html', result=result,img=img)
        else:
            return render_template('analyze.html', result="Image file not accepted")
    else:
        return render_template('analyze.html', result=None)

def is_valid_password(psw):
    if len(psw) < 8:
        return False
    if not any(char.isdigit() for char in psw):
        return False
    if not any(char.isupper() for char in psw):
        return False
    if not any(char.islower() for char in psw):
        return False
    if not any(char in '!@#$%^&*()_-+=[]{}|;:,.<>?/' for char in psw):
        return False
    return True

@app.route('/log',methods=['POST','GET'])
def log():
        global email
        global uname
        email = request.form['email']
        pwd = request.form['pwd']
        user = register_info.find_one({'email': email, 'psw': pwd})
        if user:
            msg1='Login Successful'
            session['username']=email
            uname=register_info.find_one({'email':email}).get('name')
            return render_template('alogin.html', user=user,msg1=msg1)
        else:
            msg = 'Invalid email or password. Please try again.'
            return render_template('alogin.html', msg=msg)
        
@app.route('/reg', methods=['POST', 'GET'])
def reg():
    name = request.form['name']
    location =request.form['location']
    email = request.form['email']
    phn=request.form['phn']
    pwd = request.form['pwd']

    existing_user = register_info.find_one({'email': email})
    if existing_user:
        msg='Email already exists'
        return render_template('register.html',msg=msg)

    if not is_valid_password(pwd):
        msg = 'Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.'
        return render_template('register.html', msg=msg)

    user_data = {
        'name': name,
        'location':location,
        'email': email,
        'phn':phn,
        'psw': pwd,
    }
    register_info.insert_one(user_data)
    msg='Registration successful'
    return render_template('register.html',msg=msg)

@app.route('/products', methods=['POST', 'GET'])
def get_products():
    if request.method == 'POST':
        selected_location = request.form.get('selectOption')
        print(f"Selected Location: {selected_location}")
        products = list(products_info.find({'location': selected_location}))
        print(f"Fetched Products: {products}")
        if not products:
            print("No products found for the selected location.")
            return render_template('products.html', products=None, selected_location=selected_location)
        return render_template('products.html', products=products, selected_location=selected_location)
    return render_template('products.html')

# @app.route('/analyze',methods=['POST','GET'])
# def analyze():
#     if request.method=='post'

@app.route('/claimapply',methods=['POST'])
def claim_apply():
    dateOfCalamity=request.form['dateOfCalamity']
    schemeID=request.form['schemeID']
    farmerName=request.form['farmerName']
    farmerID=request.form['farmerID']
    bankAccount=request.form['bankAccount']
    premiumAmount=request.form['premiumAmount']

    contract,web3=connectWithBlockchain()
    _schemes,_schemeid,_farmername,_farmerid,_bankaccount,_premiumamount,_date,_ids,_farmeremails,_statuses=contract.functions.viewSchemes().call()

    for i in range(len(_schemes)):
        if(schemeID==_schemeid[i] and farmerID==_farmerid[i] and bankAccount == _bankaccount[i] and _premiumamount[i]==premiumAmount and _farmeremails[i]==session['username'] and _statuses[i]==0):
            print('Person applied for scheme')
            id=_ids[i]
            datafile=readDataFromThingSpeak(date=dateOfCalamity)
            num_of_samples=len(datafile)
            print(num_of_samples)
            if num_of_samples>0:
                h=0
                for i in datafile:
                    h+=float(i['field1'])
                h=h/num_of_samples
                if(h>60):
                    contract,web3=connectWithBlockchain()
                    tx_hash=contract.functions.claimScheme(int(id),1).transact()
                    web3.eth.waitForTransactionReceipt(tx_hash)
                    return render_template('claim.html',msg='person claim is original')
                elif(h<60):
                    return render_template('claim.html',msg='person claim is not original')
            if(num_of_samples==0):
                return render_template('claim.html',msg='no data available for claim, please claim manually')
    
    return render_template('claim.html',msg='no data found')


@app.route('/applyschemes', methods=['POST','GET'])
def apply_scheme():
    selected_scheme = request.form['schemes']
    scheme_id = request.form['schemeid']
    farmer_name = request.form['farmername']
    farmer_id = request.form['farmerid']
    bank_account = request.form['bankaccount']
    premium_amount = request.form['premiumamount']
    date = request.form['date']

    scheme_data = {
        'selected_scheme': selected_scheme,
        'scheme_id': scheme_id,
        'farmer_name': farmer_name,
        'farmer_id': farmer_id,
        'bank_account': bank_account,
        'premium_amount': premium_amount,
        'date': date,
        'farmer_email':session['username']
    }
    
    msg='applied successfully'

    contract,web3=connectWithBlockchain()
    _schemes,_schemeid,_farmername,_farmerid,_bankaccount,_premiumamount,_date,_ids,_farmeremails,_statuses=contract.functions.viewSchemes().call()

    for i in range(len(_ids)):
        if _schemes[i]==selected_scheme and _farmeremails[i]==session['username']:
            return render_template('apply.html',msg='scheme already applied')
    
    tx_hash=contract.functions.applyScheme(selected_scheme,scheme_id,farmer_name,farmer_id,bank_account,premium_amount,date,session['username']).transact()
    web3.eth.waitForTransactionReceipt(tx_hash)
    applied_schemes.insert_one(scheme_data)
    return render_template('apply.html',msg=msg)


@app.route('/admin')
def admin():
    return render_template('adminlogin.html')

@app.route('/adminlogin',methods=['POST','GET'])
def adminlogin():
    email1="admin@gmail.com"
    pwd1="Admin@123"
    email=request.form['email']
    pwd=request.form['pwd']
    if(email==email1 and pwd==pwd1):
        return redirect('/adminhome')
    else:
        return render_template("home.html")

@app.route('/adminhome')
def adminhome():
    contract,web3=connectWithBlockchain()
    _schemes,_schemeid,_farmername,_farmerid,_bankaccount,_premiumamount,_date,_ids,_farmeremails,_statuses=contract.functions.viewSchemes().call()
    data=[]
    for i in range(len(_schemes)):
        dummy=[]
        dummy.append(_schemes[i])
        dummy.append(_schemeid[i])
        dummy.append(_farmername[i])
        dummy.append(_farmerid[i])
        dummy.append(_bankaccount[i])
        dummy.append(_premiumamount[i])
        dummy.append(_date[i])
        dummy.append(_ids[i])
        dummy.append(_farmeremails[i])
        dummy.append(_statuses[i])
        data.append(dummy)
    return render_template('admin.html',data=data)

if __name__ == "__main__":
    app.run(port=9001,debug=True)
