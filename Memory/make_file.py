import os

def make_file(file_name: str):
    os.curdir("/Users/raaggee/Documents/betas/agent_state/Memory/test")

    try:
        with open(f"{file_name}.txt", "x") as file:
            file.write("\n\n")

        return "File Created..."

    except FileExistsError:
        return "File Already exists with this name"
    
def read_file(file_name: str):
    os.curdir("/Users/raaggee/Documents/betas/agent_state/Memory/test")

    try:
        with open(f"{file_name}.txt", "r") as file:
            return file.readline()
        
    except FileNotFoundError:
        return "File Doesn't exists..."
    
def delete_file(file_name: str):
    os.curdir("/Users/raaggee/Documents/betas/agent_state/Memory/test")

    try:
        os.remove(f"{file_name}.txt")
        return "File Deleted..."
    
    except FileNotFoundError:
        return "File not found..."

    
