# AI Study Planner

A web application that helps students create personalized study plans using OpenAI's Assistant API.

## Features

- User authentication and registration
- AI-powered study plan generation
- Customizable study schedules
- Progress tracking
- Subject-specific study recommendations

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   SECRET_KEY=your_secret_key_here
   ```
5. Initialize the database:
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```
6. Run the application:
   ```bash
   flask run
   ```

## Application Screenshots

### Home Page
![Home Page](images/1.png)

### Dashboard
![Dashboard](images/2.png)

### Create Study Plan
![Create Plan](images/3.png)

### View Study Plans
![Study Plans](images/4.png)

### Study Plan Details
![Plan Details](images/5.png)

### User Registration
![Registration](images/6.png)

### User Login
![Login](images/7.png)

### Progress Tracking
![Progress](images/8.png)

### Task Management
![Tasks](images/9.png)

## Project Structure

```
ai-study-planner/
├── app/
│   ├── __init__.py
│   ├── models/
│   ├── routes/
│   ├── static/
│   └── templates/
├── config.py
├── requirements.txt
└── run.py
```

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `SECRET_KEY`: Flask secret key for session management
- `DATABASE_URL`: SQLite database URL (default: sqlite:///app.db)