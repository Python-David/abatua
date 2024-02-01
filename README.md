# Abatua E-commerce Application

## Overview
Abatua is a sophisticated and feature-rich e-commerce application developed using the Django framework. It offers a seamless and intuitive shopping experience, incorporating advanced functionalities like product categorization, user authentication, and a dynamic shopping cart. This application represents a commitment to modern web development practices and user-centric design.

## Key Features

- **User Authentication**: Secure login and registration functionality.
- **Product Categorization**: Efficient organization of products into categories.
- **Dynamic Shopping Cart**: Interactive and user-friendly shopping cart system.
- **Responsive Design**: Optimized for a variety of devices and screen sizes.

## Directory Structure Overview

- `abatua/`: Main Django project folder with settings, URLs, and views.
- `accounts/`: Modules for user account management.
- `carts/`: Shopping cart functionality and logic.
- `category/`: Handling of product categories.
- `store/`: Core application logic for product listing and details.
- `templates/`: HTML templates for the application’s frontend.
- `static/`, `media/`: Static and media files for UI elements and user uploads.
- `manage.py`: Utility script for administrative tasks.

## Installation and Setup

1. **Clone the Repository**:

   - ```git clone [Repository URL]```
   - ```cd [Repository Name]```
  

2. **Set up a virtual environment** (optional but recommended):

   - ```python -m venv venv```
   - ```source venv/bin/activate``` # On Windows use ```venv\Scripts\activate```
   

3. **Install dependencies**:
   - ```pip install -r requirements.txt```


4. **Initialize the database**:
   - ```python manage.py makemigrations```
   - ```python manage.py migrate```


5. **Run the server**:
   - ```python manage.py runserver```

   
6. Access the application at ```http://localhost:8000/```.

## Continuous Integration with GitHub Actions

We employ GitHub Actions for automated linting, ensuring high code quality and consistency:

- **Black for Code Formatting**: Validates that the Python code adheres to our formatting standards.
- **isort for Import Order**: Checks the order of imports for cleanliness and uniformity.

**Running Checks Locally**: To contribute, please ensure code passes these checks:

- ```black .```
- ```isort .```

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
