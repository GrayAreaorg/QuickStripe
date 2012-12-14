from flask import Flask, request, render_template, Response
from werkzeug.datastructures import Headers
from werkzeug import secure_filename
import csv
import datetime
import sys, os
from decimal import Decimal
import StringIO
from flaskext.babel import Babel, format_datetime, get_locale
from dateutil.parser import parse as parse_datetime

ROOT = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder=os.path.join(ROOT, 'public'), static_url_path='/public')
app.config.from_object('config')
#app.debug = True
loc = Babel(app)

def get_locale_from_accept_header():
	langs = request.headers.get('Accept-Language').split(',')
	langs = [l.split(";")[0].replace('-','_') for l in langs]
	return langs[0]
loc.localeselector(get_locale_from_accept_header)

@app.route('/', methods=['GET','POST'])
def upload():
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			outfile = convert_file(file.read())
			file.close()
			headers = Headers()
			bare_filename, extension = os.path.splitext(file.filename)
			headers.add('Content-Disposition', 'attachment', filename='%s.iif' % bare_filename)
			return Response(outfile, mimetype='text/iif', headers=headers)
		else:
			return Response('sorry charlie', mimetype="text/plain")
	return render_template('upload.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def convert_file(infile):
	file_contents = csv.DictReader(infile.splitlines())
	for index, value in enumerate(file_contents.fieldnames):
		file_contents.fieldnames[index] = value.lower().strip().replace(' ','_')

	outfile = StringIO.StringIO()
	transaction_schema = ['!TRNS','DATE','ACCNT','NAME','CLASS','AMOUNT','MEMO']
	split_schema = ['!SPL','DATE','ACCNT','NAME','AMOUNT','MEMO']
	writer = csv.writer(outfile, dialect="excel-tab", doublequote=False, quotechar="'")
	writer.writerow(transaction_schema)
	writer.writerow(split_schema)
	writer.writerow(['!ENDTRNS'])
	def quote(string):
		return '"%s"' % string
	for row in file_contents:
		date = parse_datetime(row['time'])
		charge = Decimal(row['amount'])
		fee = Decimal(row['fee'])
		total_amount = charge - fee
		yield writer.writerow(['TRNS', quote(date), quote('Paypal'), quote(row['card_name']), quote(row['description']), total_amount, quote(row['description'])])
		yield writer.writerow(['SPL',quote(date),quote('Paypal'),quote(row['card_name']),-charge,quote(row['description'])])
		yield writer.writerow(['SPL',quote(date),quote('Paypal'),quote(row['card_name']),'Fee %s' % fee,quote(row['description'])])
		yield writer.writerow(['ENDTRNS'])

	outfile.close()
	return

if __name__ == '__main__':
	app.run()