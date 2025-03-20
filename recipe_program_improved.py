import tkinter as tk  # import tkinter for creating the graphical user interface
from tkinter import messagebox, ttk  # import messagebox for displaying error or info messages, ttk for themed widgets
import requests  # import requests to make HTTP requests to fetch recipes
import openai  # import openai to interact with the OpenAI API for chatbot functionality
from PIL import Image, ImageTk  # import PIL for image processing and displaying images
from io import BytesIO  # import BytesIO to handle image data in memory
import webbrowser  # import webbrowser to open recipe links in a browser

# set your OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"  # use the OpenAI API key for chatbot functionality

class RecipeApp:
    def __init__(self, root):
        self.root = root  # initialize the main window
        self.root.title("Enhanced Recipe App")  # set the title of the main window
        self.root.geometry("1000x800")  # set the size of the main window
        self.root.configure(bg="lightblue")  # set the background color of the main window

        # API key for Spoonacular API to fetch recipes
        self.api_key = "YOUR_SPOONACULAR_API_KEY"  # store the API key for Spoonacular

        # Data storage for user's favorite recipes and meal plan
        self.favorites = []  # list to store favorite recipes
        self.meal_plan = []  # list to store meal plan

        # Header section
        title = tk.Label(
            self.root, text="Enhanced Recipe App", font=("Arial", 24, "bold"), bg="lightblue", fg="green"
        )  # create a label for the header with a title
        title.pack(pady=10)  # add the header label to the window with padding

        # Chatbot section
        chatbot_frame = tk.Frame(self.root, bg="lightblue")  # create a frame for the chatbot
        chatbot_frame.pack(pady=5)  # pack the chatbot frame with padding
        tk.Label(chatbot_frame, text="Ask our Cooking Assistant:", bg="lightblue").grid(row=0, column=0, padx=5)  # label for user input prompt
        self.chatbot_entry = tk.Entry(chatbot_frame, width=50)  # create a text entry for user input
        self.chatbot_entry.grid(row=0, column=1, padx=5)  # grid the entry widget
        chatbot_button = tk.Button(chatbot_frame, text="Ask", command=self.chatbot_response, bg="green", fg="white")  # button to trigger chatbot response
        chatbot_button.grid(row=0, column=2, padx=5)  # grid the chatbot button
        self.chatbot_output = tk.Text(self.root, height=4, wrap=tk.WORD, state="disabled", bg="lightyellow")  # text box for displaying chatbot responses
        self.chatbot_output.pack(pady=10, padx=10, fill=tk.X)  # pack the chatbot output text box

        # Search section
        search_frame = tk.Frame(self.root, bg="lightblue")  # create a frame for the search section
        search_frame.pack(pady=10)  # pack the search frame with padding

        tk.Label(search_frame, text="Search Recipes by Name or Ingredients:", bg="lightblue").grid(row=0, column=0, padx=5)  # label for search input prompt
        self.search_entry = tk.Entry(search_frame, width=50)  # text entry for recipe search query
        self.search_entry.grid(row=0, column=1, padx=5)  # grid the search entry
        tk.Button(search_frame, text="Search", command=self.search_recipes, bg="green", fg="white").grid(row=0, column=2, padx=5)  # button to trigger recipe search

        # Cuisine filter dropdown
        self.cuisine_filter = tk.StringVar()  # variable to store selected cuisine type
        tk.Label(search_frame, text="Cuisine:", bg="lightblue").grid(row=1, column=0, pady=5)  # label for cuisine filter
        cuisines = ["None", "American", "Italian", "Mexican", "Indian", "Chinese", "Thai"]  # list of cuisines
        cuisine_menu = ttk.Combobox(search_frame, textvariable=self.cuisine_filter, values=cuisines)  # create a dropdown for cuisine selection
        cuisine_menu.grid(row=1, column=1, padx=5, pady=5)  # grid the cuisine dropdown
        cuisine_menu.set("None")  # default value for the cuisine filter

        # Health filter dropdown
        self.health_filter = tk.StringVar()  # variable to store selected dietary preference
        tk.Label(search_frame, text="Dietary Preference:", bg="lightblue").grid(row=2, column=0, pady=5)  # label for health filter
        diets = ["None", "Vegetarian", "Vegan", "Gluten Free", "Ketogenic"]  # list of health preferences
        diet_menu = ttk.Combobox(search_frame, textvariable=self.health_filter, values=diets)  # create a dropdown for health preference selection
        diet_menu.grid(row=2, column=1, padx=5, pady=5)  # grid the health preference dropdown
        diet_menu.set("None")  # default value for the health filter

        # Results section where recipes will be displayed
        self.results_frame = tk.Frame(self.root, bg="lightblue")  # create a frame to display search results
        self.results_frame.pack(pady=10, fill=tk.BOTH, expand=True)  # pack the results frame with padding

        # Buttons for viewing favorites and meal plan
        buttons_frame = tk.Frame(self.root, bg="lightblue")  # create a frame for buttons
        buttons_frame.pack(pady=10)  # pack the buttons frame with padding
        tk.Button(buttons_frame, text="View Favorites", command=self.show_favorites, bg="blue", fg="white").pack(side="left", padx=5)  # button to view favorites
        tk.Button(buttons_frame, text="View Meal Plan", command=self.show_meal_plan, bg="blue", fg="white").pack(side="left", padx=5)  # button to view meal plan

    def chatbot_response(self):
        query = self.chatbot_entry.get().strip()  # get the user input from the chatbot entry
        if not query:  # if the input is empty, return
            return

        self.chatbot_output.configure(state="normal")  # enable the text box to insert text
        self.chatbot_output.insert(tk.END, f"You: {query}\n")  # insert user query into the output text box
        self.chatbot_output.configure(state="disabled")  # disable the text box after inserting the query
        self.chatbot_entry.delete(0, tk.END)  # clear the user input field

        # Fetch response from OpenAI API
        try:
            response = openai.ChatCompletion.create(  # send the query to OpenAI's API and get the response
                model="gpt-3.5-turbo",  # use the GPT-3.5 model
                messages=[  # conversation context for OpenAI API
                    {"role": "system", "content": "You are a helpful cooking assistant."},
                    {"role": "user", "content": query},
                ]
            )
            bot_reply = response["choices"][0]["message"]["content"]  # get the chatbot's reply
        except Exception as e:  # in case of error, show an error message
            bot_reply = f"Error: {str(e)}"

        self.chatbot_output.configure(state="normal")  # enable the text box to insert text
        self.chatbot_output.insert(tk.END, f"Chatbot: {bot_reply}\n")  # insert the bot's reply
        self.chatbot_output.configure(state="disabled")  # disable the text box after inserting the reply

    def search_recipes(self):
        query = self.search_entry.get().strip()  # get the search query
        if not query:  # if the query is empty, show an error message
            messagebox.showerror("Error", "Please enter a recipe name or ingredients.")
            return

        self.results_frame.destroy()  # remove the previous search results
        self.results_frame = tk.Frame(self.root, bg="lightblue")  # create a new frame for displaying search results
        self.results_frame.pack(pady=10, fill=tk.BOTH, expand=True)  # pack the new results frame

        diet = self.health_filter.get().lower()  # get the selected diet preference
        diet_param = f"&diet={diet}" if diet != "none" else ""  # add the diet filter to the API request
        cuisine = self.cuisine_filter.get().lower()  # get the selected cuisine type
        cuisine_param = f"&cuisine={cuisine}" if cuisine != "none" else ""  # add the cuisine filter to the API request

        url = f"https://api.spoonacular.com/recipes/complexSearch?query={query}{diet_param}{cuisine_param}&number=10&apiKey={self.api_key}"  # construct the API URL

        try:
            response = requests.get(url)  # make a GET request to the Spoonacular API
            response.raise_for_status()  # check for errors in the response
            recipes = response.json().get("results", [])  # parse the JSON response and get the recipes

            if not recipes:  # if no recipes are found, show an info message
                messagebox.showinfo("No Results", "No recipes found.")
                return

            for recipe in recipes:  # loop through the recipes and create a card for each
                self.create_recipe_card(recipe)

        except requests.exceptions.RequestException as e:  # if there's an error with the API request
            messagebox.showerror("Error", f"Failed to fetch recipes: {e}")

    def create_recipe_card(self, recipe):
        card = tk.Frame(self.results_frame, bg="lightgreen", borderwidth=2, relief="groove")  # create a frame for each recipe card
        card.pack(pady=5, padx=10, fill=tk.X)  # pack the card frame

        title = tk.Label(card, text=recipe["title"], font=("Arial", 14, "bold"), bg="lightgreen", fg="blue", cursor="hand2")  # create a label for the recipe title
        title.pack(anchor="w", pady=5)  # pack the title label
        title.bind("<Button-1>", lambda e, url=f"https://spoonacular.com/recipes/{recipe['title'].replace(' ', '-').lower()}-{recipe['id']}": self.open_link(url))  # open the recipe link on click

        img_url = recipe.get("image", "")  # get the image URL from the recipe
        if img_url:  # if the image URL exists
            img_data = requests.get(img_url).content  # fetch the image data
            img = Image.open(BytesIO(img_data))  # open the image from the data
            img = img.resize((150, 150), Image.ANTIALIAS)  # resize the image to fit the card
            img_tk = ImageTk.PhotoImage(img)  # convert the image to a format suitable for tkinter
            img_label = tk.Label(card, image=img_tk, bg="lightgreen")  # create a label to display the image
            img_label.image = img_tk  # keep a reference to the image to prevent garbage collection
            img_label.pack(anchor="w", padx=5)  # pack the image label

        fav_button = tk.Button(card, text="Add to Favorites", command=lambda: self.add_to_favorites(recipe), bg="yellow", fg="black")  # button to add the recipe to favorites
        fav_button.pack(anchor="e", padx=5, pady=5)  # pack the favorite button

    def add_to_favorites(self, recipe):
        self.favorites.append(recipe)  # add the recipe to the favorites list
        messagebox.showinfo("Favorites", f"{recipe['title']} has been added to favorites!")  # show a confirmation message

    def show_favorites(self):
        self.display_recipes("Favorites", self.favorites)  # display the favorites in a new window

    def show_meal_plan(self):
        self.display_recipes("Meal Plan", self.meal_plan)  # display the meal plan in a new window

    def display_recipes(self, title, recipes):
        if not recipes:  # if no recipes are available, show a message
            messagebox.showinfo(title, f"No {title.lower()} added yet!")
            return

        window = tk.Toplevel(self.root)  # create a new window to display the recipes
        window.title(title)  # set the window title
        window.geometry("600x400")  # set the window size
        window.configure(bg="lightblue")  # set the window background color

        for recipe in recipes:  # loop through the recipes and create a card for each
            self.create_recipe_card(recipe)

    @staticmethod
    def open_link(url):
        webbrowser.open(url)  # open the provided URL in the default web browser

if __name__ == "__main__":
    root = tk.Tk()  # create the main window
    app = RecipeApp(root)  # initialize the RecipeApp class with the main window
    root.mainloop()  # start the Tkinter event loop
