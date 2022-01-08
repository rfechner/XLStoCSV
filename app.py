
import pandas as pd
import os
import zipfile
from io import BytesIO
from flask import Flask, request, render_template, send_file
from flask_swagger_ui import get_swaggerui_blueprint
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap

from wtforms import URLField
from wtforms.validators import DataRequired


from werkzeug.utils import secure_filename
from config import config

ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

config_name = os.environ.get("APP_MODE") or "development"

app = Flask(__name__)
app.config.from_object(config[config_name])

bootstrap = Bootstrap(app)


SWAGGER_URL = "/api/docs"
API_URL = "/static/swagger.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "XLStoCSV"
    }
)



app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class StartForm(FlaskForm):
    data_url = URLField('URL to xls file', validators=[DataRequired()], description='Paste URL to a excel file containing data-sheets')



@app.route('/', methods=['GET', 'POST'])
def index():
    logo = './static/resources/MatOLab-Logo.svg'
    start_form = StartForm()
    return render_template("index.html", logo=logo, start_form=start_form)

@app.route("/api", methods=["GET", "POST"])
def api():
    if request.method == 'POST':
        files = request.files.getlist("files")
        memory_file = BytesIO()

        # for each input file, create sheets, for each sheet, try to add csv to zipfile

        with zipfile.ZipFile(memory_file, 'w') as zf:
            for file in files:
                if not file.filename.endswith(".xls"):
                    continue

                prefix = secure_filename(file.filename.removesuffix(".xls"))
                excel_file = pd.ExcelFile(file)

                for sheetname in excel_file.sheet_names:

                    try:
                        df = excel_file.parse(sheet=sheetname)
                        plain_text = df.to_csv(index=False)

                        filename = secure_filename(prefix + "_" + sheetname + ".csv")
                        zf.writestr(zinfo_or_arcname=filename, data=plain_text)

                    except:
                        # sometimes, excel sheets can't be turned into csv files,e.g. when
                        # the excel sheet contains a diagram. In this case, omit the current sheet
                        continue

        memory_file.seek(0)
        return send_file(memory_file, attachment_filename='result.zip', as_attachment=True)

    return render_template("index.html")
