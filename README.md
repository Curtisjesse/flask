# Flask Customer Orders Application

This is a simple Flask application to manage customer orders. The application includes a web interface to view customers and their orders, with options to update and delete orders.

## Features

- List all customers and their orders

## Technologies Used

- Flask
- SQLAlchemy
- SQLite
- HTML/CSS (Bootstrap)

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/Curtisjesse/flask.git
    cd flask
    ```

2. **Create a virtual environment:**
    ```sh
    python -m venv myenv
    ```

3. **Activate the virtual environment:**
    - On Windows:
        ```sh
        myenv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source myenv/bin/activate
        ```

4. **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

5. **Initialize the database:**
    ```sh
    python init_db.py
    ```

6. **Run the application:**
    ```sh
    python app.py
    ```

    The application will be accessible at `http://127.0.0.1:8000`.

## Project Structure

