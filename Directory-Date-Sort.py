import datetime
from datetime import datetime, timedelta
import os
import subprocess
import shutil


# sort files based on modification time in directory
def list_based_mtime(foldername: str):
    files = os.listdir(foldername)
    files = [os.path.join(foldername, file) for file in files]
    files.sort(key=os.path.getmtime)
    return files


# create new directories in foldername:= recent: 1-2 weeks old, aged: ~1 month old(4-6 weeks), old: 6 weeks and older
def generate_folder_structure(foldername: str):
    recentpath = os.path.join(foldername, "recent")
    agedpath = os.path.join(foldername, "aged")
    oldpath = os.path.join(foldername, "old")
    try:
        if not os.path.isdir(recentpath):
            os.mkdir(recentpath)
        if not os.path.isdir(agedpath):
            os.mkdir(agedpath)
        if not os.path.isdir(oldpath):
            os.mkdir(oldpath)
    # path may be entered incorrectly, in such case return -1, the main loop will exit
    except FileNotFoundError as e:
        # print(e)
        return -1
    return 1


# move files from foldername/recent & foldername/aged & foldername/old  to foldername/
def move_files_in_folder(foldername: str) -> int:
    recentpath = os.path.join(foldername, "recent")
    agedpath = os.path.join(foldername, "aged")
    oldpath = os.path.join(foldername, "old")
    try:
        # move conents of /foldername/recent/ to /foldername/
        recentfiles = os.listdir(recentpath)
        for file in recentfiles:
            srcpath = os.path.join(recentpath, file)
            destpath = os.path.join(foldername, file)
            shutil.move(srcpath, destpath)
        #
        # move conents of /foldername/aged/ to /foldername/
        agedfiles = os.listdir(agedpath)
        for file in agedfiles:
            srcpath = os.path.join(agedpath, file)
            destpath = os.path.join(foldername, file)
            shutil.move(srcpath, destpath)
        #
        # move conents of /foldername/old/ to /foldername/
        oldfiles = os.listdir(oldpath)
        for file in oldfiles:
            srcpath = os.path.join(oldpath, file)
            destpath = os.path.join(foldername, file)
            shutil.move(srcpath, destpath)
    except Exception as e:
        # in case errors arise
        print(e)

    return


# move each file to the appropriate folder, based on mtime
def categorize_and_move(foldername: str, files: list):
    current_time = datetime.now()
    for file in files:
        # skip foldername/recent & foldername/aged & foldername/old to avoid duplicate of empty folder
        if os.path.isdir(file) and os.path.basename(file) in {"recent", "aged", "old"}:
            continue
        # get modification time(path.getctime gives last metadata change. not what we need, since the file could've been moved in previous iterations of script. nullifying the sorting preocess)
        mtime = os.path.getmtime(file)
        converted_mtime = datetime.fromtimestamp(mtime)
        time_diff = current_time - converted_mtime
        # print(f"mtime and timediff for {file} : {
        #       converted_mtime} , {time_diff}")
        if time_diff < timedelta(weeks=2):
            destination = "recent"
        elif time_diff < timedelta(weeks=6):
            destination = "aged"
        else:
            destination = "old"
        # move file to appropriate folder
        destpath = os.path.join(foldername, destination)
        shutil.move(file, destpath)
    # end for
    return

# use $gio to move old/* to trash


def move_to_trash(foldername: str):
    oldpath = os.path.join(foldername, "old")
    gio_command = f"gio trash -f {oldpath}/*"
    try:
        print(f"Moving to trash...")
        result = subprocess.run(gio_command, shell=True, check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    except:
        # running $gio with -f flag surpresses any errors.
        pass
    print("Complete!")
    return


def cleaner(foldername: str):
    ''' call helper functions to: 
            1. create sorting folder structure(if one doesn't exist)
            2. move files from sorting folder structure one level up (if such structure holds files)
            3. create a sorted list of files with their appropriate modification times
            4. categorize each file based on mtime and move to the appropriate destination folder in the sorting structure
            5. prompt if the user wants to move old/* to trash
    '''
    result = generate_folder_structure(foldername)
    if result == -1:
        print("----------")
        print(f"Error in folder structure generation.\nCheck if entered path:{
              foldername} is valid.")
        print("----------")
        return
    #
    move_files_in_folder(foldername)
    #
    files = list_based_mtime(foldername)
    #
    categorize_and_move(foldername, files)
    #
    delete = input("Would you like to move the old files to trash (Y/n)?")
    if delete == 'Y':
        move_to_trash(foldername)
    print("Done.")
    return


# simple directory cleaner can take any argument as a path to preform oragnization and (if ordered) move to trash
def main():
    print("Specify the complete folder path that you would like to sort.")
    try:
        foldername = input(
            "To use default folder /$home/$user/Downloads/ press [Enter]: ")
    except KeyboardInterrupt:
        print("")
        print("Interruption deteced. Exiting.")
        return

    if not foldername:
        home = os.environ['HOME']
        # user = os.environ['USER']
        print("No folder received. Executing on default folder: /$HOME/$USER/Downloads/")
        foldername = os.path.join(home, 'Downloads')

    cleaner(foldername)
    return

#
if __name__ == "__main__":
    main()
