# Klaw App Admin Side Documentation

This documentation covers the **Admin Side** of the Klaw app, a Django REST Framework (DRF) project that connects to a MongoDB database using Djongo. The admin side manages courses, blogs, notifications, user statuses, and contact form submissions, all interacting with a shared MongoDB database (`klaw_db_dev`). Below, you’ll find setup instructions, model details, and a detailed breakdown of each API endpoint, including inputs, outputs, and logic.

## 1. Project Overview

The Klaw app’s admin side is a Django project that provides APIs for:
- **Admin Authentication**: Login for superusers using JWT.
- **Course Management**: Create, update, delete, and toggle course status (draft/published).
- **Blog Management**: Create, list, edit, toggle status, and delete blogs.
- **Notification Management**: Send push notifications and view notification history.
- **User Management**: List users, toggle user status, and view user details.
- **Contact Form**: Handle contact form submissions.

Both the admin and app sides share the same MongoDB database, with the admin side accessing the `mobile_api_appuser` collection for user management.

## 2. Setup Instructions

### Prerequisites
- **Python**: Python 3.10.18
- **MongoDB**: A running MongoDB instance (e.g., local or MongoDB Atlas)
- **Dependencies**: Install required packages using `pip install -r requirements.txt`. Key packages include:
anyio==4.9.0
asgiref==3.8.1
blinker==1.9.0
CacheControl==0.14.3
cachetools==5.5.2
certifi==2025.6.15
cffi==1.17.1
charset-normalizer==3.4.2
click==8.2.1
cryptography==45.0.5
Django==3.2.25
django-cors-headers==4.3.1
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
djongo==1.3.6
exceptiongroup==1.3.0
firebase-admin==6.9.0
Flask==3.1.1
google-api-core==2.25.1
google-api-python-client==2.175.0
google-auth==2.40.3
google-auth-httplib2==0.2.0
google-cloud-core==2.4.3
google-cloud-firestore==2.21.0
google-cloud-storage==3.1.1
google-crc32c==1.7.1
google-resumable-media==2.7.2
googleapis-common-protos==1.70.0
grpcio==1.73.1
grpcio-status==1.73.1
h11==0.16.0
h2==4.2.0
hpack==4.1.0
httpcore==1.0.9
httplib2==0.22.0
httpx==0.28.1
hyperframe==6.1.0
idna==3.10
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.2
msgpack==1.1.1
numpy==1.26.4
pillow==11.3.0
proto-plus==1.26.1
protobuf==6.31.1
pyasn1==0.6.1
pyasn1_modules==0.4.2
pycparser==2.22
PyJWT==2.8.0
pymongo==3.12.3
pyparsing==3.2.3
python-decouple==3.8
python-dotenv==1.1.1
pytz==2025.2
requests==2.32.4
requests-toolbelt==1.0.0
rsa==4.9.1
sniffio==1.3.1
sqlparse==0.2.4
typing_extensions==4.14.0
uritemplate==4.2.0
urllib3==2.5.0
Werkzeug==3.1.3
### Installation
1. **Clone the Project**:
   ```bash
   git clone 
   cd klaw_app
   ```

2. **Set Up Environment Variables**:
   Create a `.env` file in the project root:
GOOGLE_APPLICATION_CREDENTIALS=/home/ubuntu/desktop/admin/credentials/klaw-18480-firebase-adminsdk-fbsvc-298b5624b8.json
AI_SERVER=http://172.31.9.4:5000

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MongoDB**:
   Update `settings.py` with your MongoDB connection string:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'djongo',
           'NAME': 'klaw_db_dev',
           'CLIENT': {
               'host': 'mongodb://admin:developer2025@13.204.52.164:27017',
               'retryWrites': True,
               'w': 'majority',
           },
       }
   }
   ```

5. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the Server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the API**:
   The admin APIs are available at `http://localhost:8000/api/admin/`.

