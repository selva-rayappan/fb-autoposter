# Text post now
curl -X POST "https://graph.facebook.com/$FB_GRAPH_VERSION/$FB_PAGE_ID/feed" \
-F "message=Hello from cURL" \
-F "access_token=$FB_PAGE_TOKEN"


# Schedule text post
curl -X POST "https://graph.facebook.com/$FB_GRAPH_VERSION/$FB_PAGE_ID/feed" \
-F "message=This is scheduled" \
-F "published=false" \
-F "scheduled_publish_time=1763010600" \
-F "access_token=$FB_PAGE_TOKEN"


# Photo by URL
curl -X POST "https://graph.facebook.com/$FB_GRAPH_VERSION/$FB_PAGE_ID/photos" \
-F "caption=Photo via URL" \
-F "url=https://example.com/pic.jpg" \
-F "access_token=$FB_PAGE_TOKEN"