import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os

# Download necessary NLTK data files
nltk.download('punkt')
nltk.download('stopwords')




app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Ensure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Read the content of the text file
            with open(filepath, 'r') as f:
                content = f.read()
                
            return render_template('index.html', text_content=content)
    
    return render_template('index.html')


@app.route('/summarize', methods=['POST'])
def summarize():
    text_content = request.form['text_content']
    sentences = sent_tokenize(text_content)
    
    # Tokenize the text into words and convert to lowercase
    words = word_tokenize(text_content.lower())
    
    # Remove punctuation and non-alphanumeric characters
    words = [word for word in words if word.isalnum()]
    
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]
    
    # Compute word frequencies
    word_freq = Counter(words)
    
    # Score sentences based on word frequencies
    sentence_scores = {}
    for sentence in sentences:
        sentence_words = word_tokenize(sentence.lower())
        sentence_words = [word for word in sentence_words if word.isalnum()]
        sentence_words = [word for word in sentence_words if word not in stop_words]
        
        if len(sentence_words) == 0:
            continue
        
        score = sum(word_freq.get(word, 0) for word in sentence_words)
        sentence_scores[sentence] = score
    
    num_sentences = 5
    # Get the top N sentences
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    summary = ' '.join(top_sentences)
    

    return render_template('portfolio-details.html', summary=summary)

if __name__ == '__main__':
    app.run(debug=True)