### Directory Structure
- `klaw_app/`: Project root
  - `settings.py`: Configuration for Django, DRF, JWT, MongoDB, and CORS.
  - `urls.py`: Main URL configuration routing to `admin_panel.urls`.
  - `admin_panel/`: App containing models, serializers, views, and URLs.
    - `models.py`: Defines MongoDB models for courses, blogs, notifications, etc.
    - `serializers.py`: Serializers for data validation and serialization.
    - `views.py`: API views for handling requests.
    - `urls.py`: URL patterns for admin APIs.

## 3. Database Configuration
The project uses MongoDB with Djongo as the ORM engine. The database `klaw_db_dev` is hosted at `mongodb://admin:developer2025@13.204.52.164:27017`. Key collections include:
- `admin_panel_coursebasicinfo`
- `admin_panel_courseoutcome`
- `admin_panel_coursesyllabus`
- `admin_panel_coursequestion`
- `admin_panel_coursematerial`
- `admin_panel_course`
- `admin_panel_contact`
- `admin_panel_blog`
- `admin_panel_notification`
- `mobile_api_appuser` (shared with app side for user data)

## 4. Models
The admin side defines the following MongoDB models in `models.py`:

1. **CourseBasicInfo**: Stores basic course details.
   - Fields: `_id` (ObjectId), `course_name`, `course_code` (unique), `year`, `branch`, `semester`, `group`, `created_at`, `updated_at`.

2. **CourseOutcome**: Stores course outcomes.
   - Fields: `_id` (ObjectId), `course_code`, `short_form`, `outcome`, `created_at`, `updated_at`.

3. **CourseSyllabus**: Stores syllabus items for a course.
   - Fields: `_id` (ObjectId), `course_code`, `syllabus_item`, `created_at`, `updated_at`.

4. **CourseQuestion**: Stores questions for a course.
   - Fields: `_id` (ObjectId), `course_code`, `question`, `created_at`, `updated_at`.

5. **CourseMaterial**: Stores course material files.
   - Fields: `_id` (ObjectId), `course_code`, `file_path`, `file_type`, `created_at`, `updated_at`.

6. **Course**: Tracks course status (draft/published).
   - Fields: `_id` (ObjectId), `course_code` (unique), `status` (draft/published), `created_at`, `updated_at`.

7. **Contact**: Stores contact form submissions.
   - Fields: `_id` (ObjectId), `name`, `email`, `phone`, `how_did_you_find_us`, `created_at`, `updated_at`.

8. **Blog**: Stores blog posts.
   - Fields: `title`, `author`, `category`, `html_code`, `created_at`, `status` (draft/publish).

9. **Notification**: Stores push notification records.
   - Fields: `title`, `message`, `created_at`.

10. **AdminAppUser**: Maps to the shared `mobile_api_appuser` collection for user management.
    - Fields: `id` (Integer), `full_name`, `phone_number`, `email`, `year_of_study`, `college`, `department`, `university`, `blood_group`, `profile_pic`, `subscription_plan`, `status` (accepted/rejected).

## 5. API Endpoints

Below is a detailed breakdown of each API endpoint, including the endpoint URL, HTTP method, inputs, outputs, and logic. All APIs except `/login/` and `/contact/` require JWT authentication (`IsAuthenticated`). The `/login/` and `/contact/` endpoints allow unauthenticated access (`AllowAny`).

### 5.1 Admin Login
- **Endpoint**: `POST /api/admin/login/`
- **Permission**: `AllowAny`
- **Description**: Authenticates an admin user (superuser) and returns JWT access and refresh tokens.
- **Input**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Output**:
  - **Success (200)**:
    ```json
    {
      "access": "jwt-access-token",
      "refresh": "jwt-refresh-token"
    }
    ```
  - **Error (401)**:
    ```json
    {"detail": "Invalid credentials or not an admin user."}
    ```
  - **Error (400)**:
    ```json
    {"username": ["This field is required."]}
    ```
