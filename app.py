from flask import Flask , render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
from flask_login import UserMixin # for creating user Model in Database
from flask_login import login_user, LoginManager, login_required, logout_user, current_user # For the functionality of Login page.
# from wtforms.form import Form
#For creating flask Forms 
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
#Import Bcrypt to hast the passwords
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from flask_migrate import Migrate
import random


app = Flask(__name__)

#Configuring SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///license.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.config['SECRET_KEY']='thisisasecretkey'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

migrate = Migrate(app, db)

#Login Feature 
login_manager = LoginManager() # will allow our app and flask login to work together for logging in.
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))


#Mail Configuration

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = '2021wc86778@wilp.bits-pilani.ac.in'
app.config['MAIL_PASSWORD'] = 'fbzk oqkp cgbr apvj'
app.config['MAIL_DEFAULT_SENDER'] = '2021wc86778@wilp.bits-pilani.ac.in'

mail = Mail(app)


class User(db.Model, UserMixin):
   id = db.Column(db.Integer, primary_key=True)
   username = db.Column(db.String(20), nullable = False, unique= True)
   password = db.Column(db.String(80), nullable = False)

class License(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   product_name = db.Column(db.String(50), nullable=False)
   license_key = db.Column(db.String(100), unique=True, nullable=False)
   purchase_date = db.Column(db.Date, nullable=False)
   expiry_date = db.Column(db.Date, nullable=False)
   owner_name = db.Column(db.String(100), nullable=False)
   owner_email = db.Column(db.String(120), nullable=False)
   company = db.Column(db.String(100), nullable=True)
   category = db.Column(db.String(50), nullable=True)  # e.g., Antivirus, Office Suite, OS, etc.
   status = db.Column(db.String(15), nullable=False, default='Active')
   

   # id = db.Column(db.Integer, primary_key= True)
   # product_name = db.Column(db.String(20), unique=False, nullable=False)
   # expiry_date = db.Column(db.Date, nullable=False)
   # status = db.Column(db.String(15), unique=False, default='Active')
   # owner_email = db.Column(db.String(120), unique=False, nullable=False)
   def __repr__(self):
      return f"<License: {self.product_name} (Status: {self.status})>"
   
   def update_status(self):
      # Automatically update the license status based on expiry date
      if isinstance(self.expiry_date, str):
        self.expiry_date = datetime.strptime(self.expiry_date, "%Y-%m-%d").date()

    # Compare with today's date
      if self.expiry_date < date.today():
        self.status = "Expired"
      else:
        self.status = "Active"


# Flask Registration Form
class RegistrationForm(FlaskForm):
   username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Username"})
   password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Password"})
   submit = SubmitField("Register")

   def validate_username(self, username):
      existing_user_username = User.query.filter_by(username = username.data).first()

      if existing_user_username:
         raise ValidationError("This username already exists. Please choose a different one.")
      
# Flask Login Form
class LoginForm(FlaskForm):
   username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Username"})
   password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder":"Password"})
   submit = SubmitField("Login")




@app.route('/add', methods=["POST"])
def save_license():
   # Get Data from the form
   product_name = request.form['product_name']
   license_key = request.form['license_key']
   purchase_date = datetime.strptime(request.form['purchase_date'], "%Y-%m-%d").date()
   expiry_date = datetime.strptime(request.form['expiry_date'], "%Y-%m-%d").date()
   owner_name = request.form['owner_name']
   owner_email = request.form['owner_email']
   company = request.form['company']
   category = request.form['category']
   # product_name = request.form.get("product_name")
   # expiry_date_str = request.form.get("expiry_date")
   # status = request.form.get("status")
   # email_address = request.form.get("email_address")

   # if not (product_name and expiry_date_str and status and email_address):
   #      return "There was an issue saving the data: missing fields"

   #  # Convert expiry_date to datetime.date
   # try:
   #      expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
   # except ValueError:
   #      return "Invalid date format! Use YYYY-MM-DD."   

   if product_name != '' and status != '' and expiry_date_str and email_address:
      expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
      #Create new License Record
      new_license = License(
         product_name=product_name,
         license_key=license_key,
        purchase_date=purchase_date,
        expiry_date=expiry_date,
        owner_name=owner_name,
        owner_email=owner_email,
        company=company,
        category=category)
      new_license.update_status()

      db.session.add(new_license) #informing DB that we want to save these data
      db.session.commit()  #saving into database#
      return redirect('/license')
   else:
      return "There was an issue saving the data..."

@app.route('/delete/<int:id>')
def delete_license(id):
    lic = License.query.get_or_404(id)
    db.session.delete(lic)
    db.session.commit()
    return redirect(url_for('license'))


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_license(id):
    lic = License.query.get_or_404(id)

    if request.method == 'POST':
        lic.product_name = request.form['product_name']
        lic.expiry_date = request.form['expiry_date']
        lic.owner_email = request.form['owner_email']
        lic.update_status()
        db.session.commit()
        return redirect(url_for('license'))

    return render_template('update_license.html', license=lic)



@app.route('/')
def basepage():
   return render_template('base.html')

@app.route('/homepage')
def home():
   return render_template('homepage.html')

@app.route('/login', methods=['GET','POST'])
def login():
   form = LoginForm()
   if form.validate_on_submit():
      user = User.query.filter_by(username = form.username.data).first()
      if user:
         if bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))

   return render_template('login.html', form=form)

