from flask import Flask, request, jsonify
import instaloader

app = Flask(__name__)

@app.route('/download_reel', methods=['POST'])
def download_reel():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    L = instaloader.Instaloader()
    shortcode = url.split("/")[-2]

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        L.download_post(post, target="/tmp/reels")
        return jsonify({"message": "Download successful", "file": f"/tmp/reels/{shortcode}.mp4"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500