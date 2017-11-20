from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, send_from_directory
from werkzeug import secure_filename

from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime
import json

from itsdangerous import Signer, URLSafeSerializer

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
        
    return update_wrapper(no_cache, view)

def allowcors(view):
    @wraps(view)
    def acors(*args, **kwargs):
        r = make_response(view(*args, **kwargs))
        h = r.headers
        h['Access-Control-Allow-Origin'] = "*"
        h['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET'
        h['Access-Control-Allow-Credentials'] = 'true'
        h['Access-Control-Max-Age'] = "10"
        r.headers = h
        return r
    return update_wrapper(acors, view)
            

import socket, struct, sqlite3, hashlib, atexit, random, json

import threading, os, subprocess, shutil

import blog, user2 as user, forum

def close_database(db, dbc):
    dbc.commit()
    dbc.close()

app = Flask(__name__)



dbc = sqlite3.connect('store/db.db',  check_same_thread=False)
dbc.row_factory = sqlite3.Row
db = dbc.cursor()

user_handle = user.Logins(db, dbc)

blog_inst = blog.Blog(db, dbc, user_handle)

forum = forum.ForumHandler(db, dbc, user_handle)

@app.route("/forum/section/<sect>")
def view_section(sect):
    if "token" in session:
        if user_handle.is_token_valid(session["token"]):
            user_handle.revalidate_token(session["token"])
        else:
            del session["token"]
    return forum.view_section(sect)

@app.route("/forum/get_threads/<path:section>")
def view_get_threads(section):
    if "token" in session:
        if user_handle.is_token_valid(session["token"]):
            user_handle.revalidate_token(session["token"])
        else:
            del session["token"]
    return forum.view_get_forums(section)

@app.route("/forum/view/<path:data>")
def view_view_data(data):
    if "token" in session:
        if user_handle.is_token_valid(session["token"]):
            user_handle.revalidate_token(session["token"])
        else:
            del session["token"]
    a = data.split('/')
    return forum.view_show_thread(a[0], a[1])
    
@app.route("/forum/create_thread", methods=["POST"])
def view_add_post():
    if "token" in session:
        if user_handle.is_token_valid(session["token"]):
            user_handle.revalidate_token(session["token"])
        else:
            del session["token"]
    return forum.view_create_thread()


    


@app.route("/forum/edit/<int:id2>", methods=["POST"])
def view_edit_post(id2):
    if "token" in session:
        if user_handle.is_token_valid(session["token"]):
            user_handle.revalidate_token(session["token"])
        else:
            del session["token"]
    return forum.view_edit_post(id2)

@app.route("/forum/delete/<int:id2>")
def view_delete_post(id2):
    if "token" in session:
        if user_handle.is_token_valid(session["token"]):
            user_handle.revalidate_token(session["token"])
        else:
            del session["token"]
    return forum.view_delete_post(id2)

@app.route("/create_post", methods=["POST"])
def do_post():
    if "token" not in session:
        abort(403)
    else:
        if not user_handle.is_token_valid(session["token"]):
            abort(403)
        else:
            uid = user_handle.tokens[session["token"]]
            if int(user_handle.get_user_data(uid)["AuthLevel"]) & 4 != 4:
                abort(403)
            else:
                post_data = {}
                post_data["Title"] = request.form["title"]
                post_data["Tags"] = request.form["tags"]
                post_data["User"] = uid
                post_data["Body"] = request.form["thepost"]
                blog_inst.create_post(post_data)
    return ""
            

@app.context_processor
def inject_message():
    
    def get_login_message():
        if "token" in session:
            if user_handle.is_token_valid(session["token"]):
                return '<li><p class="navbar-text">Logged in as <a href="/account">' + user_handle.get_user_data(user_handle.tokens[session["token"]])["Username"] + '</a> | <a href="#" id="logoutLink"> Logout </a></p></li>'
            else:
                return '<li><a data-toggle="modal" href="#loginModal" id="loginBtn"><span class="glyphicon glyphicon-log-in"></span> Login</a></li>'
        else:
            return '<li><a data-toggle="modal" href="#loginModal" id="loginBtn"><span class="glyphicon glyphicon-log-in"></span> Login</a></li>'
    
    def get_is_logged_in():
        if "token" in session:
            return "true" if user_handle.is_token_valid(session["token"]) else "false"
        else:
            return "false"
    
    def get_authlevel():
        if "token" in session:
            if user_handle.is_token_valid(session["token"]):
                return str(user_handle.get_user_data(user_handle.tokens[session["token"]])["AuthLevel"])
            else:
                return "undefined"
        return "undefined"
    
    def get_username():
        if "token" in session:
            if user_handle.is_token_valid(session["token"]):
                return "'" + str(user_handle.get_user_data(user_handle.tokens[session["token"]])["Username"]) + "'"
            else:
                return "undefined"
        return "undefined"
    
    def get_fullname():
        if "token" in session:
            if user_handle.is_token_valid(session["token"]):
                return "'" + str(user_handle.get_user_data(user_handle.tokens[session["token"]])["FullName"]) + "'"
            else:
                return "undefined"
        return "undefined"
    
    def get_id():
        if "token" in session:
            if user_handle.is_token_valid(session["token"]):
                return "'" + str(user_handle.get_user_data(user_handle.tokens[session["token"]])["ID"]) + "'"
            else:
                return "undefined"
        return "undefined"
    
    
    
    return dict(get_login_message=get_login_message, get_is_logged_in=get_is_logged_in, get_authlevel=get_authlevel, get_username=get_username, get_fullname=get_fullname, get_id=get_id)



@app.route("/forums")
def view_forums():
    if "token" in session:
        if user_handle.is_token_valid(session["token"]):
            user_handle.revalidate_token(session["token"])
        else:
            del session["token"]
    return render_template('forum_home.html')

@app.route("/logout")
def process_logout():
    if "token" in session:
        del session["token"]
    else:
        return ""
    return ""
        
@app.route("/user_icon/<int:id>")
@nocache
def get_user_icon(id):
    
    if not os.path.exists("private/userimg/" + str(id) + ".png"):
        shutil.copyfile("private/userimg/default.png", "private/userimg/" + str(id) + ".png")
    
    return send_from_directory('private/userimg', str(id) + ".png")

@app.route("/login_go", methods=["POST"])
@allowcors
def process_login():
    try:
    
        user = request.form["user"]
        password = request.form["pass"]
        
        result = user_handle.do_login(user, password)
        
        if result == -1:
            return "false"
        else:
            session["token"] = result
            return "true"
    except Exception, e:
        print str(e)



@app.route('/login_page')
def do_login_page():
    if "token" in session:
        bc = user_handle.uid_for_token(session["token"])
        if (bc != -1):
            return redirect(request.args.get('to'))
    return render_template('login.html')

@app.route("/user/has_service/<service>", methods=["POST"])
@allowcors
def view_has_service(service):
    if "token" in session:
        bc = user_handle.uid_for_token(session["token"])
        if (bc != -1):
            return str(service in user_handle.get_user_data(bc)).lower()
    abort(403)
    return ''

@app.route('/user/get_uid')
@allowcors
def view_get_uid():
    if "token" in session:
        bc = user_handle.uid_for_token(session["token"])
        if (bc != -1):
            return str(bc)
    abort(403)
    return ''

@app.route('/user/add_service/<service>', methods=["POST"])
@allowcors
def view_add_service(service):
    if "token" in session:
        bc = user_handle.uid_for_token(session["token"])
        if (bc != -1):
            user_handle.add_service(bc, service)
            return ''
    abort(403)
    return ''

@app.route("/user/change_username", methods=["POST"])
def view_change_name():
    if "token" in session:
        bc = user_handle.uid_for_token(session["token"])
        if (bc != -1):
            user_handle.change_username(bc, request.form["new"])
            return ""
    abort(403)
    return ""

@app.route('/user/change_icon', methods=["POST"])
def view_change_icon():
    if "token" in session:
        bc = user_handle.uid_for_token(session["token"])
        if (bc != -1):
            file = request.files.keys()[0]
            t = request.files[file]
            os.remove('private/userimg/' + str(bc) + ".png")
            t.save('private/userimg/' + str(bc) + ".png")
            flash("Changed icon!")
            return ""
    flash("Could not change icon.")
    abort(403)
    
    return ""
    
@app.route("/account")
def view_account():
    if "token" in session:
        bc = user_handle.uid_for_token(session["token"])
        if (bc != -1):
            return render_template('user_account_user.html')
    abort(403)
    return ""

@app.route("/blog_delete/<int:id>")
def tag_delete_post(id):
    if "token" in session:
        if user_handle.is_token_valid(session["token"]):
            user_handle.revalidate_token(session["token"])
        else:
            del session["token"]
    post_data = blog_inst.post_data(id)
    if "token" in session:
        if user_handle.uid_for_token(session["token"]) == post_data["Author"]:
            blog_inst.delete_post(id)
            flash("Deleted post!")
            return ""
    flash("Unauthorized to delete post")
    abort(403)


secret_auther = 'y >b./ai,hYM?=f.[hB3pm6:@ozv4UxX;FI'
@app.route('/user/make_create_user_token')
def make_ctu():
    if "token" in session:
        bc = user_handle.uid_for_token(session["token"])
        if (bc != -1):
            if user_handle.is_auth(bc, 64):
                s = URLSafeSerializer(secret_auther)
                return s.dumps(request.args.get('fname') + ';' + request.args.get('email'))
    abort(403)



@app.route('/create_user_front')
def do_make_user():
    
    token = request.args.get('token')
    
    try:
        s = URLSafeSerializer(secret_auther)
        t = s.loads(token).split(';')
        data = {
            'fullname': t[0],
            'email': t[1],
            'token': token
            }
        for i in db.execute("SELECT * FROM Users WHERE FullName=?", (data['fullname'],)):
            abort(403)
    except:
        abort(403)
    
    return render_template('do_make_user.html', data=data)

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

@app.route('/send_account_emails', methods=["POST"])
def do_send_emails():
    def muser(fname, email):
        if "token" in session:
            bc = user_handle.uid_for_token(session["token"])
            if (bc != -1):
                if user_handle.is_auth(bc, 64):
                    s = URLSafeSerializer(secret_auther)
                    return s.dumps(fname + ';' + email)
        abort(403)
    
    indata = json.loads(request.form['data'])
    
    smt = smtplib.SMTP('sc<redacted>om',  587)
    smt.login('account-dj@smcsgrade7.com', 'M<nope>l')
    
    for i in indata['emails']:
        sender = 'account-dj@smcsgrade7.com'
        password = 'M<redacted>l'
        recv = i['email']
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Setup your clasroom website account"
        msg['From'] = sender
        msg['To'] = recv
        
        text = "It seems that your email client dislikes HTML. No worries, simply copy-paste the following link into your browsers address bar to signup: \n\n {}"
        html = """
        
<html>
<head></head>
<body>
<p>
Click the following link to signup for the class website! <br />
<a href="{}">Click me!</a>
</p>
</body>
</html>
        """
        link = 'http://smcsgrade7.com/create_user_front?token=' + muser(i['fname'], i['email'])
        part1 = MIMEText(text.format(link), 'plain')
        part2 = MIMEText(html.format(link), 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        smt.sendmail(sender, [recv], msg.as_string())
    
    smt.close()
    return ''
        

@app.route('/create_account_go', methods=["POST"])
def do_create_user():
    token = request.form["token"]
    u = request.form["username"]
    p = request.form["password"]
    auth=3
    try:
        s = URLSafeSerializer(secret_auther)
        t = s.loads(token).split(';')
        data = {
            'fullname': t[0],
            'email': t[1],
        
        }
        
        user_handle.create_account(u, p.encode('utf-8'), data['fullname'])
        
        return ''
    except:
        pass
    abort(403)
    

@app.route("/blog/<url>")
def view_blogpost(url):
    if "token" in session:
        if user_handle.is_token_valid(session["token"]):
            user_handle.revalidate_token(session["token"])
        else:
            del session["token"]
    post = blog_inst.post_data(blog_inst.postID_from_url("/blog/" + url))
    
    post_title = post["Title"]
    post_author = user.format_username(post["Author"], user_handle)
    tag_template = '<span class="label label-{}">{}</span>'
        
    tag_colors = {"gray": "default", "red": "danger", "blue": "primary", "green": "success"}
    
    tag_names = {
        "Project": "blue",
        "Important": "red",
        "Auto Generated": "gray"
    }
    
    tags = post["Tags"].split(";")
    tag_str = ""
    if tags != ['']:
        for i in tags:
            if i == "deleted":
                continue
            else:
                try:
                    tag_str += tag_template.format(tag_colors[tag_names[i]], i) + " "
                except:
                    tag_str += tag_template.format("primary", i) + " "
    
    post_tags = tag_str
    post_body = post["Body"]
    
    return render_template("blogpost.html", post_title=post_title, post_author=post_author, post_tags=post_tags, post_body=post_body, post_author_id=post["Author"])

@app.route("/account/deleted_blogs")
def view_del_blogs():
    return "Page not ready yet! Check back later"
    

    
apis = {
    
    'ads': '-%t3)zExbRI"f[2x~hgkoE~=G0Sb|@',
    'bank': 'cDDRmxK3\\1}ohRjucPt2}wl\'L#tl1(-/]A.?.6=g6\\I!!^&l_M'
    
}
    
@app.route('/api/sign')
@allowcors
def sign_view():
    if "token" in session:
        bc = user_handle.uid_for_token(session["token"])
        if (bc != -1):
            s = Signer(apis[request.args.get('api')], salt=request.args.get('rand'))
    
            return s.sign(str(bc))
    abort(403)
    return ""

    
    

@app.route("/")
def view_root():
    global user_handle
    if "token" in session:
        if user_handle.is_token_valid(session["token"]):
            user_handle.revalidate_token(session["token"])
        else:
            del session["token"]
    return render_template("home.html")

@app.route("/blog_internal/<int:page>")
def get_blogs(page):
    uid = None
    if "token" in session:
        if user_handle.is_token_valid(session["token"]):
            user_handle.revalidate_token(session["token"])
            print "testy"
            uid = user_handle.tokens[session["token"]]
        else:
            del session["token"]
    
    posts = blog_inst.get_posts(page * 9, 9)
    
    data = ""
    
    for post in posts:
        if blog_inst.show_post(post["ID"]):
            data += blog_inst.format_post(post, uid)
    
    return data

@app.route("/blog_internal_count")
def get_post_count():
    if "token" in session:
        if user_handle.is_token_valid(session["token"]):
            user_handle.revalidate_token(session["token"])
        else:
            del session["token"]
        
    pages = blog_inst.post_view_count() / 9
    if blog_inst.post_count() / 9 < blog_inst.post_view_count():
        pages += 1
    pages -= 1
    if pages == 0 and blog_inst.post_view_count() != 0:
        pages = 1
    return str(pages)


@app.route("/blog_upload", methods=["GET", "POST"])
def upload_blog():
    un = ""
    if "token" in session:
        if user_handle.is_token_valid(session["token"]):
            un = user_handle.get_user_data(user_handle.tokens[session["token"]])["Username"]
        else:
            abort(403)
    else:
        abort(403)
    if request.method == 'POST':
        file = request.files.keys()[0]
        file = request.files[file]
        if file:
            fname = secure_filename(file.filename)
            ext = os.path.splitext(fname)[1]
            fname = "file-uploaded-" + str(random.randint(1000000, 99999999))
            
            file.save(os.path.join("static/img/postdata", fname + "-" + un + ext))
            fname = fname + "-" + un + ext
            return json.dumps({"location": fname})
        return ""
    return ""

## After here is DEBUG CODE

## NOT PRODUCTION!!!
## AFGAFDSADSFADSFDASFAS!!!!
atexit.register(close_database, db, dbc)
app.secret_key = os.urandom(128)

## ADDED FOR PYCON HERE:

user = raw_input("Add user with name: (leave blank to start now) ")
if user is not "":
    password = raw_input("pass: ")
    user_handle.create_account(user, password, "Test Pycon USER", auth=127)

## END ADDED SECTION

app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)), debug=True)