@app.route('/register', methods=['GET','POST'])
def register():
   form= RegistrationForm()

   if form.validate_on_submit():
      hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
      new_user = User(username = form.username.data, password= hashed_password)

      db.session.add(new_user)
      db.session.commit()
      return redirect(url_for('login'))
   
   return render_template('register.html', form=form)

@app.route('/license', methods=["GET"])
def license():
   license= License.query.all()
   for lic in license:
      lic.update_status()
   db.session.commit()
   return render_template('license.html', license= license)

@app.route('/Add_license')
def Add_license():
   return render_template('add_license.html')

@app.route('/dashboard', methods=["GET","POST"])
@login_required
def dashboard():
   # return render_template('dashboard.html')
   today = datetime.today()
   upcoming_threshold = today + timedelta(days=30)

    # Fetch all licenses
   licenses = License.query.all()

    # Counts
   total_licenses = len(licenses)
   active_licenses = License.query.filter_by(status='Active').count()
   expired_licenses = License.query.filter(License.expiry_date < today).count()
   expiring_soon = License.query.filter(
   License.expiry_date.between(today, upcoming_threshold)
   ).count()

    # Licenses expiring soon
   upcoming_licenses = License.query.filter(
        License.expiry_date.between(today, upcoming_threshold)
    ).order_by(License.expiry_date.asc()).all()

   return render_template(
        'dashboard.html',
        total_licenses=total_licenses,
        active_licenses=active_licenses,
        expired_licenses=expired_licenses,
        expiring_soon=expiring_soon,
        upcoming_licenses=upcoming_licenses,
        licenses=licenses,
        now=datetime.now
    )

@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
   logout_user()
   return redirect(url_for('login'))

# For deleting all the data from Database

@app.route('/clear_licenses')
def clear_licenses():
    db.session.query(License).delete()
    db.session.commit()
    return "All license data deleted successfully!"

# ADDING Sample Data

@app.route('/add_sample_data')
def add_sample_data():
    db.session.query(License).delete()

    sample_licenses = [
        License(
            product_name="Microsoft Office 365",
            license_key="MSO365-ABC123-XYZ789",
            purchase_date=date.today() - timedelta(days=200),
            expiry_date=date.today() + timedelta(days=165),
            owner_name="Aman Pathak",
            owner_email="aman.pathak@company.com",
            company="Wipro",
            category="Office Suite"
        ),
        License(
            product_name="Kaspersky Antivirus",
            license_key="KASP-001-987",
            purchase_date=date.today() - timedelta(days=400),
            expiry_date=date.today() - timedelta(days=30),
            owner_name="Ravi Kumar",
            owner_email="ravi.kumar@company.com",
            company="Wipro",
            category="Security"
        ),
        License(
            product_name="Adobe Photoshop",
            license_key="ADOBE-PS-2025-556",
            purchase_date=date.today() - timedelta(days=100),
            expiry_date=date.today() + timedelta(days=120),
            owner_name="Priya Sharma",
            owner_email="priya.sharma@company.com",
            company="Wipro",
            category="Design Tool"
        )
    ]

    for lic in sample_licenses:
        lic.update_status()
        db.session.add(lic)

    db.session.commit()
    return "Sample data added successfully!"


# Adding Data in bulk



@app.route('/add_bulk_data')
def add_bulk_data():
    # Remove old data first

   #  Stops from deleting older Data
   #  db.session.query(License).delete()

    product_names = [
        "Microsoft Office 365", "Adobe Photoshop", "Kaspersky Antivirus", "Windows 11 Pro",
        "AutoCAD 2024", "Visual Studio Enterprise", "AWS Developer Tools", "JetBrains IntelliJ IDEA",
        "Slack Premium", "Zoom Pro", "Figma Pro", "Notion Team", "Trello Business",
        "Canva Pro", "Docker Enterprise", "GitHub Copilot", "Google Workspace",
        "MongoDB Atlas", "Postman Pro", "VMware Workstation", "Anaconda Enterprise",
        "PyCharm Professional", "Node.js Enterprise", "Tableau Creator", "Salesforce Admin",
        "Bitdefender Total Security", "Dropbox Business", "Cisco AnyConnect", "SAP ERP License",
        "Atlassian Jira", "Autodesk Maya", "Unity Pro", "Blender Studio", "VS Code Premium"
    ]

    categories = [
        "Office Suite", "Design Tool", "Security", "Operating System", "Engineering", "Development",
        "Cloud", "Team Collaboration", "Analytics", "Data Science", "Productivity", "Virtualization"
    ]

    companies = [
        "Wipro", "Infosys", "TCS", "Tech Mahindra", "HCL", "Cognizant", "Mindtree", "IBM India"
    ]

    email_addresses = [
        "aman.pathak.198@gmail.com",
        "2021wc86778@wilp.bits-pilani.ac.in"
    ]

    sample_licenses = []

    for i in range(35):
        purchase_date = date.today() - timedelta(days=random.randint(100, 600))
        expiry_date = purchase_date + timedelta(days=random.randint(100, 500))

        license = License(
            product_name=random.choice(product_names),
            license_key=f"KEY-{random.randint(100000,999999)}-{random.randint(1000,9999)}",
            purchase_date=purchase_date,
            expiry_date=expiry_date,
            owner_name="Aman Pathak",
            owner_email=random.choice(email_addresses),
            company=random.choice(companies),
            category=random.choice(categories)
        )

        license.update_status()
        sample_licenses.append(license)

    db.session.bulk_save_objects(sample_licenses)
    db.session.commit()

    return f"{len(sample_licenses)} sample licenses added successfully!"



