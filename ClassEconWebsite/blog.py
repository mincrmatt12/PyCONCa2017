## Blog container. Requires row_factory = sqlite3.Row

## Also requires the valid schema. see docs for detailzies

import urllib, html_utils, user2

class Blog:
    def __init__(self, db, dbc, ucontrol):
        self.db = db
        self.dbc = dbc
        self.users = ucontrol
    
    def post_count(self):
        phrase = "SELECT * FROM Counts WHERE Type=1 LIMIT 1"
        self.db.execute(phrase)
        row = self.db.fetchone()
        return int(row["Count"])
    
    def post_view_count(self):
        phrase = "SELECT * FROM Counts WHERE Type=2 LIMIT 1"
        self.db.execute(phrase)
        row = self.db.fetchone()
        return int(row["Count"])
    
    def show_post(self, pid):
        return not "deleted" in self.post_data(pid)["Tags"].split(";")
    
    def format_post(self, post_data, uid):
        # <div class="panel panel-default">
        #     <div class="panel-heading">
        #         <h4 class="text-center">PostTitleHere</h4>
        #         <p class="text-left">by TestAuthor <span class="label label-primary">Project Announcment</span></p>
        #     </div>
        #     <div class="panel-body">
        #         <p>Test body.</p>
        #     </div>
        # </div>
        
        template = """
        
        <div class="panel panel-default" class="ablogpost">
            <div class="panel-heading">
                <h4 class="text-center">{}</h4>
                {}
                
                <p class="text-left">by <img class="icon-user-mini img-circle" src="/user_icon/{}"> {} {}</p>

            </div>
            <div class="panel-body">
                <div >{}</div>
            </div>
            <div class="panel-footer">
                <div class="btn-group">
                    <button class="btn btn-default" type="button" onclick="location.href='{}'">Goto post page</button>
                    
                </div>
                <button class="btn btn-link pull-right" type="button" onclick="scrollToTop()">Back to top</button>
            </div>
        </div>
        
        """
        
        tag_template = '<span class="label label-{}">{}</span>'
        
        tag_colors = {"gray": "default", "red": "danger", "blue": "primary", "green": "success"}
        
        tag_names = {
            "Project": "blue",
            "Important": "red",
            "Auto Generated": "gray"
        }
        
        body = html_utils.split(100, post_data["Body"])
        title = post_data["Title"]
        
        user = post_data["Author"]
        username = user2.format_username(user, self.users)
        
        tags = post_data["Tags"].split(";")
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
        
        url = post_data["URL"]
        
        dotdot = ""
        print uid
        if uid:
            if post_data["Author"] == uid:
                print "test"
                dotdot = """
                
                <div class="dropdown pull-right">
                    <button id="deleteLabel" class="btn btn-link" data-toggle="dropdown"><span class="glyphicon glyphicon-option-vertical"></span></button>
                    <ul class="dropdown-menu">
                        <li><a href="#" data-delete-id="{}"  class="deleteLink">Delete</a></li>
                    </ul>
                </div>
                
                """.format(post_data["ID"])
        return template.format(title, dotdot, user, username, tag_str, body, url)
    
    def delete_post(self, ID):
        t = self.post_data(ID)
        if "deleted" in t["Tags"]:
            return
        else:
            phrase = "UPDATE BlogPosts SET Tags=? WHERE ID=?"
            data = (t["Tags"] + "deleted" if t["Tags"].endswith(";") else t["Tags"] + ";deleted", ID,)
            self.db.execute(phrase, data)
            self.db.execute("UPDATE Counts SET Count = Count - 1 WHERE Type=2")
            self.db.execute("UPDATE BlogPosts SET Organize = Organize - 1 WHERE ID >= ?", (ID,))
            self.dbc.commit()
            
    
    def get_posts(self, offset, count):
        offset = self.post_view_count() + 1 - offset
        phrase = "SELECT * FROM BlogPosts WHERE Organize <= ? ORDER BY `Organize` DESC LIMIT ?"
        data = (offset, count,)
        self.db.execute(phrase, data)
        return self.db.fetchall()
    
    def create_post(self, post_data):
        ## WARN: THIS DOES NOT CHECK SESSION/AUTH TOKENS
        ## INTERNAL API!!!! ***NO AUTH!!!***
        
        title = str( post_data["Title"])
        user = int(post_data["User"])
        url = "/blog/" + str(urllib.quote(str(title).strip(".,!?").replace(" ", "-"), '')) + "-" + str(self.post_count()+1)
        body = str(post_data["Body"])
        tags = str(post_data["Tags"])
        organize = int(self.post_view_count())
        
        data = (title, url, user, body, tags, organize,)
        phrase = "INSERT INTO `BlogPosts`(`Title`,`URL`,`Author`,`Body`,`Tags`,`Organize`) VALUES (?, ?, ?, ?, ?, ?);"
        
        self.db.execute(phrase, data)
        self.dbc.commit()
    
    def postID_from_url(self, url):
        
        url = "/blog/" + urllib.quote(url[6:], '')
        
        phrase = "SELECT * FROM BlogPosts WHERE URL=? LIMIT 1"
        data = (url,)
        
        self.db.execute(phrase, data)
        return int(self.db.fetchone()["ID"])
    
    def post_data(self, ID):
        
        phrase = "SELECT * FROM BlogPosts WHERE ID=? LIMIT 1"
        data = (ID,)
        
        self.db.execute(phrase, data)
        
        db_back = self.db.fetchone()
        return db_back
    
    def perm_delete_post(self, postID):
        
        phrase = "DELETE FROM BlogPosts WHERE ID=?"
        data = (postID,)
        
        self.db.execute(phrase, data)
        self.dbc.commit()
        
    