- **Logic**:
  1. Validate input using `AdminLoginSerializer`.
  2. Authenticate user with Django’s `authenticate` function.
  3. Check if the user is a superuser.
  4. Generate JWT tokens using `RefreshToken.for_user`.
  5. Log success or failure and return response.

### 5.2 Course Basic Info
- **Endpoints**:
  - `POST /api/admin/course-basic-info/`: Create a new course.
  - `PATCH /api/admin/course-basic-info/<course_code>/`: Update an existing course’s basic info.
- **Permission**: `IsAuthenticated`
- **Description**: Manages basic course information (e.g., name, code, year).
- **Input (POST)**:
  ```json
  {
    "course_name": "string",
    "course_code": "string",
    "year": integer,
    "branch": "string",
    "semester": integer,
    "group": "string"
  }
  ```
- **Input (PATCH)**:
  ```json
  {
    "course_name": "string",
    "year": integer,
    "branch": "string",
    "semester": integer,
    "group": "string"
  }
  ```
- **Output**:
  - **Success (201 for POST, 200 for PATCH)**:
    ```json
    {
      "course_code": "string",
      "message": "successful"
    }
    ```
  - **Error (400)**:
    ```json
    {"course_code": ["Course code already exists."]}
    ```
  - **Error (403)**:
    ```json
    {"error": "Only draft courses can be edited."}
    ```
  - **Error (404)**:
    ```json
    {"error": "Course not found."}
    ```
- **Logic**:
  - **POST**: Validate input, ensure unique `course_code`, save to `CourseBasicInfo`, and create a `Course` entry with `status='draft'`.
  - **PATCH**: Check if the course exists and is in `draft` status. Prevent `course_code` updates. Update fields and save.

### 5.3 Course Outcomes
- **Endpoints**:
  - `POST /api/admin/course-outcomes/`: Add outcomes for a course.
  - `PATCH /api/admin/course-outcomes/<course_code>/`: Update outcomes.
- **Permission**: `IsAuthenticated`
- **Description**: Manages course outcomes (e.g., learning objectives).
- **Input (POST)**:
  ```json
  {
    "course_code": "string",
    "outcomes": [
      {"short_form": "string", "outcome": "string"},
      {"short_form": "string", "outcome": "string"}
    ]
  }
  ```
- **Input (PATCH)**:
  ```json
  {
    "outcomes": [
      {"short_form": "string", "outcome": "string"},
      {"short_form": "string", "outcome": "string"}
    ]
  }
  ```
- **Output**:
  - **Success (201 for POST, 200 for PATCH)**:
    ```json
    {
      "course_code": "string",
      "message": "successful"
    }
    ```
  - **Error (400)**:
    ```json
    {"error": "Course code is required."}
    ```
  - **Error (403)**:
    ```json
    {"error": "Only draft courses can be edited."}
    ```
  - **Error (404)**:
    ```json
    {"error": "Course not found."}
    ```
- **Logic**:
  - **POST**: Validate `course_code` and outcomes. Save each outcome to `CourseOutcome`.
  - **PATCH**: Check if course is in `draft` status. Delete existing outcomes, validate new outcomes for uniqueness, and save.

### 5.4 Course Syllabus
- **Endpoints**:
  - `POST /api/admin/course-syllabus/`: Add syllabus items.
  - `PATCH /api/admin/course-syllabus/<course_code>/`: Update syllabus items.
- **Permission**: `IsAuthenticated`
- **Description**: Manages course syllabus items.
- **Input (POST)**:
  ```json
  {
    "course_code": "string",
    "syllabus_items": ["string", "string"]
  }
  ```
- **Input (PATCH)**:
  ```json
  {
    "syllabus_items": ["string", "string"]
  }
  ```
