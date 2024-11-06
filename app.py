from logging import debug
from flask import Flask, render_template, request, redirect, jsonify, send_file
import utils  
from utils import preprocessdata 
import sqlite3
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

app = Flask(__name__)

conn = sqlite3.connect('money_tracker.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS expenses
             (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, amount REAL, info TEXT, date TEXT)''')
conn.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/moneytrack')
def money_track():
    return render_template('moneytrack.html')
@app.route('/add', methods=['POST'])
def add_expense():
    category = request.json['category_select']
    amount = request.json['amount_input']
    info = request.json['info']
    date = request.json['date_input']

    c.execute("INSERT INTO expenses (category, amount, info, date) VALUES (?, ?, ?, ?)",
              (category, amount, info, date))
    conn.commit()

    return jsonify({"success": True})

@app.route('/expenses')
def get_expenses():
    c.execute("SELECT * FROM expenses")
    expenses = c.fetchall()

    expenses_list = []
    for expense in expenses:
        expenses_list.append({
            "_id": expense[0],
            "category": expense[1],
            "amount": expense[2],
            "info": expense[3],
            "date": expense[4]
        })

    return jsonify(expenses_list)

@app.route('/download')
def download_expenses():
    c.execute("SELECT * FROM expenses")
    expenses = c.fetchall()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    data = [['Category', 'Amount', 'Info', 'Date']] + [[expense[1], expense[2], expense[3], expense[4]] for expense in expenses]
    table = Table(data)
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), '#f2f2f2'),
                        ('TEXTCOLOR', (0, 0), (-1, 0), '#000000'),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), '#ffffff'),
                        ('GRID', (0, 0), (-1, -1), 1, '#ffffff'),
                        ('GRID', (0, 0), (-1, 0), 1, '#000000'),
                        ('GRID', (0, -1), (-1, -1), 1, '#000000')])
    table.setStyle(style)

    doc.build([table])
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, attachment_filename='expenses.pdf')


@app.route('/expenses/<int:id>', methods=['DELETE'])
def delete_expense(id):
    c.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    return jsonify({"success": True})

@app.route('/predict/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        Gender = request.form.get('Gender')
        Married = request.form.get('Married')
        Education = request.form.get('Education')
        Self_Employed = request.form.get('Self_Employed')
        ApplicantIncome = request.form.get('ApplicantIncome')
        CoapplicantIncome = request.form.get('CoapplicantIncome')
        LoanAmount = request.form.get('LoanAmount')
        Loan_Amount_Term = request.form.get('Loan_Amount_Term')
        Credit_History = request.form.get('Credit_History')
        Property_Area = request.form.get('Property_Area')

        prediction = utils.preprocessdata(Gender, Married, Education, Self_Employed, ApplicantIncome,
                                           CoapplicantIncome, LoanAmount, Loan_Amount_Term, Credit_History,
                                           Property_Area)

        
        if prediction == 0:
            return render_template('predict.html', prediction="Not Eligible")
        elif prediction == 1:
            return render_template('predict.html', prediction="Eligible")
    return redirect('/prediction/')

@app.route('/prediction/')
def loan_eligibility():
    return render_template('prediction.html')


if __name__ == '__main__':
    app.run(debug=True)
