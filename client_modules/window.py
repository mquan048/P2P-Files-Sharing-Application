import customtkinter  as ctk
from PIL import Image
from socket import *


class App():
    def __init__(self,root,width,height,share_dir,local_dir):
        self.mainframe = ctk.CTkFrame(root)
        self.width = width
        self.height = height
        self.share_dir = share_dir
        self.local_dir = local_dir
        self.login_screen = LoginFrame(self, self.mainframe, self.width, self.height)
        self.dashboard_screen = DashboardFrame(self, self.mainframe, self.width, self.height, self.share_dir, self.local_dir)
        self.login_screen.show()
        self.mainframe.pack(fill="both", expand=True)

    def changeDashboardFrame(self):
        self.login_screen.hide()
        self.dashboard_screen.show()

    def changeLoginFrame(self):
        self.dashboard_screen.hide()
        self.login_screen.show()

    def login(self,username,password):
        print(f"Username: {username}, Password: {password}")
        # If user authenticated -> change to login frame
        self.changeDashboardFrame()

    def logout(self):
        # Logout logic
        self.changeLoginFrame()

class LoginFrame(ctk.CTkFrame):
    def __init__(self, app, master, width, height):
        super().__init__(master)
        self.app = app
        self.master = master
        self.width = width
        self.height = height
        self.background = ctk.CTkImage(light_image=Image.open("public/login_background.png"),dark_image=Image.open("public/login_background.png"),size=(width,height))
        self.main_frame = ctk.CTkFrame(master)

    def show(self):
        # Background image
        background_label = ctk.CTkLabel(self.main_frame,image=self.background,text="")
        background_label.pack()
        # Center frame
        center_frame = ctk.CTkFrame(self.main_frame,fg_color="white",width=400,height=350)
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
        login_button = ctk.CTkButton(center_frame, text="Login",font=("Arial", 16), fg_color="#00A2FF",text_color="white",corner_radius=5,width=350,command=lambda: self.app.login(self.username_entry.get(),self.password_entry.get()))
        login_button.pack()
        # Pack
        center_frame.place(relx=0.5, rely=0.5, anchor="c")
        self.main_frame.pack(fill="both", expand=True)

    def hide(self):
        self.main_frame.pack_forget()

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, app, master, width, height,share_dir,local_dir):
        super().__init__(master)
        self.app = app
        self.master = master
        self.width = width
        self.height = height
        self.share_dir = share_dir
        self.local_dir = local_dir
        self.main_frame = ctk.CTkFrame(master)

    def show(self):
        # Left menu
        left_frame=ctk.CTkFrame(self.main_frame,width=150,height=self.height,fg_color="white",corner_radius=0)
        left_frame.pack_propagate(0)
        # Vertical line
        vertical_line = ctk.CTkFrame(left_frame,width=1,height=self.height-10,fg_color="#9E9E9E",border_color="#9E9E9E",border_width=1)
        vertical_line.pack(side="right")
        # Right panel
        self.right_frame=ctk.CTkFrame(self.main_frame,width=self.width-150,height=self.height,fg_color="white",corner_radius=0)
        self.right_frame.pack_propagate(0)
        # Menu items
        share_button = ctk.CTkButton(left_frame,text="Shared files",font=("Arial", 18),fg_color="white",text_color="blue",corner_radius=0,hover_color="white",width=150,command=lambda: self.showSharedFiles(self.right_frame))
        share_button.pack(pady=(20,15))
        local_button = ctk.CTkButton(left_frame,text="My files",font=("Arial", 18),fg_color="white",text_color="blue",corner_radius=0,hover_color="white",width=150,command=lambda: self.showMyFiles(self.right_frame))
        local_button.pack(pady=(15,20))
        logout_button = ctk.CTkButton(left_frame,text="Logout",font=("Arial", 20),fg_color="white",text_color="red",corner_radius=0,width=150,hover_color="white",command=self.app.logout)
        logout_button.pack(pady=(self.height-175,0))
        # Create 2 main frames
        self.showSharedFiles(self.right_frame,True)
        self.showMyFiles(self.right_frame,True)
        self.my_file_frame.pack_forget()
        # Pack
        left_frame.pack(side="left",fill="both", expand=True)
        self.right_frame.pack(side="right",fill="both", expand=True)
        self.main_frame.pack(fill="both", expand=True)

    def hide(self):
        self.main_frame.pack_forget()

    def showSharedFiles(self,master,first_time=False):
        self.shared_file_frame=ctk.CTkFrame(master,width=self.width-150,height=self.height,fg_color="white")
        # Label
        label=ctk.CTkLabel(self.shared_file_frame,text="Shared files",font=("Arial", 30))
        label.pack(pady=(20,50))
        # Header frame
        header_frame=ctk.CTkFrame(self.shared_file_frame,width=self.width-150,height=50,fg_color="white")
        header_frame.pack_propagate(0)
        file_name_label=ctk.CTkLabel(header_frame,text="File name",font=("Arial", 16),width=300)
        file_name_label.pack(side="left")
        file_size_label=ctk.CTkLabel(header_frame,text="File size",font=("Arial", 16),width=100)
        file_size_label.pack(padx=(250,300),side="left")
        action_label=ctk.CTkLabel(header_frame,text="Action",font=("Arial", 16),width=100)
        action_label.pack(padx=(0,100),side="left")
        header_frame.pack()
        # Horizontal line
        horizontal_line=ctk.CTkFrame(self.shared_file_frame,width=self.width-200,height=1,fg_color="#9E9E9E",border_color="#9E9E9E",border_width=1)
        horizontal_line.pack()
        # File list

        # Pack
        self.shared_file_frame.pack(fill="both", expand=True)

        # Remove my files frame
        if hasattr(self, 'my_file_frame') and not first_time:
            self.my_file_frame.pack_forget()

    def showMyFiles(self,master,first_time=False):
        self.my_file_frame=ctk.CTkFrame(master,width=self.width-150,height=self.height,fg_color="white")
        # Label
        label=ctk.CTkLabel(self.my_file_frame,text="My files",font=("Arial", 30))
        label.pack(pady=(20,50))
        # Header frame
        header_frame=ctk.CTkFrame(self.my_file_frame,width=self.width-150,height=50,fg_color="white")
        header_frame.pack_propagate(0)
        file_name_label=ctk.CTkLabel(header_frame,text="File name",font=("Arial", 16),width=300)
        file_name_label.pack(side="left")
        file_size_label=ctk.CTkLabel(header_frame,text="File size",font=("Arial", 16),width=100)
        file_size_label.pack(padx=(250,300),side="left")
        action_label=ctk.CTkLabel(header_frame,text="Action",font=("Arial", 16),width=100)
        action_label.pack(padx=(0,100),side="left")
        header_frame.pack()
        # Horizontal line
        horizontal_line=ctk.CTkFrame(self.my_file_frame,width=self.width-200,height=1,fg_color="#9E9E9E",border_color="#9E9E9E",border_width=1)
        horizontal_line.pack()
        # File list

        # Pack
        self.my_file_frame.pack(fill="both", expand=True)

        # Remove shared files frame
        if hasattr(self, 'shared_file_frame') and not first_time:
            self.shared_file_frame.pack_forget()

def initWindow(APP_NAME, WIDTH, HEIGHT,SHARE_DIR,LOCAL_DIR):
    root=ctk.CTk()
    root.title(APP_NAME)
    root.geometry(f"{WIDTH}x{HEIGHT}")
    App(root, WIDTH, HEIGHT,SHARE_DIR,LOCAL_DIR)
    root.mainloop()
