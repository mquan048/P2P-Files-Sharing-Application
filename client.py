import os
from client_modules.window import initWindow
from client_modules.socket import initSocket
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
SERVER_HOST = os.getenv('SERVER_HOST')
SERVER_PORT = os.getenv('SERVER_PORT')
BUFFE_SIZE  = os.getenv('BUFFER_SIZE')
HEIGHT		= int(os.getenv('HEIGHT'))
WIDTH		= int(os.getenv('WIDTH'))
APP_NAME   	= os.getenv('APP_NAME')

if __name__ == '__main__':
    try:
        # Initialize socket connection
        initSocket(SERVER_HOST, SERVER_PORT, BUFFE_SIZE)
    	# Initialize window
        initWindow(APP_NAME, WIDTH, HEIGHT)
    except Exception as e:
        print(f"An exception occurred: {e}")
    finally:
        print("Program terminated")