- **Output**:
  - **Success (201 for POST, 200 for PATCH)**:
    ```json
    {
      "course_code": "string",
      "message": "successful"
    }
    ```
  - **Error (400)**:
    ```json
    {"error": "At least one syllabus item is required."}
    ```
  - **Error (403)**:
    ```json
    {"error": "Only draft courses can be edited."}
    ```
  - **Error (404)**:
    ```json
    {"error": "Course not found."}
    ```
- **Logic**:
  - **POST**: Validate `course_code` and syllabus items. Save each item to `CourseSyllabus`.
  - **PATCH**: Check if course is in `draft` status. Delete existing syllabus items, validate new items for uniqueness, and save.

### 5.5 Course Questions
- **Endpoints**:
  - `POST /api/admin/course-questions/`: Add questions for a course.
  - `PATCH /api/admin/course-questions/<course_code>/`: Update questions.
- **Permission**: `IsAuthenticated`
- **Description**: Manages course questions (e.g., study questions).
- **Input (POST)**:
  ```json
  {
    "course_code": "string",
    "questions": ["string", "string"]
  }
  ```
- **Input (PATCH)**:
  ```json
  {
    "questions": ["string", "string"]
  }
  ```
- **Output**:
  - **Success (201 for POST, 200 for PATCH)**:
    ```json
    {
      "course_code": "string",
      "message": "successful"
    }
    ```
  - **Error (400)**:
    ```json
    {"error": "At least one question is required."}
    ```
  - **Error (403)**:
    ```json
    {"error": "Only draft courses can be edited."}
    ```
  - **Error (404)**:
    ```json
    {"error": "Course not found."}
    ```
- **Logic**:
  - **POST**: Validate `course_code` and questions. Save each question to `CourseQuestion`.
  - **PATCH**: Check if course is in `draft` status. Delete existing questions, validate new questions for uniqueness, and save.

### 5.6 Course Materials
- **Endpoints**:
  - `POST /api/admin/course-materials/`: Add course materials.
  - `PATCH /api/admin/course-materials/<course_code>/`: Update materials.
- **Permission**: `IsAuthenticated`
- **Description**: Manages course material files (PDF or TXT, max 100MB).
- **Input (POST)**:
  - Content-Type: `multipart/form-data`
  ```json
  {
    "course_code": "string",
    "status": "draft" or "published",
    "files": [file1, file2],
    "file_type_0": "string",
    "file_type_1": "string"
  }
  ```
- **Input (PATCH)**:
  - Content-Type: `multipart/form-data`
  ```json
  {
    "files": [file1, file2],
    "file_type_0": "string",
    "file_type_1": "string"
  }
  ```
- **Output**:
  - **Success (201 for POST, 200 for PATCH)**:
    ```json
    {
      "course_code": "string",
      "message": "successful"
    }
    ```
  - **Error (400)**:
    ```json
    {"error": "At least one file is required."}
    ```
  - **Error (403)**:
    ```json
    {"error": "Only draft courses can be edited."}
    ```
  - **Error (404)**:
    ```json
    {"error": "Course not found."}
    ```
- **Logic**:
  - **POST**: Validate `course_code` and files (PDF/TXT, <100MB). Save files to `media/` and create `CourseMaterial` entries. Create or update `Course` with status.
  - **PATCH**: Check if course is in `draft` status. Delete existing materials, validate new files for unique names, save to `media/`, and create new `CourseMaterial` entries.

### 5.7 Process Course
- **Endpoint**: `POST /api/admin/process/`
- **Permission**: `IsAuthenticated` (superuser only)
- **Description**: Sends course data to an external AI server for processing.
- **Input**:
  ```json
  {
    "course_code": "string"
  }
  ```
- **Output**:
  - **Success (200)**:
    ```json
    {
      "course_code": "string",
      "status": "processing_started",
      "results": {
        "basic_info": "success",
        "course_outcome": "success",
        "syllabus": "success",
        "questions": "success",
        "materials": "success",
        "trigger": "success"
      }
    }
    ```
  - **Error (400)**:
    ```json
    {"error": "Course code is required."}
    ```
  - **Error (403)**:
    ```json
    {"error": "Only admin users can process courses."}
    ```
  - **Error (404)**:
    ```json
    {"error": "Course not found."}
    ```
