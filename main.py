import bcrypt, json, os, PIL
import customtkinter as ctk

database = {
    'users' : [],
    'items' : []
}
active_user = None
errormessage = ''
pages = {}
widgets = {}
startup_image = ctk.CTkImage(dark_image=PIL.Image.open('data\\startupimage.png'),size=(1280,720))

DATABASE_LOCATION = 'data\\database.json'

def set_page(newpage):
    global pages
    [page.forget() for page in pages.values()]
    newpage.pack(fill='both',expand=True)

def update():
    global pages
    [page.update() for page in pages.values()]

def reset_errormessage(errorlabel):
    global pages,widgets
    widgets[f'{errorlabel}'].configure(text='')
    update()

def handle_database():
    global database

    if not os.path.exists('data'):
        os.makedirs('data')

    if not os.path.exists(DATABASE_LOCATION):
        with open(DATABASE_LOCATION, 'w') as file:
            json.dump(database,file)
    else:
        with open(DATABASE_LOCATION, 'r') as file:
            database = json.load(file)

def update_database():
    global database

    if not os.path.exists(DATABASE_LOCATION):
        return
    with open(DATABASE_LOCATION, 'w') as file:
        json.dump(database,file)

def get_user_index(username):
    global database

    if username.lower() not in list(list(users.keys())[0].lower() for users in database['users']):
        return False
    return database['users'].index([user for user in database['users'] if list(user.keys())[0] == f'{username}'][0])

def get_item_index(itemid):
    global database
    item_list = [list(item.keys())[0] for item in database['items']]
    if str(itemid) not in item_list:
        return -1
    return database['items'].index([item for item in database['items'] if list(item.keys())[0] == itemid][0])

def update_items():
    global database
    add_to_itemframe()
    update_user_profile()

def create_user(username,password):
    global database
    user = {
        f'{username}' : f'{password}',
        'balance' : 5000,
        'items' : []
    }
    database['users'].append(user)
    update_database()

def add_item():
    global database, active_user, widgets,errormessage
    if not active_user:
        widgets['itemerrorlabel'].configure(text='Error: no user logged in!')
        update()
        pages['additempage'].after(2000,lambda:reset_errormessage('itemerrorlabel'))
        return
    if not database['items']:
        id = '0'
    else:
        id = str(int(list(database['items'][-1].keys())[0]) + 1)
    name = widgets['itemnamebox'].get().strip()
    desc = widgets['itemdescbox'].get().strip()
    price = widgets['itempricebox'].get().strip()
    if not name or not price:
        widgets['itemerrorlabel'].configure(text='Missing required information!')
        update()
        pages['additempage'].after(2000,lambda:reset_errormessage('itemerrorlabel'))
        return
    if len(name)<3 or len(name)>16:
        widgets['itemerrorlabel'].configure(text='Name must be between 3 and 16 characters!')
        update()
        pages['additempage'].after(2000,lambda:reset_errormessage('itemerrorlabel'))
        return
    if not price.isnumeric() or int(price) < 250 or int(price) > 10000:
        widgets['itemerrorlabel'].configure(text='Price must be integer between 250 and 10000!')
        update()
        pages['additempage'].after(2000,lambda:reset_errormessage('itemerrorlabel'))
        return
    item = {
            id : name,
            'desc' : desc,
            'price' : int(price),
            'owner' : active_user
    }
    database['items'].append(item)
    update_database()
    widgets['itemnamebox'].delete(0, 'end')
    widgets['itemdescbox'].delete(0, 'end')
    widgets['itempricebox'].delete(0, 'end')
    widgets['itemnamebox'].focus()
    widgets['itemerrorlabel'].configure(text='Item added!')
    pages['additempage'].after(2000,lambda:reset_errormessage('itemerrorlabel'))
    update()
    update_items()

