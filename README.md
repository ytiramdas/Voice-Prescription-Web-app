# Voice-Prescription-Web-app

An application to write formatted prescriptions based on dictation from the doctor.

## Setting up the Environment 🛠

* Clone the repository
  * Copy the following command in the terminal/command-line: `git clone https://github.com/Yashi1011/Voice-Prescription-Web-app.git`
* Move to the cloned directory
* Create a virtual environment
  * Make sure you install the `python3-venv` module 
  * `python -m venv venv` - for windows
  * `python3 -m venv venv` - for ubuntu
* Activate the virtual environment
  * `venv\Scripts\activate` - for windows
  * `venv\bin\activate` - for ubuntu
* Install the dependancies
  * `pip install requirements.txt`
* You can now run the code
  * `python run.py`

## Accessing database
* Go to python shell in Voice-Prescription-Web-app directory
* `from voiceprescription import db, create_app`
* `app = create_app()`
* `app.app_context().push()`
* `db.create_all()` - when you add a table)
* You can create sample data using [data.py file](/voiceprescription/data.py).

NOTE: While creating prescription internet should be ON as I used [Annyang](https://www.talater.com/annyang/) JS files form internet for speech recognition.