- **Logic**:
  1. Verify superuser status.
  2. Check if course exists and is in `draft` status.
  3. Send `CourseBasicInfo`, `CourseOutcome`, `CourseSyllabus`, `CourseQuestion`, and `CourseMaterial` data to the AI server (`AI_SERVER` URL).
  4. Trigger final processing on the AI server.
  5. Return results for each step or error if any step fails.

### 5.8 Delete Course
- **Endpoint**: `DELETE /api/admin/course-delete/?course_code=<course_code>`
- **Permission**: `IsAuthenticated`
- **Description**: Deletes a course and all related data.
- **Input**: Query parameter `course_code`.
- **Output**:
  - **Success (200)**:
    ```json
    {"detail": "Course <course_code> and related data deleted successfully."}
    ```
  - **Error (400)**:
    ```json
    {"error": "Course code is required."}
    ```
  - **Error (500)**:
    ```json
    {"error": "Internal server error message"}
    ```
- **Logic**:
  1. Validate `course_code`.
  2. Delete all related records from `CourseBasicInfo`, `CourseOutcome`, `CourseSyllabus`, `CourseQuestion`, `CourseMaterial`, and `Course`.

### 5.9 Toggle Course Status
- **Endpoint**: `POST /api/admin/toggle-course/<course_code>/`
- **Permission**: `IsAuthenticated` (superuser only)
- **Description**: Toggles course status between `draft` and `published`.
- **Input**: None (uses `course_code` from URL).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "course_code": "string",
      "status": "draft" or "published",
      "message": "successful"
    }
    ```
  - **Error (403)**:
    ```json
    {"error": "Only admin users can toggle course status."}
    ```
  - **Error (404)**:
    ```json
    {"detail": "Course not found."}
    ```
- **Logic**:
  1. Verify superuser status.
  2. Find course by `course_code`.
  3. Toggle `status` (`draft` ↔ `published`) and save.

### 5.10 Get Courses
- **Endpoint**: `GET /api/admin/get-courses/?status=<draft|published>`
- **Permission**: `IsAuthenticated`
- **Description**: Retrieves courses filtered by status.
- **Input**: Query parameter `status` (draft or published).
- **Output**:
  - **Success (200)**:
    ```json
    [
      {
        "course_code": "string",
        "status": "draft" or "published",
        "basic_info": {...},
        "outcomes": [...],
        "syllabus": [...],
        "questions": [...],
        "materials": [...],
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
    ```
  - **Error (400)**:
    ```json
    {"error": "Invalid status filter. Use 'draft' or 'published'."}
    ```
- **Logic**:
  1. Validate `status` query parameter.
  2. Fetch courses with matching status.
  3. Serialize with `CourseDetailSerializer` to include related data.

### 5.11 Course Detail
- **Endpoint**: `GET /api/admin/courses/<course_code>/`
- **Permission**: `IsAuthenticated`
- **Description**: Retrieves detailed information for a specific course.
- **Input**: None (uses `course_code` from URL).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "course_code": "string",
      "status": "draft" or "published",
      "basic_info": {...},
      "outcomes": [...],
      "syllabus": [...],
      "questions": [...],
      "materials": [...],
      "created_at": "datetime",
      "updated_at": "datetime"
    }
    ```
  - **Error (404)**:
    ```json
    {"detail": "Course not found."}
    ```
- **Logic**:
  1. Fetch course by `course_code`.
  2. Serialize with `CourseDetailSerializer` to include all related data.

### 5.12 Contact Form
- **Endpoint**: `POST /api/admin/contact/`
- **Permission**: `AllowAny`
- **Description**: Handles contact form submissions.
- **Input**:
  ```json
  {
    "name": "string",
    "email": "string",
    "phone": "string",
    "how_did_you_find_us": "string"
  }
  ```
- **Output**:
  - **Success (201)**:
    ```json
    {"message": "Contact entry successfully submitted!"}
    ```
  - **Error (400)**:
    ```json
    {"email": ["Enter a valid email address."]}
    ```
- **Logic**:
  1. Validate input with `ContactSerializer`.
  2. Save to `Contact` model.

### 5.13 Create Blog
- **Endpoint**: `POST /api/admin/create-blog/`
- **Permission**: `IsAuthenticated`
- **Description**: Creates a new blog post.
- **Input**:
  ```json
  {
    "title": "string",
    "author": "string",
    "category": "string",
    "html_code": "string",
    "status": "draft" or "publish"
  }
  ```
- **Output**:
  - **Success (201)**:
    ```json
    {"message": "successful"}
    ```
  - **Error (400)**:
    ```json
    {"title": ["This field is required."]}
    ```
- **Logic**:
  1. Validate input with `BlogSerializer`.
  2. Save to `Blog` model.

### 5.14 List Blogs
- **Endpoint**: `GET /api/admin/blogs/`
- **Permission**: `IsAuthenticated`
- **Description**: Retrieves all blogs, ordered by creation date (descending).
- **Input**: None.
- **Output**:
  - **Success (200)**:
    ```json
    [
      {
        "id": integer,
        "title": "string",
        "author": "string",
        "category": "string",
        "html_code": "string",
        "created_at": "datetime",
        "status": "draft" or "publish"
      }
    ]
    ```
- **Logic**:
  1. Fetch all blogs, ordered by `created_at` (descending).
  2. Serialize with `BlogSerializer`.

### 5.15 Single Blog
- **Endpoint**: `GET /api/admin/blogs/<id>/`
- **Permission**: `IsAuthenticated`
- **Description**: Retrieves a specific blog by ID.
- **Input**: None (uses `id` from URL).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "id": integer,
      "title": "string",
      "author": "string",
      "category": "string",
      "html_code": "string",
      "created_at": "datetime",
      "status": "draft" or "publish"
    }
    ```
  - **Error (404)**:
    ```json
    {"detail": "Blog not found."}
    ```
- **Logic**:
  1. Fetch blog by `id`.
  2. Serialize with `BlogSerializer`.

### 5.16 Edit Blog
- **Endpoint**: `PATCH /api/admin/edit-blog/<id>/`
- **Permission**: `IsAuthenticated`
- **Description**: Updates a blog (only if in `draft` status).
- **Input**:
  ```json
  {
    "title": "string",
    "author": "string",
    "category": "string",
    "html_code": "string",
    "status": "draft" or "publish"
  }
  ```
- **Output**:
  - **Success (200)**:
    ```json
    {"detail": "Blog updated successfully."}
    ```
  - **Error (400)**:
    ```json
    {"title": ["This field is required."]}
    ```
  - **Error (403)**:
    ```json
    {"error": "Editing is only allowed for draft blogs."}
    ```
  - **Error (404)**:
    ```json
    {"detail": "Blog not found."}
    ```
- **Logic**:
  1. Fetch blog by `id`.
  2. Check if status is `draft`.
  3. Update fields using `BlogSerializer` (partial update).

### 5.17 Toggle Blog Status
- **Endpoint**: `POST /api/admin/toggle-blog/<id>/`
- **Permission**: `IsAuthenticated`
- **Description**: Toggles blog status between `draft` and `publish`.
- **Input**: None (uses `id` from URL).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "id": integer,
      "message": "successful"
    }
    ```
  - **Error (404)**:
    ```json
    {"detail": "Blog not found."}
    ```
- **Logic**:
  1. Fetch blog by `id`.
  2. Toggle `status` (`draft` ↔ `publish`) and save.

### 5.18 Delete Blog
- **Endpoint**: `DELETE /api/admin/delete-blog/<id>/`
- **Permission**: `IsAuthenticated`
- **Description**: Deletes a blog by ID.
- **Input**: None (uses `id` from URL).
- **Output**:
  - **Success (200)**:
    ```json
    {"message": "successful"}
    ```
  - **Error (404)**:
    ```json
    {"detail": "Blog not found."}
    ```
- **Logic**:
  1. Fetch blog by `id`.
  2. Delete the blog.

### 5.19 Push Notification
- **Endpoint**: `POST /api/admin/push-notification/`
- **Permission**: `IsAuthenticated` (superuser only)
- **Description**: Sends a push notification and saves it to the database.
- **Input**:
  ```json
  {
    "title": "string",
    "message": "string"
  }
  ```
- **Output**:
  - **Success (201)**:
    ```json
    {
      "message": "Notification sent successfully",
      "notification": {
        "id": integer,
        "title": "string",
        "message": "string",
        "created_at": "datetime"
      },
      "fcm_response": {...}
    }
    ```
  - **Error (400)**:
    ```json
    {"title": ["Title is required and cannot be empty."]}
    ```
  - **Error (403)**:
    ```json
    {"error": "Only admin users can send notifications."}
    ```
- **Logic**:
  1. Verify superuser status.
  2. Validate input with `NotificationSerializer`.
  3. Save notification to `Notification` model.
  4. Send notification using `send_notification_to_topic` (assumes FCM integration).
  5. Return notification data and FCM response.

### 5.20 Notification History
- **Endpoint**: `GET /api/admin/notification-history/`
- **Permission**: `IsAuthenticated`
- **Description**: Retrieves all notifications, ordered by creation date (descending).
- **Input**: None.
- **Output**:
  - **Success (200)**:
    ```json
    [
      {
        "id": integer,
        "title": "string",
        "message": "string",
        "created_at": "datetime"
      }
    ]
    ```
- **Logic**:
  1. Fetch all notifications, ordered by `created_at` (descending).
  2. Serialize with `NotificationSerializer`.

### 5.21 List Users
- **Endpoint**: `GET /api/admin/users/`
- **Permission**: `IsAuthenticated`
- **Description**: Lists all users from the `mobile_api_appuser` collection.
- **Input**: None.
- **Output**:
  - **Success (200)**:
    ```json
    {
      "users": [
        {
          "index": integer,
          "id": integer,
          "name": "string",
          "phone number": "string",
          "year of study": "string",
          "status": "accepted" or "rejected"
        }
      ]
    }
    ```
- **Logic**:
  1. Fetch all users from `AdminAppUser`.
  2. Format response with index and selected fields.

### 5.22 Toggle User Status
- **Endpoint**: `POST /api/admin/toggle_status/<user_id>/`
- **Permission**: `AllowAny` (Note: Consider changing to `IsAuthenticated` for security)
- **Description**: Toggles user status between `accepted` and `rejected`.
- **Input**: None (uses `user_id` from URL).
- **Output**:
  - **Success (200)**:
    ```json
    {"message": "User status updated to <status>"}
    ```
  - **Error (404)**:
    ```json
    {"error": "User not found"}
    ```
- **Logic**:
  1. Fetch user by `id` (not `_id`).
  2. Toggle `status` (`accepted` ↔ `rejected`) and save.

### 5.23 View User Details
- **Endpoint**: `GET /api/admin/view_user/<user_id>/`
- **Permission**: None (Note: Consider adding `IsAuthenticated`)
- **Description**: Retrieves detailed user information.
- **Input**: None (uses `user_id` from URL).
- **Output**:
  - **Success (200)**:
    ```json
    {
      "user": {
        "name": "string",
        "phone_number": "string",
        "email": "string",
        "year_of_study": "string",
        "college": "string",
        "department": "string",
        "university": "string",
        "blood_group": "string",
        "profile_pic": "url or null",
        "subscription_plan": "string",
        "status": "accepted" or "rejected"
      }
    }
    ```
  - **Error (404)**:
    ```json
    {"error": "User not found"}
    ```
- **Logic**:
  1. Fetch user by `id` (not `_id`).
  2. Return formatted user details.

## 6. Security and Authentication
- **JWT Authentication**: Uses `rest_framework_simplejwt` with:
  - Access token lifetime: 60 minutes.
  - Refresh token lifetime: 7 days.
  - Tokens are generated via `/api/admin/login/`.
- **CORS**: Configured with `CORS_ALLOW_ALL_ORIGINS = True` for development. For production, specify allowed origins.
- **Permissions**:
  - Most endpoints require `IsAuthenticated`.
  - `ProcessCourseAPIView`, `ToggleCourseStatusView`, and `PushNotificationView` require superuser status.
  - `/login/` and `/contact/` use `AllowAny`.
  - `ToggleUserStatus` and `view_user_details` lack explicit permissions (consider adding `IsAuthenticated`).

## 7. File Storage
- **Media Files**: Course materials (PDF/TXT) are stored in `media/` directory.
  - `MEDIA_URL = '/media/'`
  - `MEDIA_ROOT = os.path.join(BASE_DIR, 'media')`
- **Validation**: Files are validated for:
  - Extensions: `.pdf`, `.txt`.
  - Size: <100MB.

## 8. Logging
- Logging is implemented using `logging.getLogger(__name__)` to track:
  - Successful operations (e.g., course creation, blog updates).
  - Errors (e.g., validation failures, missing courses).
- Logs are essential for debugging and monitoring API usage.

## 9. External Dependencies
- **AI Server**: The `ProcessCourseAPIView` sends data to an external AI server (`AI_SERVER` URL from `.env`). Ensure the server is running and accessible.
- **FCM (Firebase Cloud Messaging)**: Used for push notifications via `send_notification_to_topic` (assumed to be defined in `utils.py`).

## 10. Notes for Developers
- **MongoDB Integration**: Djongo maps Django models to MongoDB collections. Ensure `course_code` is consistent across related models (`CourseBasicInfo`, `CourseOutcome`, etc.).
- **Draft vs. Published**: Only `draft` courses and blogs can be edited to prevent unintended changes to published content.
- **Shared Database**: The `AdminAppUser` model maps to the `mobile_api_appuser` collection, shared with the app side. Use `id` (not `_id`) for queries.
- **Security Improvements**:
  - Change `CORS_ALLOW_ALL_ORIGINS = True` to specific origins in production.
  - Add `IsAuthenticated` to `ToggleUserStatus` and `view_user_details`.
  - Set `DEBUG = False` in production and secure `SECRET_KEY`.
- **Testing**: Use tools like Postman or curl to test APIs. Include `Authorization: Bearer <access_token>` for authenticated endpoints.

## 11. Example API Usage
### Login
```bash
curl -X POST http://localhost:8000/api/admin/login/ -d '{"username": "admin", "password": "password"}'
```

### Create Course
```bash
curl -X POST http://localhost:8000/api/admin/course-basic-info/ \
-H "Authorization: Bearer <access_token>" \
-H "Content-Type: application/json" \
-d '{
  "course_name": "Introduction to Python",
  "course_code": "CS101",
  "year": 2023,
  "branch": "Computer Science",
  "semester": 1,
  "group": "A"
}'
```

### Upload Materials
```bash
curl -X POST http://localhost:8000/api/admin/course-materials/ \
-H "Authorization: Bearer <access_token>" \
-F "course_code=CS101" \
-F "status=published" \
-F "files=@/path/to/file.pdf" \
-F "file_type_0=PDF"
```

### Send Notification
```bash
curl -X POST http://localhost:8000/api/admin/push-notification/ \
-H "Authorization: Bearer <access_token>" \
-H "Content-Type: application/json" \
-d '{
  "title": "New Course Available",
  "message": "Check out CS101 on the Klaw app!"
}'
```