def add_to_itemframe():
    for item in widgets['itemframe'].winfo_children():
        item.destroy()

    currentitem = ctk.CTkFrame(widgets['itemframe'],width=1000,height=150,fg_color="#D3D2D2")
    currentitem.pack(padx=15,pady=15,fill="both", expand=True)
    currentitem.grid_columnconfigure((0,1,2,3),weight=1)
    itemname = ctk.CTkLabel(currentitem,text='Name',text_color="#000000",font=('Arial',30))
    itemname.grid(row=0,column=0,padx=25,pady=25)
    itemdesc = ctk.CTkLabel(currentitem,text='Description',text_color="#000000",font=('Arial',30))
    itemdesc.grid(row=0,column=1,padx=25,pady=25)
    itemprice = ctk.CTkLabel(currentitem,text='Price',text_color="#000000",font=('Arial',30))
    itemprice.grid(row=0,column=2,padx=25,pady=25)
    buy = ctk.CTkLabel(currentitem,text='Buy',text_color="#000000",font=('Arial',30))
    buy.grid(row=0,column=3,padx=25,pady=25)

    for item in database['items']:
        id = list(item.keys())[0]
        currentitem = ctk.CTkFrame(widgets['itemframe'],width=1000,height=150,fg_color="#D3D2D2")
        currentitem.pack(padx=15,pady=15,fill="both", expand=True)
        currentitem.grid_columnconfigure((0,1,2,3),weight=1)
        itemname = ctk.CTkLabel(currentitem,text=item[str(id)],text_color="#000000",font=('Arial',30))
        itemname.grid(row=0,column=0,padx=25,pady=25)
        itemdesc = ctk.CTkLabel(currentitem,text=item['desc'],text_color="#000000",font=('Arial',30))
        itemdesc.grid(row=0,column=1,padx=25,pady=25)
        itemprice = ctk.CTkLabel(currentitem,text=f'${item['price']}',text_color="#000000",font=('Arial',30))
        itemprice.grid(row=0,column=2,padx=25,pady=25)
        buybutton = ctk.CTkButton(currentitem,text='Buy',fg_color="#2B2B2B",hover_color="#222222",font=('Arial',30),command=lambda id=id, item=item:buy_item(id,item))
        buybutton.grid(row=0,column=3,padx=25,pady=25)

def update_user_profile():
    global active_user
    for item in widgets['useritems'].winfo_children():
        item.destroy()

    widgets['profilename'].configure(text=active_user)
    widgets['profileamount'].configure(text=f'${database['users'][get_user_index(active_user)]['balance']}')
    update()

    for item in database['users'][get_user_index(active_user)]['items']:
        currentitem = ctk.CTkFrame(widgets['useritems'],width=1000,height=150,fg_color="#D3D2D2")
        currentitem.pack(padx=15,pady=15,fill="both", expand=True)
        currentitem.grid_columnconfigure((0,1),weight=1)
        itemname = ctk.CTkLabel(currentitem,text=item['name'],text_color="#000000",font=('Arial',30))
        itemname.grid(row=0,column=0,padx=25,pady=25)
        itemprice = ctk.CTkLabel(currentitem,text=f'${item['price']}',text_color="#000000",font=('Arial',30))
        itemprice.grid(row=0,column=1,padx=25,pady=25)

def buy_item(id,item):
    global active_user, database
    itemid = id
    item_index = get_item_index(itemid)
    user_index = get_user_index(active_user)
    if item_index == -1:
        widgets['homeerrorlabel'].configure(text='Item not found!')
        update()
        pages['homepage'].after(2000,lambda:reset_errormessage('homeerrorlabel'))
        return
    item_name = item[itemid]
    item_price = item['price']
    item_owner = item['owner']
    if active_user == item_owner:
        widgets['homeerrorlabel'].configure(text='Cannot buy your own item!')
        update()
        pages['homepage'].after(2000,lambda:reset_errormessage('homeerrorlabel'))
        return
    if database['users'][user_index]['balance'] < item_price:
        widgets['homeerrorlabel'].configure(text='insufficient balance!')
        update()
        pages['homepage'].after(2000,lambda:reset_errormessage('homeerrorlabel'))
        return
    database['users'][get_user_index(active_user)]['balance'] -= item_price
    if item_owner in list(list(users.keys())[0].lower() for users in database['users']):
        database['users'][get_user_index(item['owner'])]['balance'] += item_price
    user_item = {
        'name':item_name,
        'price':item_price
    }
    database['users'][get_user_index(active_user)]['items'].append(user_item)
    widgets['homeerrorlabel'].configure(text=f'{active_user} bought {item_name} for {item['price']}.')
    update()
    pages['homepage'].after(2000,lambda:reset_errormessage('homeerrorlabel'))
    del database['items'][item_index]
    update_database()
    update_items()
    widgets['activeuserlabel'].configure(text=f'Logged in as: {active_user}, ${database['users'][get_user_index(active_user)]['balance']}.')
    update()
    return True

