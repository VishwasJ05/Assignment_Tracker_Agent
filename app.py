from flask import Flask, request, jsonify
from part1_open_course import CompleteAssignmentScraper

app = Flask(_name_)

# Store credentials in memory (for demo only)
user_credentials = {}

@app.route('/save_credentials', methods=['POST'])
def save_credentials():
    data = request.json
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Missing fields'}), 400
    user_credentials['username'] = username
    user_credentials['password'] = password
    return jsonify({'message': 'Credentials saved successfully'})

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    if not data:
        return jsonify({'error': 'No JSON data received'}), 400
    url = data.get('url')
    username = data.get('username') or user_credentials.get('username')
    password = data.get('password') or user_credentials.get('password')
    if not url or not username or not password:
        return jsonify({'error': 'Missing fields'}), 400
    scraper = CompleteAssignmentScraper()
    assignments = scraper.scrape_assignments(url, username, password)
    return jsonify(assignments)

if _name_ == '_main_':
    app.run(debug=True)