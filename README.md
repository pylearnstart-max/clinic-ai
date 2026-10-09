\# ClinicAI – Clinic Management REST API



A Flask-based REST API for managing patients, doctors, and appointments. This project demonstrates Python backend development using a layered architecture, database operations, and automated testing.



\## Features



\* Patient management APIs

\* Doctor management APIs

\* Appointment management APIs

\* Create, read, update, and delete (CRUD) operations

\* Input validation and error handling

\* Database connectivity using Python

\* Automated unit and API tests



\## Tech Stack



\* \*\*Language:\*\* Python

\* \*\*Backend:\*\* Flask

\* \*\*Database Connectivity:\*\* pyodbc

\* \*\*Configuration:\*\* python-dotenv

\* \*\*Testing:\*\* pytest, pytest-cov

\* \*\*Version Control:\*\* Git and GitHub

\* \*\*API Testing:\*\* Postman



\## Project Architecture



The application follows a layered structure:



\* \*\*API Layer:\*\* Handles HTTP requests and responses.

\* \*\*Service Layer:\*\* Contains business logic and validation.

\* \*\*Repository Layer:\*\* Handles data access operations.

\* \*\*Model Layer:\*\* Represents patient, doctor, and appointment data.

\* \*\*Database Layer:\*\* Manages database connectivity.



\## Project Structure



```text

clinic-ai/

├── app/

│   ├── api/

│   ├── models/

│   ├── repositories/

│   └── services/

├── tests/

├── db.py

├── run.py

├── requirements.txt

├── .gitignore

└── README.md

```



\## Setup and Installation



\### 1. Clone the repository



```bash

git clone https://github.com/pylearnstart-max/clinic-ai.git

cd clinic-ai

```



\### 2. Create a virtual environment



```bash

python -m venv venv

```



Activate it on Windows PowerShell:



```powershell

.\\venv\\Scripts\\Activate.ps1

```



\### 3. Install dependencies



```bash

pip install -r requirements.txt

```



\### 4. Configure the database



Configure the required database connection settings for your environment. Keep credentials and secrets in a local `.env` file and never commit that file to GitHub.



\### 5. Run the application



```bash

python run.py

```



\## Running Tests



Run the test suite:



```bash

pytest

```



Run tests with coverage:



```bash

pytest --cov=app --cov-report=term-missing

```



\*\*Latest test result:\*\* 230 tests passed with 100% measured code coverage in the tested project modules.



\## Learning Outcomes



\* Building REST APIs using Flask

\* Implementing CRUD operations

\* Organizing backend code with a layered architecture

\* Separating business logic from database access

\* Writing automated tests using pytest

\* Measuring test coverage

\* Managing source code with Git and GitHub



\## Author



GitHub: \[pylearnstart-max](https://github.com/pylearnstart-max)



