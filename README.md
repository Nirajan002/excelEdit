# Excel Django App 📊

A Django-based web app to upload, edit, and analyze Excel files with summary stats like totals and averages.

## Features
- Excel file upload
- View and edit table
- view totals/averages
- Export edited Excel

## Setup

```bash
git clone https://github.com/Nirajan002/excelEdit.git
cd excelEdit
python -m venv venv
venv\Scripts\activate #on mac: source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
