import urllib, html_utils, time, user2 as user

from flask import request, session, g, redirect, url_for, abort, render_template, flash
from werkzeug import secure_filename

## Encompases the forums

class ForumHandler:
    def __init__(self, db, dbc, ucontrol):
        self.db = db
        self.dbc = dbc
        self.users = ucontrol
        self.nonalphanum = ''.join(c for c in map(chr, range(256)) if not (c.isalnum() or c== " "))
    
    def view_delete_post(self, postid):
        if "token" in session:
            bc = self.users.uid_for_token(session["token"])
            if (bc != -1):
                self.db.execute("SELECT * FROM ForumThreads WHERE ID=?", (postid,))
                thread = self.db.fetchone()
                if (bc != thread["Author"]):
                    abort(403)
                else:
                    self.db.execute("DELETE FROM ForumThreads WHERE ID=?", (postid,))
                    self.dbc.commit()
                    flash("Thread deleted!")
            else:
                flash("You tried to delete a thread that was not yours")
                abort(403)
        else:
            flash("You are not logged in")
            abort(403)
        return ""
    
    def view_edit_post(self, postid):
        if "token" in session:
            bc = self.users.uid_for_token(session["token"])
            if (bc != -1):
                self.db.execute("SELECT * FROM ForumThreads WHERE ID=?", (postid,))
                thread = self.db.fetchone()
                if (bc != thread["Author"]):
                    abort(403)
                else:
                    newtags = request.form['tags']
                    newbody = request.form['body']
                    
                    phrase = "UPDATE ForumThreads SET Tags=?,Body=? WHERE ID=?"
                    data = (newtags,newbody,postid,)
                    
                    self.db.execute(phrase, data)
                    self.dbc.commit()
                    
            else:
                abort(403)
        else:
            abort(403)
        return ""
    
    
    def view_section(self, section):
        user_handle = self.users
        if "token" in session:
            if user_handle.is_token_valid(session["token"]):
                user_handle.revalidate_token(session["token"])
            else:
                del session["token"]
        section_int = section
        return render_template('forum_sect.html', section=self.get_section_data(section)["DisplayName"], section_int=section_int)
    
    def get_thread_count(self, sect):
        phrase = "SELECT * FROM ForumSections WHERE InternalName=?"
        data = (sect,)
        self.db.execute(phrase, data)
        data = self.db.fetchone()
        return data["PostCount"]
    
    def get_section_id(self, sect):
        phrase = "SELECT * FROM ForumSections WHERE InternalName=?"
        data = (sect,)
        self.db.execute(phrase, data)
        data = self.db.fetchone()
        return data["ID"]
    
    def get_section_data(self, sect):
        phrase = "SELECT * FROM ForumSections WHERE InternalName=?"
        data = (sect,)
        self.db.execute(phrase, data)
        data = self.db.fetchone()
        return data
    
    def get_posts(self, sect, page):
        phrase = "SELECT * FROM ForumThreads WHERE Section=? ORDER BY AddedAt DESC LIMIT ?,?"
        data = (self.get_section_id(sect), page * 12, (page + 1) * 12,)
        self.db.execute(phrase, data)
        return self.db.fetchall()
    
    def page_count(self, thread):
        count = get_thread_count(thread)
        pages = count / 9 + int(count % 9 != 0)
        return pages
        
    def get_next_post_id(self):
        phrase = "SELECT * FROM sqlite_sequence WHERE name='ForumThreads'"
        self.db.execute(phrase)
        return self.db.fetchone()["seq"] + 1
        
    def create_thread(self, data):
        phrase = "INSERT INTO ForumThreads(`Title`,`Author`,`PermissionsForUsers`,`Body`,`Tags`,`AddedAt`,`Section`,`URL`) VALUES (?,?,?,?,?,?,?,?)"
        
        title = str(data["Title"])
        author = data["Author"]
        perm = data["Perm"]
        body = data["Body"]
        tags = data["Tags"]
        addedat = int(time.time())
        section = data["Section"] if (type(data["Section"]) == int) else self.get_section_id(data["Section"])
        ust = title.translate(None, self.nonalphanum)
        ust = ust.replace(" ", "-")
        ust = ust.lower()
        ust += "-" + str(self.get_next_post_id())
        url = ust
        
        data = (title,author,perm,body,tags,addedat,section,url,)
        
        self.db.execute(phrase, data)
        self.dbc.commit()
        
    
    def view_create_thread(self):
        if "token" in session:
            bc = self.users.uid_for_token(session["token"])
            if bc == -1:
                abort(403)
            else:
                if self.users.is_auth(bc, user.AUTH_POST_FORUM):
                    
                    title = request.form["title"]
                    print title
                    author = bc
                    perms = request.form["perms"].split(';')
                    perm = 0
                    perm += int('comment' in perms) * 1
                    tags = request.form["tags"]
                    section = request.form["section"]
                    body = request.form["body"]
                    
                    data = {"Title": title, "Author": author, "Perm": perm, "Section": section, "Tags": tags, "Body": body}
                    self.create_thread(data)
                    
                    
                else:
                    abort(403)
        else:
            abort(403)
            
        return ""
        
    def view_show_thread(self, section, thread):
        phrase = "SELECT * FROM ForumThreads WHERE Section=? AND URL=? LIMIT 1"
        data = (self.get_section_id(section), thread,)
        
        bc = -1
        self.db.execute(phrase, data)
        a = self.db.fetchone()
        uname = ""
        if True:
            bc = a["Author"]
            if (bc != -1):
                uname = user.format_username(bc, self.users)
            bc = self.users.uid_for_token(session["token"] if "token" in session else "")
        
        post_data = {}
        post_data["Title"] = a["Title"]
        post_data["ID"] = a["ID"]
        dotdot = ""
        if bc == a["Author"]:
            dotdot = """
                <div class="dropdown pull-right">
                    <button id="deleteLabel" class="btn btn-link" data-toggle="dropdown"><span class="glyphicon glyphicon-option-vertical"></span></button>
                    <ul class="dropdown-menu">
                        <li><a href="#" class="deleteLink">Delete</a></li>
                        <li><a href="#" class="editLink">Edit</a></li>
                    </ul>
                </div>
            """
        post_data["DotDot"] = dotdot
        post_data["Tags"] = a["Tags"]
        author = uname
        tags = " ".join('<span class="label label-default">{}</span>'.format(x) for x in a["Tags"].split(";"))
        post_data["AuthorTags"] = author + " " + tags
        post_data["Body"] = a["Body"]
        post_data["AuthorIcon"] = a["Author"]
        
        return render_template('forum_view.html', post_data=post_data)
        
        
    ## schema to bind: /forums/get_threads/<section>/<int:page>
    def view_get_forums(self, section):
        page = int(section.split('/')[1])
        section = section.split('/')[0]
        posts = self.get_posts(section, page)
        
        post_template = '<a href="{}" class="list-group-item"><table class="table" style="margin-bottom:0px"><thead><td><h3 style="margin-top: 2px; margin-bottom: 2px">{}</h3></td><td class="text-right">by <img class="icon-user-mini img-circle" src="/user_icon/{}"> {} {}</td></thead></table></a>'
        
        data = ""
        for post in posts:
            title = post["Title"]
            author = user.format_username(post["Author"], self.users)
            tags = " ".join('<span class="label label-default">{}</span>'.format(x) for x in post["Tags"].split(";"))
            url = "/forum/view/" + section + "/" + post["URL"]
            data += post_template.format(url, title, post["Author"], author, tags)
        
        return data
    
    
            