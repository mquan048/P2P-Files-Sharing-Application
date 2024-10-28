import customtkinter  as ctk
import tkinter as tk
from PIL import Image
from socket import *
import os


class App():
    def __init__(self,root,width,height,share_dir,local_dir):
        self.mainframe = ctk.CTkFrame(root)
        self.width = width
        self.height = height
        self.share_dir = share_dir
        self.local_dir = local_dir
        self.login_screen = LoginFrame(self, self.mainframe, self.width, self.height)
        self.dashboard_screen = DashboardFrame(self, self.mainframe, self.width, self.height)
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
        # TODO: If user authenticated -> change to login frame
        self.changeDashboardFrame()

    def logout(self):
        # TODO: Logout logic
        self.changeLoginFrame()

    def downloadFile(self,filename):
        # TODO: Download file logic
        self.showMessageBox('Success','File downloaded successfully!')

    def shareFile(self,filename):
        # TODO: Share file logic
        self.showMessageBox('Success','File shared successfully!')

    def uploadMyFile(self,filePath):
        # Copy filePath to self.local_dir
        file_name = os.path.basename(filePath)
        new_file_path = os.path.join(self.local_dir, file_name)
        with open(filePath, 'rb') as file:
            with open(new_file_path, 'wb') as new_file:
                new_file.write(file.read())
        self.refreshMyFrame()
        self.showMessageBox('Success','File uploaded successfully!')

    def uploadShareFile(self,filePath):
        # Copy filePath to self.share_dir
        file_name = os.path.basename(filePath)
        new_file_path = os.path.join(self.share_dir, file_name)
        with open(filePath, 'rb') as file:
            with open(new_file_path, 'wb') as new_file:
                new_file.write(file.read())
        # TODO: Notice the server that a new file has been uploaded
        self.refreshShareFrame()
        self.showMessageBox('Success','File uploaded successfully!')

    def refreshShareFrame(self):
        self.dashboard_screen.showMyFiles()
        self.dashboard_screen.showSharedFiles()

    def refreshMyFrame(self):
        self.dashboard_screen.showSharedFiles()
        self.dashboard_screen.showMyFiles()

    def getSharedFiles(self):
        files_metadata = []
        for filename in os.listdir(self.share_dir):
            if filename == '.gitkeep':
                continue
            file_path = os.path.join(self.share_dir, filename)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                metadata = {
                    'filename': filename,
                    'size': file_stat.st_size
                }
                files_metadata.append(metadata)
        return files_metadata

    def getMyFiles(self):
        files_metadata = []
        for filename in os.listdir(self.local_dir):
            if filename == '.gitkeep':
                continue
            file_path = os.path.join(self.local_dir, filename)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                metadata = {
                    'filename': filename,
                    'size': file_stat.st_size
                }
                files_metadata.append(metadata)
        return files_metadata

    def showMessageBox(self,title,message):
        messageBox=tk.messagebox.showinfo(title,message)

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
    def __init__(self, app, master, width, height):
        super().__init__(master)
        self.app = app
        self.master = master
        self.width = width
        self.height = height
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
        share_button = ctk.CTkButton(left_frame,text="Shared files",font=("Arial", 18),fg_color="white",text_color="blue",corner_radius=0,hover_color="white",width=150,command=lambda: self.showSharedFiles())
        share_button.pack(pady=(20,15))
        local_button = ctk.CTkButton(left_frame,text="My files",font=("Arial", 18),fg_color="white",text_color="blue",corner_radius=0,hover_color="white",width=150,command=lambda: self.showMyFiles())
        local_button.pack(pady=(15,20))
        logout_button = ctk.CTkButton(left_frame,text="Logout",font=("Arial", 20),fg_color="white",text_color="red",corner_radius=0,width=150,hover_color="white",command=self.app.logout)
        logout_button.pack(pady=(self.height-175,0))
        # Create 2 main frames
        self.showSharedFiles(False)
        self.showMyFiles(False)
        self.my_file_frame.pack_forget()
        self.current_frame = "shared_files"
        # Pack
        left_frame.pack(side="left",fill="both", expand=True)
        self.right_frame.pack(side="right",fill="both", expand=True)
        self.main_frame.pack(fill="both", expand=True)

    def hide(self):
        self.main_frame.pack_forget()

    def showSharedFiles(self,removeOtherFrame=True):
        if hasattr(self, 'current_frame') and self.current_frame == "shared_files":
            return
        self.current_frame = "shared_files"
        self.shared_file_frame=ctk.CTkFrame(self.right_frame,width=self.width-150,height=self.height,fg_color="white")
        # Label
        label=ctk.CTkLabel(self.shared_file_frame,text="Shared files",font=("Arial", 30))
        label.pack(pady=20)
        # File upload button
        upload_frame=ctk.CTkFrame(self.shared_file_frame,width=self.width-200,height=25,fg_color="white")
        upload_frame.pack_propagate(0)
        upload_label=ctk.CTkLabel(upload_frame,text="Upload file:",font=("Arial", 18))
        upload_label.pack(side="left",padx=(0,20))
        upload_button=ctk.CTkButton(upload_frame,text="Choose",font=("Arial", 16),fg_color="#9E9E9E",text_color="white",corner_radius=5,command=lambda: self.uploadFile(1),hover_color="#6C6C6C")
        upload_button.pack(side="left")
        upload_frame.pack()
        # Header frame
        header_frame=ctk.CTkFrame(self.shared_file_frame,width=self.width-150,height=50,fg_color="white")
        header_frame.pack_propagate(0)
        file_name_label=ctk.CTkLabel(header_frame,text="File name",font=("Arial", 16),width=int((self.width-200)*0.4))
        file_name_label.pack(side="left")
        file_size_label=ctk.CTkLabel(header_frame,text="File size",font=("Arial", 16),width=int((self.width-200)*0.4))
        file_size_label.pack(side="left")
        action_label=ctk.CTkLabel(header_frame,text="Action",font=("Arial", 16),width=int((self.width-200)*0.2))
        action_label.pack(side="left")
        header_frame.pack()
        # Horizontal line
        horizontal_line=ctk.CTkFrame(self.shared_file_frame,width=self.width-200,height=1,fg_color="#9E9E9E",border_color="#9E9E9E",border_width=1)
        horizontal_line.pack()
        # Scrollable frame
        scroll_frame=ctk.CTkScrollableFrame(self.shared_file_frame,width=self.width-150,fg_color="white",scrollbar_button_color="white")
        # File list
        files=self.app.getSharedFiles()
        # Create a row for each file
        for file in files:
            row_frame=ctk.CTkFrame(scroll_frame,width=self.width-150,height=50,fg_color="white")
            row_frame.pack_propagate(0)
            file_name_label=ctk.CTkLabel(row_frame,text=file['filename'],font=("Arial", 16),width=int((self.width-200)*0.4))
            file_name_label.pack(side="left")
            fileSize = str(file['size'])
            if file['size'] == 1 or file['size'] == 0:
                fileSize += " byte"
            else:
                fileSize += " bytes"
            file_size_label=ctk.CTkLabel(row_frame,text=fileSize,font=("Arial", 16),width=int((self.width-200)*0.4))
            file_size_label.pack(side="left")
            download_button=ctk.CTkButton(row_frame,text="Download",font=("Arial", 16),fg_color="#00A2FF",text_color="white",corner_radius=5,width=int((self.width-200)*0.2),command=lambda: self.downloadFile(file['filename']))
            download_button.pack(side="left")
            row_frame.pack()
            # Horizontal line
            horizontal_line=ctk.CTkFrame(scroll_frame,width=self.width-200,height=1,fg_color="#9E9E9E",border_color="#9E9E9E",border_width=1)
            horizontal_line.pack()
        # Pack
        scroll_frame.pack(fill="both", expand=True)
        self.shared_file_frame.pack(fill="both", expand=True)
        # Remove my files frame
        if removeOtherFrame and hasattr(self, 'my_file_frame'):
            self.my_file_frame.pack_forget()

    def showMyFiles(self,removeOtherFrame=True):
        if hasattr(self, 'current_frame') and self.current_frame == "my_files":
            return
        self.current_frame = "my_files"
        self.my_file_frame=ctk.CTkFrame(self.right_frame,width=self.width-150,height=self.height,fg_color="white")
        # Label
        label=ctk.CTkLabel(self.my_file_frame,text="My files",font=("Arial", 30))
        label.pack(pady=20)
        # File upload button
        upload_frame=ctk.CTkFrame(self.my_file_frame,width=self.width-200,height=25,fg_color="white")
        upload_frame.pack_propagate(0)
        upload_label=ctk.CTkLabel(upload_frame,text="Upload file:",font=("Arial", 18))
        upload_label.pack(side="left",padx=(0,20))
        upload_button=ctk.CTkButton(upload_frame,text="Choose",font=("Arial", 16),fg_color="#9E9E9E",text_color="white",corner_radius=5,command=lambda: self.uploadFile(2),hover_color="#6C6C6C")
        upload_button.pack(side="left")
        upload_frame.pack()
        # Header frame
        header_frame=ctk.CTkFrame(self.my_file_frame,width=self.width-150,height=50,fg_color="white")
        header_frame.pack_propagate(0)
        file_name_label=ctk.CTkLabel(header_frame,text="File name",font=("Arial", 16),width=int((self.width-200)*0.4))
        file_name_label.pack(side="left")
        file_size_label=ctk.CTkLabel(header_frame,text="File size",font=("Arial", 16),width=int((self.width-200)*0.4))
        file_size_label.pack(side="left")
        action_label=ctk.CTkLabel(header_frame,text="Action",font=("Arial", 16),width=int((self.width-200)*0.2))
        action_label.pack(side="left")
        header_frame.pack()
        # Horizontal line
        horizontal_line=ctk.CTkFrame(self.my_file_frame,width=self.width-200,height=1,fg_color="#9E9E9E",border_color="#9E9E9E",border_width=1)
        horizontal_line.pack()
        # Scrollable frame
        scroll_frame=ctk.CTkScrollableFrame(self.my_file_frame,width=self.width-150,fg_color="white",scrollbar_button_color="white")
        # File list
        files=self.app.getMyFiles()
        # Create a row for each file
        for file in files:
            row_frame=ctk.CTkFrame(scroll_frame,width=self.width-150,height=50,fg_color="white")
            row_frame.pack_propagate(0)
            file_name_label=ctk.CTkLabel(row_frame,text=file['filename'],font=("Arial", 16),width=int((self.width-200)*0.4))
            file_name_label.pack(side="left")
            fileSize = str(file['size'])
            if file['size'] == 1 or file['size'] == 0:
                fileSize += " byte"
            else:
                fileSize += " bytes"
            file_size_label=ctk.CTkLabel(row_frame,text=fileSize,font=("Arial", 16),width=int((self.width-200)*0.4))
            file_size_label.pack(side="left")
            upload_button=ctk.CTkButton(row_frame,text="Share",font=("Arial", 16),fg_color="#00A2FF",text_color="white",corner_radius=5,width=int((self.width-200)*0.2),command=lambda: self.shareFile(file['filename']))
            upload_button.pack(side="left")
            row_frame.pack()
            # Horizontal line
            horizontal_line=ctk.CTkFrame(scroll_frame,width=self.width-200,height=1,fg_color="#9E9E9E",border_color="#9E9E9E",border_width=1)
            horizontal_line.pack()
        # Pack
        scroll_frame.pack(fill="both", expand=True)
        self.my_file_frame.pack(fill="both", expand=True)
        # Remove shared files frame
        if removeOtherFrame and hasattr(self, 'shared_file_frame'):
            self.shared_file_frame.pack_forget()

    def downloadFile(self,filename):
        self.app.downloadFile(filename)
        # self.current_frame=""
        # self.shared_file_frame.pack_forget()
        # self.showSharedFiles()

    def shareFile(self,filename):
        self.app.shareFile(filename)
        # self.current_frame=""
        # self.my_file_frame.pack_forget()
        # self.showMyFiles()

    def uploadFile(self,flag):
        filePath=ctk.filedialog.askopenfilename()
        if filePath == "":
            return
        self.app.uploadShareFile(filePath) if flag == 1 else self.app.uploadMyFile(filePath)

def initWindow(APP_NAME, WIDTH, HEIGHT,SHARE_DIR,LOCAL_DIR):
    root=ctk.CTk()
    root.title(APP_NAME)
    root.geometry(f"{WIDTH}x{HEIGHT}")
    App(root, WIDTH, HEIGHT,SHARE_DIR,LOCAL_DIR)
    root.mainloop()
