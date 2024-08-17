import tkinter as tk
from pymongo import MongoClient
from tkinter import messagebox
from tkinter import LEFT, Entry, Label, StringVar, ttk, Tk, Text, Scrollbar, VERTICAL, RIGHT, Y, END
import speech_recognition as sr
import re

def check_password(password):
    
    # Define password requirements
    if len(password) < 8:
        messagebox.showwarning("Password Check", "Password must be at least 8 characters long.")
        return False

    if not re.search(r'[A-Z]', password):
        messagebox.showwarning("Password Check", "Password must contain at least one uppercase letter.")
        return False

    if not re.search(r'[a-z]', password):
        messagebox.showwarning("Password Check", "Password must contain at least one lowercase letter.")
        return False

    if not re.search(r'\d', password):
        messagebox.showwarning("Password Check", "Password must contain at least one digit.")
        return False

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        messagebox.showwarning("Password Check", "Password must contain at least one special character.")
        return False

    return True

# Connect to MongoDB for Login
client1 = MongoClient('mongodb+srv://Admin:Astitva2711@analysis.zljgu3m.mongodb.net/')
db1 = client1['Sentiment']
users_collection = db1['Login']

def is_valid_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(regex, email):
        return True
    else:
        return False

# Function to handle login
def login():
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showerror("Input Error", "Both fields are required")
        return

    if not is_valid_email(username):
        messagebox.showerror("Input Error", "Invalid UserID Format, Please enter valid E-mail Address")
        return

    user = users_collection.find_one({"username": username, "password": password})
    if user:
        messagebox.showinfo("Login Successful", f"Welcome, {username}!")
        open_main_window(username)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

# Function to handle SignUp
def register():
    username = username_entry.get()
    password = password_entry.get()
    
    if not username or not password:
        messagebox.showerror("Input Error", "Both fields are required")
        return
    
    if not is_valid_email(username):
        messagebox.showerror("Input Error", "Invalid UserID Format, Please enter valid E-mail Address")
        return
    
    if not check_password(password):
        return
    
    if users_collection.find_one({"username": username}):
        messagebox.showerror("Registration Failed", "Username already exists")
    else:
        users_collection.insert_one({"username": username, "password": password})
        messagebox.showinfo("Registration Successful", f"User {username} registered successfully!")

