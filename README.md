🔹 Step1  download project.
🔹 Step 2 : Set Up a Virtual Environment (Recommended)
To keep dependencies organized, create and activate a virtual environment:

Windows:
python -m venv venv
venv\Scripts\activate

Mac/Linux:
python3 -m venv venv
source venv/bin/activate

🔹 Step 3: Install Required Dependencies
Make sure you have all necessary packages installed:

pip install -r requirements.txt
This installs: ✅ Flask
✅ Flask-SocketIO
✅ python-socketio
✅ python-engineio
✅ dateparser
✅ threading

🔹 Step 4: Run the Flask Application
Start the Flask server with:
python app.py
If everything is set up correctly, you should see:
csharp

 * Running on http://127.0.0.1:5000
Now, open your browser and go to http://127.0.0.1:5000.
