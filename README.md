# STEM Hub | University Lab Management System

**STEM Hub** is a centralized web dashboard designed to streamline the scheduling, resource management, and communication flow for university STEM facilities. It replaces disjointed spreadsheets with a real-time, interactive reservation system.

## Project Overview

Managing high-demand laboratories (Physics, Robotics, Chemistry) and specialized equipment requires precision. STEM Hub allows students to check real-time availability and book slots, while giving administrators full control over facility usage, asset tracking, and safety compliance.

### Key Features

#### For Students (End Users)
* **Interactive Dashboard:** View available facilities, upcoming slots, and recent announcements at a glance.
* **Smart Booking System:** Browse labs, check capacity, and request reservations with automatic conflict detection.
* **Notification Center:** Real-time alerts (🔔) for reservation approvals/rejections and general updates.
* **Resource Access:** View detailed equipment inventories, operational status, and safety guidelines before entering the lab.

#### For Staff & Administrators
* **Facility Management:** Create and edit labs using complex forms (Django Formsets) to dynamically add/remove equipment.
* **Reservation Control:** Approve or reject student requests via an admin panel.
* **Broadcast System:** Send color-coded public announcements (Info/Warning/Success) to specific user groups (Students/Staff/All).
* **Asset Tracking:** Mark specific equipment (e.g., Oscilloscopes, VR Headsets) as "Broken" or "Maintenance" to prevent usage.

---

## Tech Stack

* **Backend:** Python, Django 5.x
* **Frontend:** HTML5, Tailwind CSS (Glassmorphism Design), JavaScript
* **Database:** SQLite (Dev) / PostgreSQL (Compatible)
* **Key Django Features Used:**
    * **Signals:** Automated notification generation on model changes.
    * **Formsets:** Dynamic inline forms for managing equipment lists.
    * **Context Processors:** Global notification counters available on every page.
    * **Decorators:** Role-based access control (`@staff_member_required`).

---

## Installation & Setup

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/yourusername/stem-hub.git](https://github.com/yourusername/stem-hub.git)
    cd stem-hub
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install django
    ```

4.  **Run Migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  **Run the Server**
    ```bash
    python manage.py runserver
    ```

---

## Application Workflow

1.  **Login:** Users authenticate to access the dashboard.
2.  **Browse:** Students select a lab (e.g., *Robotics Lab C*) to view equipment status.
3.  **Reserve:** Student submits a time slot.
4.  **Process:** Admin receives a "Pending Request" notification.
5.  **Notify:** Upon Approval/Rejection, the system automatically triggers a notification to the student's bell icon.

---

## 🔐 Example Login Credentials

To test the application, you can use the following pre-configured accounts:

| Role | Username | Password | Capabilities |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full access to Admin Panel, Lab Editing, Broadcasts & Approvals |
| **Student** | `student` | `ilikeicecream123` | Can Browse Labs, View Map, Book Slots & Receive Notifications |