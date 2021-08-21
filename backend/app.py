from pdf_mail import sendpdf 
from fpdf import FPDF
import pathlib
import os 
from dotenv import load_dotenv
from flask import request, jsonify, Flask
from google.cloud import vision
import speech_recognition as sr
import io
import base64


app = Flask(__name__)
client = vision.ImageAnnotatorClient()


load_dotenv()  # take environment variables from .env.

@app.route('/sendNotes/Speech2Text', methods = ['POST'])
def sendNodesSpeech():
    toEmail = request.form['toEmail']
    fileName = request.form['fileName']

    r = sr.Recognizer()
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

    f = request.files['audio']

    with open ('test1.wav', 'wb') as audio:
        f.save(audio)
    with sr.AudioFile('test1.wav') as source:
        audio_text= r.listen(source)
    try:   
        # using google speech recognition
        text = r.recognize_google(audio_text)
        print('Converting audio transcripts into text ...')
        print(text)
        f= open("test.txt","w+", encoding='utf-8')
        f.write(text)

        pdf = FPDF()   
    
    # Add a page
        pdf.add_page()
        pdf.set_font("Times", size = 15)

        f = open("test.txt", "r")
        for x in f:
            pdf.cell(200, 10, txt = x, ln = 1, align = 'L')
        
        # Store the pdf created
        pdf.output(f"{fileName}.pdf") 


    # Create email service 
        emailService = sendpdf("emailsendingpdf@gmail.com", 
                    f"{toEmail}", 
                    EMAIL_PASSWORD, 
                    f"{fileName} ", 
                    "Your Notes Are Attached To This Email.", 
                    f"{fileName}", 
                    pathlib.Path().resolve()) 

    #  send email
        emailService.email_send()
        os.remove(f"{fileName}.pdf")
        #Delete TXT file
        #os.remove("test.txt")

    except:
         print('Sorry.. run again...')

    return {"message": "works"}

@app.route('/sendNotes/OCR', methods = ['POST'])
def sendNotes():
    toEmail = request.json['toEmail']
    fileName = request.json['fileName']
    imgString = request.json['image']

    imgdata = base64.b64decode(imgString)
    filename = 'converted.jpg'  #
    with open(filename, 'wb') as f:
        f.write(imgdata)
    with io.open(filename, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    docText = response.full_text_annotation.text
    f= open("test.txt","w+", encoding='utf-8')
    f.write(docText)
    print(docText)
   
    if response.error.message:
        return {"message": 'error'}

    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    pdf = FPDF()   
    
    # Add a page
    pdf.add_page()
    pdf.set_font("Times", size = 15)

    f = open("test.txt", "r")
    for x in f:
        pdf.cell(200, 10, txt = x, ln = 1, align = 'L')
    
    # Store the pdf created
    pdf.output(f"{fileName}.pdf") 

   # Create email service 
    emailService = sendpdf("emailsendingpdf@gmail.com", 
                f"{toEmail}", 
                EMAIL_PASSWORD, 
                f"{fileName} PDF Notes", 
                "Your Notes Are Attached To This Email.", 
                f"{fileName}", 
                pathlib.Path().resolve()) 

  #  send email
    emailService.email_send()
    #Create pdf string
    with open(f"{fileName}.pdf", "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read())
    os.remove(f"{fileName}.pdf")
    os.remove(f"{filename}")
    #Delete TXT file
    #os.remove("test.txt")

    return {"Generated PDF": encoded_string}
 
@app.route('/deleteFile', methods =['DELETE'])
def deleteFile ():
    os.remove("test.txt")

    return {"message": "File deleted"}

if __name__ == "__main__":
    app.run(debug=True)