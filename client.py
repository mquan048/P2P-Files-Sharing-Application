import os
from client_modules.window import initWindow
from client_modules.socket import initSocket
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
SERVER_HOST = os.getenv('SERVER_HOST')
SERVER_PORT = int(os.getenv('SERVER_PORT'))
BUFFE_SIZE  = int(os.getenv('BUFFE_SIZE'))
HEIGHT		= int(os.getenv('HEIGHT'))
WIDTH		= int(os.getenv('WIDTH'))
APP_NAME   	= os.getenv('APP_NAME')
SHARE_DIR   = os.getenv('SHARE_DIR')
LOCAL_DIR   = os.getenv('LOCAL_DIR')

if __name__ == '__main__':
    try:
        # Initialize socket connection
        server, peer = initSocket(SERVER_HOST, SERVER_PORT, BUFFE_SIZE, LOCAL_DIR, SHARE_DIR)
    	# Initialize window
        initWindow(APP_NAME, WIDTH, HEIGHT, SHARE_DIR, LOCAL_DIR, server, peer)
    except Exception as e:
        print(f"An exception occurred: {e}")
    finally:
        print("Program terminated")
        os._exit(0)