import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


# Nějáké poznámky jsou od gpt, jelikož jsem neměl tušení co to dělá a code mi bez toho ve výsledku nefungoval nebo stránka házela error
# Workzeug mi prozatím generuje password hash a zajišťuje, že hesla nejsou uloženy v čitelné podobě, ale ve formě, která je bezpečná i v případě uníku databáze
# Pořád nechápu jak má fungovat nahráni obrázků "avatarů" (https://www.youtube.com/watch?v=I9BBGulrOmo - později zkusím podle toho)
# Později propojit settings, questy, levels a leaderboards app route
# Addnout soundbar pro level-up později

app = Flask(__name__)  # Inicializace Flasku
app.secret_key = 'tajny_klic'  # Tajný klíč pro šifrování session
app.config['UPLOAD_FOLDER'] = 'static/avatars/'  # složka pro uložení avatarů

# Ujistí se jestli slozka pro ulozeni "avataru" existuje
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])  # vytvoření složky pokud neexistuje

# Dočasná databáze uživatelů (Později napojím na SQLite)
users_db = {}  # Bude mít informace o uživatelích jako heslo, exp, level, přezdívku atd.

@app.route('/')
def index():
    # Přesměrování na login stránku jako výchozí
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Funkce pro registraci uživatelů
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return 'Musíš zadat uživatelské jméno a heslo!'  # Ošetření prázdného vstupu

        if username in users_db:
            return 'Uživatelské jméno již existuje!'  # Kontrola, zda uživatel již existuje

        hashed_password = generate_password_hash(password)  # Hashování hesla
        users_db[username] = {
            'password': hashed_password,
            'exp': 0,
            'level': 0,
            'nickname': '',
            'about': '',
            'avatar': ''  
        }

        return redirect(url_for('login'))  # Přesměrování na login po registraci

    return render_template('register.html')  # Zobrazení registrační stránky

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Funkce pro přihlášení uživatele
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return 'Musíš zadat uživatelské jméno a heslo!'  # Ošetření prázdného vstupu

        user = users_db.get(username)  # Vyhledání uživatele v databázi (Dodělám soon)

        if user and check_password_hash(user['password'], password):
            session['username'] = username  # Uložení uživatelského jména do session
            # Kontrola jestli jde o první přihlášení (level 0)
            if user['level'] == 0:
                return redirect(url_for('qualification'))  # Přesměrování na stránku qualification

            return redirect(url_for('home'))  # Přesměrování na home po přihlášení
        else:
            return 'Špatné uživatelské jméno nebo heslo!'  # Špatny login

    return render_template('login.html')  # Zobrazení přihlašovací stránky

@app.route('/qualification')
def qualification():
    # Stránka s otazkou (Byl jsi kvalifikován jako hrac blablabla solo leveling reference) po prvním loginu
    return render_template('qualification.html')

@app.route('/home')
def home():
    # Home stránka uživatele
    if 'username' in session:
        user = users_db.get(session['username'])  # Získání informací o uživateli ze session
        return render_template('home.html', username=user['nickname'], exp=user['exp'], level=user['level'], avatar=user['avatar'])
    else:
        return redirect(url_for('login'))  # Přesměrování na login stránku, pokud uživatel není přihlášen

@app.route('/ucet', methods=['GET', 'POST'])
def ucet():
    # Stránka účtů s možností úprav
    if 'username' in session:
        username = session['username']
        user = users_db.get(username)

        if request.method == 'POST':
            nickname = request.form.get('nickname')
            about = request.form.get('about')

            if nickname:
                user['nickname'] = nickname  # Uložení "nové přezdívky"
            if about:
                user['about'] = about  # Uložení nového "o mně"

        return render_template('ucet.html', nickname=user['nickname'], about=user['about'], level=user['level'], exp=user['exp'], avatar=user['avatar'])
    else:
        return redirect(url_for('login'))  # Přesměrování na login, pokud uživatel není přihlášen

@app.route('/upravit_ucet', methods=['GET', 'POST'])
def upravit_ucet():
    # Stránka pro úpravu účtu uživatele
    if 'username' in session:
        username = session['username']
        user = users_db.get(username)

        if request.method == 'POST':
            nickname = request.form.get('nickname')
            about = request.form.get('about')
            avatar = request.files.get('avatar')

            if nickname:
                user['nickname'] = nickname  
            if about:
                user['about'] = about 

            # Zpracovani nahrání obraázku
            if avatar:
                avatar_filename = secure_filename(avatar.filename)  # Bezpečné uložení souboru
                avatar.save(os.path.join(app.config['UPLOAD_FOLDER'], avatar_filename))  # Uložení souboru do složky
                user['avatar'] = avatar_filename  # Uložení názvu souboru do databáze

            flash('Úspěšně upraveno.', 'success')  # Zobrazení že to bylo upraveno
            return redirect(url_for('ucet'))  # Redirect zpět na účet po uložení

        return render_template('upravitucet.html', nickname=user['nickname'], about=user['about'], level=user['level'], exp=user['exp'], avatar=user['avatar'])
    else:
        return redirect(url_for('login'))  # Redirect na login, pokud uživatel není přihlášen

@app.route('/logout')
def logout():
    # Funkce pro logout uživatele
    session.pop('username', None)  # Vymazání acc údajů ze session
    return redirect(url_for('login'))  # Přesměrování na přihlašovací stránku

if __name__ == '__main__':
    app.run(debug=True)  #  run aplikace v debug módu (myslím že to zobrazuje konkrétní errory pokud se stránka nenačte) 
