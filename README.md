# Flask Backend - Project Documentation

## Overview

This repository contains the backend implementation for a web application using Flask. The backend provides RESTful APIs
for user authentication, quest tracking, and other core functionalities. It is designed to return data only, leaving UI
handling to the frontend.

The app is deployed on AWS Elastic Beanstalk with a configured CI/CD pipeline for manual or automatic deployment.

For static files, AWS S3 with CloudFront is used.
## Features

- User JWT-based authentication
- User profile information update
- Image and video uploads to AWS S3
- Quest tracking system with score, completion status, time, and rating
- User quest history
- Real-time user progress updates using Websockets

## Technologies Used

- **Flask** - Web framework for building RESTful APIs
- **MongoDB** - NoSQL database for storing users and quests
- **Pydantic** - Data validation and serialization
- **JWT (JSON Web Token)** - Secure user authentication
- **flask_socketio** - Real-time updates
- **boto3** - AWS SDK
- **flask-restx** - API Swagger documentation


## Installation

### Prerequisites

In order to run the application you need:

- Python 3.12+
- MongoDB database configured
- AWS S3 bucket for static files upload (with or without CloudFront distribution)

### Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/nastyapetrunia/quest-platform-server.git
   cd quest-platform-server
   ```

2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Create a `.env` file in the root directory with the following:
   ```ini
   MONGO_URI=
   MONGO_DB_NAME=
   JWT_SECRET_KEY=
   AWS_ACCESS_KEY_ID=
   AWS_SECRET_ACCESS_KEY=
   S3_BUCKET_RESOURCES=
   S3_REGION=
   CLOUDFRONT_DISTRIBUTION=
   ```

## Running the Application

Start the Flask server with:

```sh
flask run --host=0.0.0.0 --port=8000
```

## Deployment

For deployment to AWS you need:

- AWS account and user with correct permissions
- AWS Elastic Beanstalk application
- Configure GitHub Action variables and secrets
- Manually trigger the aws_deploy.yml workflow or set up automatic deployment

## License

This project is licensed under the MIT License.

## Contact

For questions or contributions, contact [nastyagr217@gmailcom](mailto:nastyagr217@gmailcom).

