
# Django Ecommerce RESTful API

an API built with Django and Django REST Framework  




## Start your app

1- Creating a new virtual enviroment :
```
python3.9 -m venv myvenv
```

2- Activate the virtual enviroment :

**Windows**
```
myvenv/Scripts/activate
```

**Linux**
```
source myvenv/bin/activate
```

3- Install project requirements :
```
pip install -r requirements.txt
```

4- Make migrations :
```
python manage.py makemigrations
```

5- Migrate :
```
python manage.py migrate
```
6- Setup email sending service (to send activation tokens and reset password), by adding email and pasword in ecommerce/settings.py

7- Finally, run the development server :
```
python manage.py runserver 
```


## Features

**General API**
+ Full Authentication system ( Register(email verification), login, logout, forget
password{via email) )

+ user could ( add products to favorite, rate and write reviews to products, have
multiple addresses, update profile information )

+ advanced search for products / filter products by [category, subcategory, popularity,
price range and more]

+ discount coupons and discount per product options are available with expiry date
and max number of orders for both

+ the ability to confirm orders by user, and cancel without affecting the stock quantity

**Dashboard API**
+ special login for staff users accounts

+ staff users also can't authenticate to the client General API
+ CRUD for all sections based on (groups permissions) given to the staff user

+ the ability to show alll pending orders and update orders status (canceled, accepted,
delivered, in-way and rejected) and notify the user with it