# Function to open the main window after successful login
def open_main_window(username):
    # Close the login window
    root.destroy()
    
    def analyze_sentiment(text):
        # Connect to the MongoDB server
        client2 = MongoClient('localhost', 27017)

        # Access a database named 'testdb'
        db2 = client2.Sentiment

        # Access a collection named 'testcollection'
        collection = db2.Words

        # Retrieve documents and access the array field
        for document in collection.find():
            negative_words = f"{document['negative_words']}"
            positive_words = f"{document['positive_words']}"

        # Close the connection
        client2.close()

        # Split text into words and then convert it into lowercase
        words = text.lower().split()

        # Count the number of positive and negative words in the text
        num_positive = sum(1 for word in words if word in positive_words)
        num_negative = sum(1 for word in words if word in negative_words)
        
        # Determine the overall sentiment based on the counts
        if num_positive > num_negative:
            return "Positive"
        elif num_negative > num_positive:
            return "Negative"
        else:
            return "Neutral"

    def transcribe_audio():
        status_label.config(text="Status: Project Started")
        main_window.update_idletasks()  # Forcefully Updating GUI
        
        # Initialize the recognizer for fetching voice to generate text
        recognizer = sr.Recognizer()
        # Using default microphone as the audio source
        with sr.Microphone() as source:
            status_label.config(text="Status: Please Speak...")
            main_window.update_idletasks()  # Forcefully Updating GUI
            print("Please speak...")
            # Using inbuilt function to adjust ambient noise in the voice
            recognizer.adjust_for_ambient_noise(source)
            # Fetching the voice input
            audio = recognizer.listen(source)

            try:
                status_label.config(text="Status: Transcribing...")
                main_window.update_idletasks() # Forcefully Updating GUI
                print("Transcribing...")
                # converting speech to text
                text = recognizer.recognize_google(audio)
                print("You said:", text)

                text_widget.config(state=tk.NORMAL)
                text_widget.delete(1.0, END)
                text_widget.insert(END, text)
                text_widget.config(state=tk.DISABLED)
                
                # Analyze sentiment using basic logic
                sentiment = analyze_sentiment(text)
                print("Sentiment:", sentiment)
                sentiment_var.set(sentiment)
            except sr.UnknownValueError:
                print("Sorry, I couldn't understand what you said.")
                status_label.config(text="Status: Couldn't understand. Try again.")
            except sr.RequestError as e:
                print("Error fetching results; {0}".format(e))
                status_label.config(text="Status: API Error.")
            status_label.config(text="Project Completed")

    # Create the main application window
    main_window = Tk()
    # GUI Block Dimension
    main_window.geometry("700x310")
    main_window.title("Sentiment Analysis")
    main_window.configure(bg="lightblue")

    title_label = Label(main_window, text='Sentiment Analysis of Incoming Calls on Helpdesk', font=("Helvetica", 16, "bold"), bg="lightblue")
    title_label.pack(pady=10)
    
    sentiment_var = StringVar()

    # Create a label to display the status
    status_label = ttk.Label(main_window, text="Status: Waiting to start")
    status_label.pack(pady=10)

    # Create a Text widget with a scroll view
    transcribed_text_label = Label(main_window, text="Transcribed Text", bg="lightblue")
    transcribed_text_label.pack()

    # Create a Frame to hold the Text widget and Scrollbar with side padding
    text_frame = tk.Frame(main_window, bg="lightblue", padx=20)  # Add side padding here
    text_frame.pack(pady=5, fill=tk.BOTH, expand=False)

    scrollbar = Scrollbar(text_frame, orient=VERTICAL)
    text_widget = Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, width=60, height=5, state=tk.DISABLED) 
    scrollbar.config(command=text_widget.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    text_widget.pack(side=LEFT, fill=tk.BOTH, expand=True)

    # Sentiment Block
    sentiment_label = Label(main_window, text="Sentiment Analyzed", bg="lightblue")
    sentiment_label.pack()
    sentiment_entry = Entry(main_window, textvariable=sentiment_var, state="readonly")
    sentiment_entry.pack(pady=5)

    # Button to start progress
    start_button = tk.Button(main_window, text="Start Progress", command=transcribe_audio)
    start_button.pack(pady=10)

    main_window.mainloop()

if __name__ == "__main__":
    # Create the Login Window
    root = tk.Tk()
    root.geometry("700x310")
    root.title("Sentiment Analysis Login Page")
    root.configure(bg="lightblue")


    # Create a main frame to centralize content
    main_frame = tk.Frame(root)
    main_frame.pack(expand=True)

    # Create a frame for the form
    form_frame = tk.Frame(main_frame, padx=10, pady=10)
    form_frame.pack()

    # Create and place the username label and entry
    username_label = tk.Label(form_frame, text="Username")
    username_label.grid(row=0, column=0, pady=5, sticky="e")
    username_entry = tk.Entry(form_frame, width=30)
    username_entry.grid(row=0, column=1, pady=5)

    # Create and place the password label and entry
    password_label = tk.Label(form_frame, text="Password")
    password_label.grid(row=1, column=0, pady=5, sticky="e")
    password_entry = tk.Entry(form_frame, show="*", width=30)
    password_entry.grid(row=1, column=1, pady=5)

    # Create a frame for the buttons
    button_frame = tk.Frame(main_frame, pady=10)
    button_frame.pack()

    # Create and place the login and register buttons
    login_button = tk.Button(button_frame, text="Login", width=15, command=login)
    login_button.grid(row=0, column=0, padx=5)
    register_button = tk.Button(button_frame, text="Register", width=15, command=register)
    register_button.grid(row=0, column=1, padx=5)

    # Run the main loop
    root.mainloop()
    