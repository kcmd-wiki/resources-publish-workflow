import os

post_id = os.environ.get("POST_ID")
content = os.environ.get("POST_CONTENT")
if not post_id or not content:
    print("Error: Missing environment variables.")
    exit()

# os.makedirs("posts", exist_ok=True)

with open(f"post_{post_id}.md", "w", encoding="utf-8") as f:
    f.write(content)

