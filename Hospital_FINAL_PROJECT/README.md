# Hospital Management System

A comprehensive web-based Hospital Management System built with Flask, featuring patient management, doctor scheduling, appointment booking, EHR (Electronic Health Records), billing, pharmacy, lab management, and ML-based disease prediction.

## Features

- **Authentication**: User authentication and authorization
- **Patient Management**: Maintain patient records and profiles
- **Doctor Management**: Manage doctor information and schedules
- **Appointments**: Schedule and manage appointments
- **EHR (Electronic Health Records)**: Maintain digital patient health records
- **Billing**: Generate and manage bills
- **Pharmacy**: Manage medication inventory and prescriptions
- **Lab Management**: Manage lab tests and results
- **ML Prediction**: Machine learning-based disease prediction

## Project Structure

```
hospital-management-system/
├── app.py                 # Main entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── frontend/              # Frontend templates and assets
├── backend/               # Backend logic
│   ├── routes/            # API endpoints
│   ├── controllers/        # Business logic
│   ├── models/            # Database models
│   └── utils/             # Helper functions
├── ml_model/              # Machine learning models
├── database/              # Database schema
└── uploads/               # User uploads
```

## Installation

1. Clone the repository
2. Create a virtual environment
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Configure the database in `config.py`
5. Run the application:
   ```
   python app.py
   ```

## Usage

Access the API endpoints at `http://localhost:5000/`

## License

MIT License