def add_funds():
    global widgets, active_user, database
    if not active_user:
        widgets['fundserrorlabel'].configure(text='No active user!')
        update()
        pages['addfundspage'].after(2000,lambda:reset_errormessage('fundserrorlabel'))
        return
    amount = widgets['addfundsbox'].get().strip()
    widgets['addfundsbox'].delete(0, 'end')
    if not amount.isnumeric() or int(amount) < 500 or int(amount) > 5000:
        widgets['fundserrorlabel'].configure(text='Amount must be integer and between 500 to 5000!')
        update()
        pages['addfundspage'].after(2000,lambda:reset_errormessage('fundserrorlabel'))
        return
    database['users'][get_user_index(active_user)]['balance'] += int(amount)
    update_database()
    widgets['fundserrorlabel'].configure(text='Amount added!')
    pages['addfundspage'].after(2000,lambda:reset_errormessage('fundserrorlabel'))
    widgets['activeuserlabel'].configure(text=f'Logged in as: {active_user}, ${database['users'][get_user_index(active_user)]['balance']}.')
    update()
    return True

def register():
    global database
    username = widgets['usernamebox'].get().strip()
    password = widgets['passwordbox'].get().strip()
    while len(username) < 8 or len(username) > 32 or any([not ch.isalnum() for ch in username]):
        widgets['errorlabel'].configure(text='Username must be between 8 and 32 characters and alphanumeric!')
        widgets['usernamebox'].delete(0, 'end')
        widgets['passwordbox'].delete(0, 'end')
        widgets['usernamebox'].focus()
        update()
        widgets['errorlabel'].after(2000,lambda:reset_errormessage('errorlabel'))
        return
    user_list = [list(users.keys())[0].lower() for users in database['users']]
    if username.lower() in user_list:
        widgets['errorlabel'].configure(text='User already exists!')
        widgets['usernamebox'].delete(0, 'end')
        widgets['passwordbox'].delete(0, 'end')
        widgets['usernamebox'].focus()
        update()
        widgets['errorlabel'].after(2000,lambda:reset_errormessage('errorlabel'))
        return
    while len(password) < 8 or len(password) > 32 or any([not ch.isalnum() for ch in password]):
        widgets['errorlabel'].configure(text='Password must be between 8 and 32 characters and alphanumeric!')
        widgets['usernamebox'].delete(0, 'end')
        widgets['passwordbox'].delete(0, 'end')
        widgets['usernamebox'].focus()
        update()
        widgets['errorlabel'].after(2000,lambda:reset_errormessage('errorlabel'))
        return
    hashed_password = str(bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()))[2:-1]
    create_user(username,hashed_password)
    login()

def login():
    global database, active_user
    username = widgets['usernamebox'].get().strip()
    password = widgets['passwordbox'].get().strip()
    update()
    user_list = [list(users.keys())[0].lower() for users in database['users']]
    if username.lower() not in user_list:
        widgets['errorlabel'].configure(text='Invalid username or password!')
        pages['loginpage'].after(2000,lambda:reset_errormessage('errorlabel'))
        widgets['usernamebox'].delete(0, 'end')
        widgets['passwordbox'].delete(0, 'end')
        widgets['usernamebox'].focus()
        update()
        return
    else:
        check_password: str = database['users'][get_user_index(username)][username]
        if not bcrypt.checkpw(password.encode('utf-8'),check_password.encode('utf-8')):
            widgets['errorlabel'].configure(text='Invalid username or password!')
            pages['loginpage'].after(2000,lambda:reset_errormessage('errorlabel'))
            widgets['usernamebox'].delete(0, 'end')
            widgets['passwordbox'].delete(0, 'end')
            widgets['usernamebox'].focus()
            update()
            return
    active_user = username
    update_items()
    widgets['activeuserlabel'].configure(text=f'Logged in as: {active_user}, ${database['users'][get_user_index(active_user)]['balance']}.')
    set_page(pages['homepage'])
    widgets['usernamebox'].delete(0, 'end')
    widgets['passwordbox'].delete(0, 'end')
    widgets['usernamebox'].focus()
    update()

