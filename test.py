from heapq import nlargest                                       
from string import punctuation

import pyrebase               # Here i have used pyrebse for using Firebase API for database
import spacy
from flask import Flask, request, render_template
from spacy.lang.en.stop_words import STOP_WORDS

nlp = spacy.load('en_core_web_sm')

app = Flask(__name__)

firebaseConfig = {                      # If you create firebase account for database then firebase will provide you configuration file for connecting to your database
                                         # Add your Configuration file data over here.
    "apiKey": "",
    "authDomain": "",
    "databaseURL": "",
    "projectId": "",
    "storageBucket": "",
    "messagingSenderId": "",
    "appId": "",
    "measurementId": ""

}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()                               


@app.route('/')
def my_form():
    return render_template('login.html')


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.form.get('button') == 'Register':       # Code for registration page
        try:
            email = request.form['email']
            password = request.form['password']

            userr = request.form['user']
            user = auth.create_user_with_email_and_password(email, password)
            #usera = auth.send_email_verification(email)
            #vms = "Check Email For Verification Then Login"
            return render_template('index.html')
        except:
            err = " Email Id Already Exists "
            return render_template('login.html', er=err)

    elif request.form.get('button') == 'Login':    # Code for Login Page
        suser = request.form.get('emailid')
        spass = request.form.get('pass')
        try:
            log = auth.sign_in_with_email_and_password(suser, spass)
            return render_template('index.html')
        except:
            errmsg = "Enter Correct Credentials"
            return render_template('login.html',umessage=errmsg )
    
    elif request.form.get('button') == 'Forget Password':          #Code for Forget Password
        return render_template('fp.html')
    elif request.form.get('button') == 'Submit':
        try:
            emailuser = request.form.get('emailidd')
            cuser = auth.send_password_reset_email(emailuser)
            return render_template('login.html')
        except:
            regf = " Register First "
            return render_template('fp.html',rf = regf)
    elif request.form.get('button') == 'Register Here':
        return render_template('login.html')

    else:                                                     # Text Summarization Code                            
        try:
            if request.method == 'POST':
                text = request.form['u']
                doc = nlp(text)

                stopwords = list(STOP_WORDS) + list(punctuation) + ['\n']

                word_frequency = {}
                for word in doc:
                    if word.text.lower() not in stopwords:
                        if word.text not in word_frequency.keys():
                            word_frequency[word.text] = 1
                        else:
                            word_frequency[word.text] += 1

                max_frequency = max(word_frequency.values())

                for word in word_frequency.keys():
                    word_frequency[word] = word_frequency[word] / max_frequency

                sentence_tokens = [sent for sent in doc.sents]

                sentence_score = {}

                for sent in sentence_tokens:
                    for word in sent:
                        if word.text.lower() in word_frequency.keys():
                            if sent not in sentence_score.keys():
                                sentence_score[sent] = word_frequency[word.text.lower()]
                            else:
                                sentence_score[sent] += word_frequency[word.text.lower()]

                para_length = int(len(sentence_tokens) * (30 / 100))

                summary = nlargest(para_length, sentence_score, key=sentence_score.get)

                final_summary = [word.text for word in summary]

                summary = ' '.join(final_summary)

                return render_template('result.html', data=summary)
        except:
            msg = "Enter Valid text"
            return render_template('index.html', mmsg=msg)


if __name__ == "__main__":
    app.run(debug = True)
