# Abatua E-commerce Application

## Overview
Abatua is a robust and feature-rich e-commerce application built using the Django framework. This application is designed to provide a smooth and intuitive shopping experience, featuring a variety of products, categories, user accounts, and shopping cart functionality.

## Directory Structure

- `abatua/`: The main Django project directory.
  - `settings.py`: Contains settings/configuration for the project.
  - `urls.py`: Project-level URL declarations.
  - `views.py`: Project-level views.
  - `static/`: Contains static files (CSS, JS, images).
  - `media/`: Media files uploaded by users (e.g., product photos).
- `accounts/`: User account management (login, registration).
- `carts/`: Shopping cart functionality.
- `category/`: Product category management.
- `store/`: Core application logic for product listing and details.
- `templates/`: HTML templates for the application.
- `manage.py`: Django's command-line utility for administrative tasks.
- `db.sqlite3`: SQLite database file.

## Features

- User authentication (login and registration).
- Product listing with categorization.
- Shopping cart functionality.
- Responsive design for various devices.

## Installation

To get the application running locally:

1. **Clone the repository**

   - `git clone [URL of the repository]`

   - `cd [repository name]`
  

2. **Set up a virtual environment** (optional but recommended):

   - `python -m venv venv`
   
   - `source venv/bin/activate` # On Windows use `venv\Scripts\activate`
   

3. **Install dependencies**:
   - `pip install -r requirements.txt`


4. **Initialize the database**:
   - `python manage.py makemigrations`
   - `python manage.py migrate`


5. **Run the server**:
   - `python manage.py runserver`



6. Access the application at `http://localhost:8000/`.

## Contributing

Contributions to improve Abatua are welcome. Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

Copyright (c) 2024 Python David

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
