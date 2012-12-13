from flask import Flask, request, render_template, Response
from werkzeug.datastructures import Headers
from werkzeug import secure_filename
import csv
import datetime
import sys, os
from decimal import Decimal
import StringIO
app = Flask(__name__)
app.config.from_object('config')

@app.route('/', methods=['GET','POST'])
def upload():
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			outfile = convert_file(file)
			headers = Headers()
			bare_filename, extension = os.path.splitext(file.filename)
			headers.add('Content-Disposition', 'attachment', filename='%s.iif' % bare_filename)
			return Response(outfile, mimetype='text/iif', headers=headers)
	return render_template('upload.html')

def allowed_file(filename):
	bare_filename, extension = os.path.splitext(file.filename)
	return extension in app.config['ALLOWED_EXTENSIONS']

def convert_file(infile):
	file_contents = csv.DictReader(infile)
	for index, value in enumerate(file_contents.fieldnames):
		file_contents.fieldnames[index] = value.lower().strip().replace(' ','_')

	outfile = StringIO.StringIO()
	transaction_schema = ['!TRNS','DATE','ACCNT','NAME','CLASS','AMOUNT','MEMO']
	split_schema = ['!SPL','DATE','ACCNT','NAME','AMOUNT','MEMO']
	writer = csv.writer(outfile, dialect="excel-tab")
	writer.writerow(transaction_schema)
	writer.writerow(split_schema)
	writer.writerow(['!ENDTRNS'])
	for row in file_contents:
		date = datetime.datetime.strptime(row['time'], '%Y-%m-%d %H:%M').strftime('%m/%d/%Y')
		charge = Decimal(row['amount'])
		fee = Decimal(row['fee'])
		total_amount = charge - fee
		writer.writerow(['TRNS', date, 'gaffta.org', row['card_name'], row['description'], total_amount, row['description']])
		writer.writerow(['SPL',date,'gaffta.org',row['card_name'],-charge,row['description']])
		writer.writerow(['SPL',date,'gaffta.org',row['card_name'],'Fee %s' % fee,row['description']])
		writer.writerow(['ENDTRNS'])

	outfile.seek(0)
	return outfile

if __name__ == '__main__':
	app.run()