# BlackBliss-Updated

TO use this Project you have to simply clone the repo and use it 
The admin Credentials are username admin and password admin
Then for payment feature to work you have to set a paypal developer account in that you have to create a account and then you have to create a api credentials in app and credentials
Then you have to copy the clinte id and paste it in the format of 
<script src="https://www.paypal.com/sdk/js?client-id=// Your clint id //&currency=USD"></script>
<script type="text/javascript">
Then you have to create a sandbox account one personal and one business
Then when you click on pay through paypal in the website then a window will open in that you have to enter the personal account email and password to login and pay the amount will be creditied in the business account.
With this the payment feature will work rest all the things are working make sure to use this commands 
python -m venv .venv
.venv\Scripts\Activate.ps1
then pip requirments.txt
then python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Note this project use Django Default Database i.e sqlite3 if you want you can you any of your choice 