def log_out():
    global active_user
    active_user = None
    set_page(pages['loginpage'])

def create_app():
    global pages,widgets
    app = ctk.CTk()
    app.title('Shopping App')
    width = 1280
    height = 720
    x = app.winfo_screenwidth() // 2 - width // 2
    y = (app.winfo_screenheight() // 2 - height // 2) - 25
    app.geometry(f'{width}x{height}+{x}+{y}')
    app.resizable(True,True)
    
    loginpage = ctk.CTkFrame(app,fg_color="#D3D2D2",width=width,height=height,corner_radius=0)
    loginpage.grid_columnconfigure((0,1),weight=1)
    loginpage.grid_rowconfigure(0,weight=0)
    loginpage.grid_rowconfigure((1,2,3),weight=1)
    errorlabel = ctk.CTkLabel(loginpage,text=errormessage,text_color="#CC0000",font=('Arial',15))
    errorlabel.grid(row=0,column=0,columnspan=2,padx=25,pady=25)
    widgets['errorlabel'] = errorlabel
    usernamelabel = ctk.CTkLabel(loginpage,text='Username:',text_color="#000000",font=('Arial',30))
    usernamelabel.grid(row=1,column=0,padx=25,pady=25)
    passwordlabel = ctk.CTkLabel(loginpage,text='Password:',text_color="#000000",font=('Arial',30))
    passwordlabel.grid(row=2,column=0,padx=25,pady=25)
    usernamebox = ctk.CTkEntry(loginpage,width=350,height=50,border_width=0,corner_radius=5,font=('Arial',30))
    usernamebox.grid(row=1,column=1,padx=25,pady=25)
    widgets['usernamebox'] = usernamebox
    passwordbox = ctk.CTkEntry(loginpage,width=350,height=50,border_width=0,corner_radius=5,show='*',font=('Arial',30))
    passwordbox.grid(row=2,column=1,padx=25,pady=25)
    widgets['passwordbox'] = passwordbox
    loginbutton = ctk.CTkButton(loginpage,text='Login',fg_color="#2B2B2B",hover_color="#222222",font=('Arial',30), command=login)
    loginbutton.grid(row=3,column=0,padx=25,pady=25)
    registerbutton = ctk.CTkButton(loginpage,text='Register',fg_color="#2B2B2B",hover_color="#222222",font=('Arial',30), command=register)
    registerbutton.grid(row=3,column=1,padx=25,pady=25)
    usernamebox.bind('<Return>', lambda event:passwordbox.focus())
    passwordbox.bind('<Return>', lambda event:login())

    homepage = ctk.CTkFrame(app,fg_color="#D3D2D2",width=width,height=height,corner_radius=0)
    homepage.grid_columnconfigure(0, weight=1)
    homepage.grid_rowconfigure(1, weight=1)
    userbar = ctk.CTkFrame(homepage,fg_color="#D3D2D2",corner_radius=0)
    userbar.grid(row=0,column=0,sticky='ew')
    userbar.grid_columnconfigure((0,1,2,3),weight=1)
    profilebutton = ctk.CTkButton(userbar,text='Profile',fg_color="#2B2B2B",hover_color="#222222",font=('Arial',30), command=lambda:set_page(profilepage))
    profilebutton.grid(row=0,column=0,padx=25,pady=15)
    addfundsbutton = ctk.CTkButton(userbar,text='Add Funds',fg_color="#2B2B2B",hover_color="#222222",font=('Arial',30),command=lambda:set_page(addfundspage))
    addfundsbutton.grid(row=0,column=1,padx=25,pady=15)
    activeuserlabel = ctk.CTkLabel(userbar,text='',text_color="#000000",font=('Arial',30))
    activeuserlabel.grid(row=0,column=2,padx=25,pady=15)
    logoutbutton = ctk.CTkButton(userbar,text='Log Out',fg_color="#2B2B2B",hover_color="#222222",font=('Arial',30), command=log_out)
    logoutbutton.grid(row=0,column=3,padx=25,pady=15)
    widgets['activeuserlabel'] = activeuserlabel
    itemarea = ctk.CTkFrame(homepage,fg_color="#D3D2D2",width=width,height=500,corner_radius=0)
    itemarea.grid(row=1,column=0,sticky='nsew')
    itemarea.grid_rowconfigure(0, weight=1) 
    itemarea.grid_columnconfigure(0, weight=1)
    itemframe = ctk.CTkScrollableFrame(itemarea,corner_radius=0)
    itemframe.grid(row=0,column=0,sticky='nsew')
    widgets['itemframe'] = itemframe
    optionarea = ctk.CTkFrame(homepage,fg_color="#D3D2D2",width=width,height=80,corner_radius=0)
    optionarea.grid(row=2,column=0,sticky='ew')
    optionarea.grid_columnconfigure((0),weight=1)
    homeerrorlabel = ctk.CTkLabel(optionarea,text=errormessage,text_color="#CC0000",font=('Arial',15))
    homeerrorlabel.grid(row=0,column=0,pady=5)
    widgets['homeerrorlabel'] = homeerrorlabel
    additembutton = ctk.CTkButton(optionarea,text='Add Item',fg_color="#2B2B2B",hover_color="#222222",font=('Arial',30),command=lambda:set_page(additempage))
    additembutton.grid(row=1,column=0,pady=10)

    additempage = ctk.CTkFrame(app,fg_color="#D3D2D2",bg_color="#D3D2D2",width=width,height=height,corner_radius=0)
    additempage.grid_columnconfigure((0,1),weight=1)
    additemlabel = ctk.CTkLabel(additempage,text='Add Item', text_color='black',font=('Arial',30))
    additemlabel.grid(row=0,column=0,columnspan=2,padx=25,pady=25)
    itemerrorlabel = ctk.CTkLabel(additempage,text=errormessage,text_color="#CC0000",font=('Arial',15))
    itemerrorlabel.grid(row=1,column=0,columnspan=2,padx=25,pady=25)
    widgets['itemerrorlabel'] = itemerrorlabel
    itemname = ctk.CTkLabel(additempage,text='Name', text_color='black',font=('Arial',30))
    itemname.grid(row=2,column=0,padx=25,pady=25)
    itemnamebox = ctk.CTkEntry(additempage,width=350,height=50,border_width=0,corner_radius=5,font=('Arial',30))
    itemnamebox.grid(row=2,column=1,padx=25,pady=25)
    widgets['itemnamebox'] = itemnamebox
    itemdesc = ctk.CTkLabel(additempage,text='Description', text_color='black',font=('Arial',30))
    itemdesc.grid(row=3,column=0,padx=25,pady=25)
    itemdescbox = ctk.CTkEntry(additempage,width=350,height=50,border_width=0,corner_radius=5,font=('Arial',30))
    itemdescbox.grid(row=3,column=1,padx=25,pady=25)
    widgets['itemdescbox'] = itemdescbox
    itemprice = ctk.CTkLabel(additempage,text='Price', text_color='black',font=('Arial',30))
    itemprice.grid(row=4,column=0,padx=25,pady=25)
    itempricebox = ctk.CTkEntry(additempage,width=350,height=50,border_width=0,corner_radius=5,font=('Arial',30))
    itempricebox.grid(row=4,column=1,padx=25,pady=25)
    widgets['itempricebox'] = itempricebox
    additembutton = ctk.CTkButton(additempage,text='Confirm',fg_color="#2B2B2B",hover_color="#222222",font=('Arial',30),command=add_item)
    additembutton.grid(row=5,column=0,padx=25,pady=25)
    backbutton = ctk.CTkButton(additempage,text='Go Back',fg_color="#2B2B2B",hover_color="#222222",font=('Arial',30),command=lambda:set_page(homepage))
    backbutton.grid(row=5,column=1,padx=25,pady=25)
    itemnamebox.bind('<Return>', lambda event:itemdescbox.focus())
    itemdescbox.bind('<Return>', lambda event:itempricebox.focus())
    itempricebox.bind('<Return>', lambda event:add_item())

    profilepage = ctk.CTkFrame(app,fg_color="#D3D2D2",bg_color="#D3D2D2",width=width,height=height,corner_radius=0)
    profilepage.grid_columnconfigure(0,weight=1)
    profilepage.grid_rowconfigure(2,weight=1)
    profilename = ctk.CTkLabel(profilepage,text='name',text_color="#000000",font=('Arial',30))
    profilename.grid(row=0,column=0,padx=25,pady=15)
    widgets['profilename'] = profilename
    profileamount = ctk.CTkLabel(profilepage,text='$1000',text_color="#000000",font=('Arial',30))
    profileamount.grid(row=1,column=0,padx=25,pady=15)
    widgets['profileamount'] = profileamount
    useritems = ctk.CTkScrollableFrame(profilepage)
    useritems.grid(row=2,column=0,sticky='nsew')
    widgets['useritems'] = useritems
    backbutton = ctk.CTkButton(profilepage,text='Go back',fg_color="#2B2B2B",hover_color="#222222",font=('Arial',30),command=lambda:set_page(homepage))
    backbutton.grid(row=3,column=0,padx=25,pady=25)

    addfundspage = ctk.CTkFrame(app,fg_color="#D3D2D2",bg_color="#D3D2D2",width=width,height=height,corner_radius=0)
    addfundspage.grid_columnconfigure((0,1),weight=1)
    addfundspage.grid_rowconfigure(0,weight=0)
    addfundspage.grid_rowconfigure((1,2),weight=1)
    fundserrorlabel = ctk.CTkLabel(addfundspage,text=errormessage,text_color="#CC0000",font=('Arial',15))
    fundserrorlabel.grid(row=0,column=0,columnspan=4,padx=25,pady=25)
    widgets['fundserrorlabel'] = fundserrorlabel
    amountlabel = ctk.CTkLabel(addfundspage,text='Amount', text_color='black',font=('Arial',30))
    amountlabel.grid(row=1,column=0,padx=25,pady=25)
    addfundsbox = ctk.CTkEntry(addfundspage,width=350,height=50,border_width=0,corner_radius=5,font=('Arial',30))
    addfundsbox.grid(row=1,column=1,padx=25,pady=25)
    widgets['addfundsbox'] = addfundsbox
    addfundsbutton = ctk.CTkButton(addfundspage,text='Add',fg_color="#2B2B2B",hover_color="#222222",font=('Arial',30),command=add_funds)
    addfundsbutton.grid(row=2,column=0,padx=25,pady=25)
    backbutton = ctk.CTkButton(addfundspage,text='Go Back',fg_color="#2B2B2B",hover_color="#222222",font=('Arial',30),command=lambda:set_page(homepage))
    backbutton.grid(row=2,column=1,padx=25,pady=25)
    addfundsbox.bind('<Return>', lambda event:add_funds())


    startupscreen = ctk.CTkFrame(app,width=width,height=height,corner_radius=0)
    start_image = ctk.CTkLabel(startupscreen,width=width,height=height,text='',image=startup_image)
    start_image.pack()

    pages['startupscreen'] = startupscreen
    pages['loginpage'] = loginpage
    pages['homepage'] = homepage
    pages['additempage'] = additempage
    pages['profilepage'] = profilepage
    pages['addfundspage'] = addfundspage

    startupscreen.pack()
    app.after(2000,lambda:set_page(loginpage))

    app.mainloop()


if __name__ == '__main__':
    handle_database()
    create_app()

    
