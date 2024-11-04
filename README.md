What is this?:\
This is a simple website that allows for users to submit information about themselves relating to their health.
The intent of this is to use their submitted data to create an A.I that can help diagnose people who are at risk of
having a stroke.\
\
To help start the website data, a dataset from Kaggle is provided called "healthcare-dataset-stroke-data.csv" which can
be loaded into the website while it is running.\
\
How do you run it?:\
Before you can run this website, please make sure you have Docker Desktop and the community edition of MongoDB installed.\
Both can be found at:\
Docker Desktop: https://docs.docker.com/desktop/install/windows-install/\
MongoDB Community Server: https://www.mongodb.com/try/download/community-kubernetes-operator\
\
After installing them, there are two ways to launch the website:\
1. Docker Compose:\
    This way is the simplest:\
        -1. Make sure Docker Desktop is running.\
        2. Use a command prompt and open it to the same directory as this README.md.\
        3. Enter `docker-compose up --build`.\
    Once docker compose is run, wait for docker to set everything up and then connect to the website\
    using the localhost on port 5000.\
    Note: Using Docker Compose does not allow you to see print statements nor can you enter MySQL commands.\

2. Multiple command lines:
    1. Open one instance of the command line and one instance of PowerShell.
    2. In both the command prompt and PowerShell windows, navigate to the ./HealthStack/ directory which is a subdirectory in the same directory as this README.md file.
    3. Modify the "deployed" variable in app.py and db_handler.py to be False. Leaving it as True will not allow the website to run correctly.
    4. Run "python app.py" in the command line.
    5. In the PowerShell window, make sure Docker Desktop is running and then enter the following commands in order:\
        -`docker run --name healthDB -p1234:3306 -e MYSQL_ROOT_PASSWORD=healthyboi -d mysql`
        -`docker cp healthdb.sql healthDB:healthdb.sql`
        -`docker exec -it healthDB mysql -p`
    After running these commands, the PowerShell window will now be in MySQL where you can enter MySQL commands.
    6. Connect to the website using the localhost on port 5000.\

How do I use the Admin?:
To use the admin, make sure you visit the home page of the website to hash their password and then go to the login screen and
enter the following username and password:\
    -Username: "baseadmin@example.com"\
    -Password: "healthyadmin"\
With this admin, you can make other users admins or delete them, delete patient data or delete all data from the tables. (Or dump the data)\

