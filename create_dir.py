import os

def mkdir_p(dir_path):
    if not os.path.isdir(dir_path):
        #dir_path doesn't exist
        #create dir_path
        # handle permission error
        print(f'{dir_path} not exists')
        try:
            os.mkdir(dir_path)         
            return True
        except PermissionError as e:
            print(e)
            return False

    else:
        #dir_path exists, do nothing
        print(f'{dir_path} exists')
        return True

if __name__ == "__main__":
    assert False == mkdir_p('/var/notExist')
    assert True == mkdir_p('screenshots')
