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

python -m pytest

```



Run tests with coverage:



```bash

python -m pytest --cov=app --cov-report=term-missing

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

\## API Documentation



\*\*Base URL:\*\* `http://127.0.0.1:5000`



\### Patient Endpoints



| Method | Endpoint                     | Description       |

| ------ | ---------------------------- | ----------------- |

| POST   | `/api/patients`              | Create a patient  |

| GET    | `/api/patients`              | Get all patients  |

| GET    | `/api/patients/<patient\_id>` | Get patient by ID |

| PUT    | `/api/patients/<patient\_id>` | Update patient    |

| DELETE | `/api/patients/<patient\_id>` | Delete patient    |



\### Doctor Endpoints



| Method | Endpoint               | Description      |

| ------ | ---------------------- | ---------------- |

| POST   | `/doctors`             | Create a doctor  |

| GET    | `/doctors`             | Get all doctors  |

| GET    | `/doctors/<doctor\_id>` | Get doctor by ID |

| PUT    | `/doctors/<doctor\_id>` | Update doctor    |

| DELETE | `/doctors/<doctor\_id>` | Delete doctor    |



\### Appointment Endpoints



| Method | Endpoint                         | Description           |

| ------ | -------------------------------- | --------------------- |

| POST   | `/appointments`                  | Book an appointment   |

| GET    | `/appointments`                  | Get all appointments  |

| GET    | `/appointments/<appointment\_id>` | Get appointment by ID |

| PUT    | `/appointments/<appointment\_id>` | Update appointment    |

| DELETE | `/appointments/<appointment\_id>` | Delete appointment    |



\### Example: Create a Doctor



\*\*POST\*\* `/doctors`



Request JSON:



```json

{

&#x20; "name": "Dr. Ravi Kumar",

&#x20; "specialization": "Cardiology",

&#x20; "phone": "9876543210",

&#x20; "email": "ravi@example.com",

&#x20; "consultation\_fee": 500

}

```



Successful response: `201 Created`



```json

{

&#x20; "message": "Doctor added successfully"

}

```



\### HTTP Status Codes



\* `200 OK` — Request completed successfully.

\* `201 Created` — Resource created successfully.

\* `400 Bad Request` — Invalid input or validation error.

\* `404 Not Found` — Requested resource not found.

\* `500 Internal Server Error` — Unexpected server error.



\### API Testing with Postman



Use Postman to test the endpoints. For POST and PUT requests, select \*\*Body → raw → JSON\*\*, provide the request data, and verify the response status and body.