What is in this website?:\
    Routes:\
    This website contains the following pages:\
        Normal Pages:\
            -Home (Route: '/')\
                This is the home page\
            -Submission (Route: '/submission/)\
                -This is the page in which a logged in user can submit their data. If they already have, it will tell the user they cannot enter more.\
            -Submission Validation (Route: '/submission/validate/)\
                -This page attempts to save the entered submission to the databases and redirects to the user's account page when successful.\
            -View Data (Route: '/data/view/')\
                -This page allows logged in users to see patient data. They cannot see who submitted this data however.\
        
        Accout/User Pages:
            -Login (Route: '/users/login/)
                -Allows signed up users to login. Though I do feel I do not need to explain that.
            -Login Validation (Route: '/users/login/validate/')
                -Checks to see if the login details are correct and logs them in if they are. Redirects to the home page if the user successfully logs in.
            -Signup (Route: '/users/signup/)
                -Allows the user to enter account details to signup. Again, I feel I do not need to explain that.
            -Signup Validation (Route: '/users/signup/validate/')
                -Checks to see if the acount exists and if not, creates one. Redirects to the login page when successful.

            -User Account (Route: '/users/account/)
                -Allows the user to see their account information and any data they have submitted.
                -Also gives the user the option to delete their submitted data or modify it and delete their account or modify it.
            -User Modify (Route: '/users/account/modify/')
                -Allows the user to modify their account information.
            -User Modify Validate (Route: '/users/account/modify/validate/')
                -Updates the user's account with their new information.
            -User Submission Modify (Route: '/users/account/submission/modify/')
                -Allows the user to modify their data submission.

            -User Submission Modify Validate (Route: '/users/account/submission/modify/validate/')
                -Modifies the user's data submission with their new information.
            -Submission Deletion Confirmation ('/users/account/submission/delete/)
                -Asks the user if they are sure that they want to delete their submitted data.
            -Submission Deletion Confirmed ('/users/account/submission/delete/confirmed/')
                -Deletes the users submitted information and redirects them back to their account page.
            -User Deletion Confirmation (Route: '/users/account/delete/')
                -Asks the user if they are sure that they want to delete their account.

            -User Deletion Confirmed (Route: '/users/account/delete/confirmed/')
                -Deletes the user's account and redirects them to the home page.
            -User Logout (Route: '/users/logout/')
                -Logs the user out and redirects to the home page.

        Admin Pages (Note: These pages are only accessible by admins. If a user is not an admin or not logged in, they will get a 404 error for all of these pages):
            -Admin Main (Route: '/admin/')
                -The main admin page. Gives three options: User Management, Patient Management and Database Management.
            -Admin Users (Route: '/admin/users/')
                -Shows all the users on the website and allows for them to made admins (or revoke their admin access) or for them to be deleted.
                -Note: The BaseAdmin cannot be deleted and cannot have their admin access revoked.
            -Apply Admin (Rote: '/admin/users/makeadmin/user_id=<user_id>')
                -Makes the given user an admin or, if they are already an admin, revokes their admin access.
                -user_id is the given user ID. It must be provided when going to this page.
            -Admin User Delete (Route: '/admin/users/delete/user_id=<user_id>')
                -Deletes the given user.
                -If the user being deleted is the admin deleting them, the user is logged out and redirected to the home page.
                -user_id is the given user ID. It must be provided when going to this page.

            -Admin Patient Management MySQL (Route: '/admin/database/manage/)
                -Shows all patient data and allows for the admin to delete any. All data shown is from the MySQL database.
            -Admin Patient Management MongoDB (Route: '/admin/database/manage/mongodb/)
                -Shows all patient data, but does not allow for it to be deleted. All data shown is from the MongoDB database.
            -Admin Patient Delete (Route: '/admin/database/delete/patient_id=<patient_id>)
                -Deletes the given patient data from both the MongoDB database MySQL database.
            -Admin Database Management (Route: '/admin/all_database/manage/')
                -The database management page. Gives five options:
                    -Dump All Database Data.
                    -Delete All Users.
                    -Delete All Patients.
                    -Delete All Links.
                    -Delete All Data.
            
            -Admin Delete All Users (Route: '/admin/all_databases/manage/delete_users/')
                Asks the user if they are sure they want to delete all users.
            -Admin Delete All Users Confirmed (Route: '/admin/all_databases/manage/delete_users/confirmed/')
                Deletes all users (Apart from the BaseAdmin).
            -Admin Delete All patients (Route: '/admin/all_databases/manage/delete_patients/')
                Asks the user if they are sure they want to delete all patients.
            -Admin Delete All patients Confirmed (Route: '/admin/all_databases/manage/delete_patients/confirmed/')
                Deletes all patients.
            
            -Admin Delete All links (Route: '/admin/all_databases/manage/delete_links/')
                Asks the user if they are sure they want to delete all links.
            -Admin Delete All links Confirmed (Route: '/admin/all_databases/manage/delete_links/confirmed/')
                Deletes all links between users and patient data.
            -Admin "Nuke" (Route: '/users/all_databases/manage/delete_nuke_all/')
                -Asks the user if they are sure they want to delete EVERYTHING.
            -Admin "Nuke" Confirmed (Route: '/admin/all_databases/manage/delete_nuke_all/confirmed/)
                -Deletes all data from all databases apart from the BaseAdmin.
            
            -Admin Data Dump (Route: '/admin/all_databases/manage/dump/')
                -Saves all data from all database to three files in '/static/dumps/':
                    -table_users.txt.
                    -table_patient_data.txt.
                    -link_user_patient_data.txt.
            -Admin DB Loader (Route: '/admin/database/manage/load_db/')
                Loads all data from 'healthcare-dataset-stroke-data.csv' into the MySQL database and MongoDB database.
        
        -Error Pages:
            -404:
                Returns a rendered HTML template rather than default 404 page so that the nav bar is still shown.
                This page is shown a lot when a user does not have access or is not logged in and tries to access pages that require admin access or an account.
            -405:
                For simplicity, this redirects to the 404 page.

        -Misc:
            -Favicon (Route: '/favicon.ico')
                Returns the URL for the favicon.ico file in the static folder. Surpresses the favicon.ico error.

Noteworthy Files:\
    -app.py:\
        This Python file handles the website using Python Flask.\
    -db_handler.py:\
        Handles all database requests for the MySQL database.\
    -mongodb.py:\
        Handles all database requests for the MongoDB database.\
    -access_logger.py:\
        Handles all of the logging. When a user does anything, this file logs that action in '/static/logs.txt/'\

Thank you for reading, if you have. If you haven't... I don't care `¯\_(ツ)_/¯`.\
Have a good one.