from azure.storage.blob import BlobServiceClient
from flask import flash
import string, random
from werkzeug.utils import secure_filename
from FlaskWebProject import app, db, login

# --- Blob Storage setup ---
blob_conn_str = f"DefaultEndpointsProtocol=https;AccountName={app.config['BLOB_ACCOUNT']};AccountKey={app.config['BLOB_STORAGE_KEY']};EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(blob_conn_str)
container_client = blob_service_client.get_container_client(app.config['BLOB_CONTAINER'])

def id_generator(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

# --- Models ---
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    author = db.Column(db.String(75))
    body = db.Column(db.String(800))
    image_path = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

    def save_changes(self, form, file, userId, new=False):
        self.title = form.title.data
        self.author = form.author.data
        self.body = form.body.data
        self.user_id = userId

        if file:
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1]
            random_filename = id_generator() + '.' + ext

            try:
                # Upload file to Azure Blob
                blob_client = container_client.get_blob_client(random_filename)
                blob_client.upload_blob(file, overwrite=True)

                # Delete old image if exists
                if self.image_path:
                    old_blob_client = container_client.get_blob_client(self.image_path)
                    old_blob_client.delete_blob()

            except Exception as e:
                flash(f"Blob storage error: {str(e)}")

            self.image_path = random_filename

        if new:
            db.session.add(self)
        db.session.commit()