@app.route('/send-mail')
def send_mail():
   msg = Message(
      subject="Test Mail — License Tracker",
      recipients=["aman.pathak.198@gmail.com"],
      body="This is a test mail!!"
   )
   mail.send(msg)
   return "Mail Sent!"


# Function to send Expiry Alerts

# def send_license_alerts():
#    # print("scheduler triggered at: ", datetime.now()) 
#    with app.app_context():
#       today = datetime.now().date()
#       upcoming = today +timedelta(days = 7)

#       expiring_license = License.query.filter(License.expiry_date <= upcoming).all()

#       for license in expiring_license:
#          msg = Message(

#             subject=f"License Expiry App Alert: {license.product_name}",
#             recipients=["aman.pathak.198@gmail.com","2021wc86778@wilp.bits-pilani.ac.in"],   
#             body=f"Dear User,\n\nYour license for {license.product_name} " f"will expire on {license.expiry_date}. Please renew it in time. Testing!!!"
#             )
#          mail.send(msg)
#          print(f"[INFO] Sent alert for {license.product_name} to {license.owner_email}")

def send_license_alerts():
    with app.app_context():
        today = datetime.now().date()

        users_data = {}  # { email: {expired:[], d7:[], d15:[], d30:[] } }

        licenses = License.query.all()
        for license in licenses:
            expiry = license.expiry_date
            days_left = (expiry - today).days
            email = license.owner_email

            if email not in users_data:
                users_data[email] = {
                    "expired": [],
                    "d7": [],
                    "d15": [],
                    "d30": []
                }

            if days_left < 0:
                users_data[email]["expired"].append(license)
            elif days_left <= 7:
                users_data[email]["d7"].append(license)
            elif days_left <= 15:
                users_data[email]["d15"].append(license)
            elif days_left <= 30:
                users_data[email]["d30"].append(license)

        # Send One Email Per User
        for email, data in users_data.items():

            if not any([data["expired"], data["d7"], data["d15"], data["d30"]]):
                continue  # If no alerts, skip

            message_body = f"Dear User,\n\nHere is your license status summary:\n\n"

            if data["expired"]:
                message_body += "🔥 EXPIRED LICENSES:\n"
                for lic in data["expired"]:
                    message_body += f" - {lic.product_name} (Expired on {lic.expiry_date})\n"
                message_body += "\n"

            if data["d7"]:
                message_body += "🚨 EXPIRING IN 7 DAYS:\n"
                for lic in data["d7"]:
                    message_body += f" - {lic.product_name} (Expires on {lic.expiry_date})\n"
                message_body += "\n"

            if data["d15"]:
                message_body += "🔔 EXPIRING IN 15 DAYS:\n"
                for lic in data["d15"]:
                    message_body += f" - {lic.product_name} (Expires on {lic.expiry_date})\n"
                message_body += "\n"

            if data["d30"]:
                message_body += "📅 EXPIRING IN 30 DAYS:\n"
                for lic in data["d30"]:
                    message_body += f" - {lic.product_name} (Expires on {lic.expiry_date})\n"
                message_body += "\n"

            message_body += "Please take necessary renewal actions.\n\n— License Tracker App"


            # Send email
            msg = Message(
                subject="📌 License Expiry Summary Report",
                recipients=[
                    "aman.pathak.198@gmail.com",
                    "2021wc86778@wilp.bits-pilani.ac.in"
                ],
                body=message_body
            )
            mail.send(msg)
            print(f"[INFO] Summary email sent to {email}")

@app.route('/run-scheduler')
def run_scheduler():
    send_license_alerts()   # call the same function we wrote earlier
    return "Scheduler executed!"
         
scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Kolkata"))
scheduler.add_job(
   func = send_license_alerts,
   trigger = "cron",
   # trigger="interval",
   hour = 8,
   minute=17
   )

scheduler.start()

@app.route('/test-alerts')
def test_alerts():
    send_license_alerts()
    return "✅ License Alert Emails Sent!"


if __name__ == '__main__':
   # Database Configuration
   with app.app_context(): #Needed for DB creation
      db.create_all()
   app.run(debug=True)
