import customtkinter  as ctk
from PIL import Image
from socket import *


class App():
    def __init__(self,root,width,height):
        self.mainframe = ctk.CTkFrame(root)
        self.width = width
        self.height = height
        # LoginFrame(self.mainframe, self.width, self.height)

        self.mainframe.pack(fill="both", expand=True)

    def changeDashboardFrame(self):
        pass

    def changeLoginFrame(self):
        pass

    def login(self,username,password):
        print(f"Username: {username}, Password: {password}")
        # If user authenticated -> change to login frame
        self.changeDashboardFrame()

    def logout(self):
        pass

class LoginFrame(ctk.CTkFrame,App):
    def __init__(self, master, width, height):
        super().__init__(master)
        self.master = master
        self.width = width
        self.height = height
        self.background = ctk.CTkImage(light_image=Image.open("public/login_background.png"),dark_image=Image.open("public/login_background.png"),size=(width,height))
        self.show()

    def show(self):
        main_frame = ctk.CTkFrame(self.master)
        # Background image
        background_label = ctk.CTkLabel(main_frame,image=self.background,text="")
        background_label.pack()
        # Center frame
        center_frame = ctk.CTkFrame(main_frame,fg_color="white",width=400,height=350)
        center_frame.pack_propagate(0)
        # Login label
        login_label = ctk.CTkLabel(center_frame, text="Login", font=("Arial", 36))
        login_label.pack(pady=10)
        # Border frame
        border_frame = ctk.CTkFrame(center_frame,width=350,height=1,fg_color="black",border_color="black",border_width=1)
        border_frame.pack_propagate(0)
        border_frame.pack()
        # Input frame
        input_frame = ctk.CTkFrame(center_frame,width=400,height=150,fg_color="white")
        input_frame.pack_propagate(0)
        # Username input
        username_label = ctk.CTkLabel(input_frame, text="Username",font=("Arial",13,"bold"),width=350)
        username_label.pack(padx=(0,285))
        self.username_entry = ctk.CTkEntry(input_frame,font=("Arial", 13),corner_radius=5,height=30,width=350,border_width=1,border_color="#CDCDCD",placeholder_text="Enter your username")
        self.username_entry.pack(pady=10)
        # Password input
        password_label = ctk.CTkLabel(input_frame, text="Password",font=("Arial",13,"bold"),width=350)
        password_label.pack(padx=(0,285))
        self.password_entry = ctk.CTkEntry(input_frame,font=("Arial", 13),corner_radius=5,height=30,width=350,border_width=1,border_color="#CDCDCD",placeholder_text="Enter your password")
        self.password_entry.pack()
        input_frame.pack(pady=30)
        # Login button
        login_button = ctk.CTkButton(center_frame, text="Login",font=("Arial", 16), fg_color="#00A2FF",text_color="white",corner_radius=5,width=350,command=self.login)
        login_button.pack()
        center_frame.place(relx=0.5, rely=0.5, anchor="c")
        main_frame.pack(fill="both", expand=True)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        super().login(username,password)



def initWindow(APP_NAME, WIDTH, HEIGHT):
    root=ctk.CTk()
    root.title(APP_NAME)
    root.geometry(f"{WIDTH}x{HEIGHT}")
    App(root, WIDTH, HEIGHT)
    root.mainloop()
