
from flask import Flask, flash, request, redirect, url_for
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename

import sys
sys.path.append('..')

from ai.pr import PR

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'sql'}

class FileHandler(Resource):

    def allowed_file(self, filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def post(self):
        # Get Text type fields
        form = request.form.to_dict()
        print(form)
        print(request.files)

        if 'file' not in request.files:
            return 'No file part'
        
        file = request.files.get("file")
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'File uploaded successfully'
        
    def get(self):
        self.x = PR()
        self.x.process()
        
    def put(self):
        self.x = PR()
        self.x.process()
        self.x.predict()