#!/usr/bin/env python3
import csv
from datetime import datetime

#!/usr/bin/env python3
import json
import requests
from datetime import datetime

class FBPoster:
    def __init__(self, page_id, page_token):
        self.page_id = page_id
        self.page_token = page_token
        self.base_url = f"https://graph.facebook.com/v18.0/{self.page_id}"

    def _post(self, endpoint, data, files=None):
        data["access_token"] = self.page_token
        r = requests.post(f"{self.base_url}/{endpoint}", data=data, files=files)
        r.raise_for_status()
        return r.json()

    # 1) Text/link post
    def create_feed_post(self, message: str, link: str = None, publish_now: bool = True, schedule_time: int | None = None):
        data = {"message": message}
        if link: 
            data["link"] = link
        if not publish_now:
            if not schedule_time:
                raise ValueError("schedule_time (unix) required when publish_now=False")
            data.update({"published": "false", "scheduled_publish_time": str(schedule_time)})
        return self._post("feed", data)

    # 2) Single photo post
    def create_photo_post(self, caption: str, image_url: str = None, image_path: str = None, publish_now: bool = True, schedule_time: int | None = None):
        if not image_url and not image_path:
            raise ValueError("Provide image_url or image_path")
        data = {"caption": caption}
        if not publish_now:
            if not schedule_time:
                raise ValueError("schedule_time (unix) required when publish_now=False")
            data.update({"published": "false", "scheduled_publish_time": str(schedule_time)})
        files = None
        if image_url:
            data["url"] = image_url
        else:
            files = {"source": open(image_path, "rb")}
        return self._post("photos", data, files)

    # 3) Carousel/multi-photo post
    def create_multi_photo_post(self, caption: str, image_urls: list[str]):
        # Upload photos unpublished
        media_ids = []
        for url in image_urls:
            res = self._post("photos", {"url": url, "published": "false"})
            media_ids.append(res["id"])
        # Create a feed post attaching media_fbid[*]
        data = {"message": caption}
        for i, mid in enumerate(media_ids):
            data[f"attached_media[{i}]"] = json.dumps({"media_fbid": mid})
        return self._post("feed", data)


def parse_hhmm_local_to_unix(hhmm: str) -> int:
    # naive local to epoch; assumes server is in same TZ or use pytz if needed
    dt = datetime.strptime(hhmm, "%Y-%m-%d %H:%M")
    return int(dt.timestamp())


# Add your main function here if needed
if __name__ == "__main__":
    # Example usage
    PAGE_ID = "135592356308721"
    PAGE_TOKEN = "EAAKPbrrVH94BP7vRBM4chhPrBy8wtS9Xpta3rI57qZAzh8Qa6dd3i9dHITUw8iaYGK2YdqwKWBap5zrhRuj1gMbENzfnxrbrUQzVixo2EBRVYPgEPmevXjlCuvQ2ZBiqmlqIC1tuZAFGy0ZCrxhkiZAaQvLK8eqmMyMAHIE3YVLpsDtUrBjGyIkcLxqruByJYnAZDZD"
    
    fb = FBPoster(PAGE_ID, PAGE_TOKEN)
    # Test your functions here

def parse_hhmm_local_to_unix(dt_str):
    """Convert 'YYYY-MM-DD HH:MM' string to Unix timestamp"""
    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    return int(dt.timestamp())


def main():
    import argparse

    p = argparse.ArgumentParser(description="FB Page auto poster")
    p.add_argument("--mode", choices=["text", "photo", "multi", "csv"], required=True)
    p.add_argument("--message", help="Post message")
    p.add_argument("--link", help="Optional link")
    p.add_argument("--image", help="Image path or URL")
    p.add_argument("--images", nargs="*", help="List of image URLs for carousel")
    p.add_argument("--schedule", help="Schedule in 'YYYY-MM-DD HH:MM' (local)")
    p.add_argument("--csv", dest="csv_path", help="CSV file with posts queue")
    args = p.parse_args()

    # Assuming FBPoster and PAGE_ID, PAGE_TOKEN are defined elsewhere
    fb = FBPoster(PAGE_ID, PAGE_TOKEN)
    schedule_unix = None
    publish_now = True

    if args.schedule:
        schedule_unix = parse_hhmm_local_to_unix(args.schedule)
        publish_now = False

    if args.mode == "text":
        print(
            fb.create_feed_post(
                args.message or "", args.link, publish_now, schedule_unix
            )
        )

    elif args.mode == "photo":
        print(
            fb.create_photo_post(
                args.message or "",
                image_url=args.image
                if (args.image and args.image.startswith("http"))
                else None,
                image_path=None
                if (args.image and args.image.startswith("http"))
                else args.image,
                publish_now=publish_now,
                schedule_time=schedule_unix,
            )
        )

    elif args.mode == "multi":
        print(fb.create_multi_photo_post(args.message or "", args.images or []))

    elif args.mode == "csv":
        if not args.csv_path:
            raise SystemExit("--csv is required")

        with open(args.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                mode = row.get("mode", "text")
                msg = row.get("message", "")
                link = row.get("link") or None
                when = row.get("schedule") or None
                publish_now = True
                schedule_unix = None

                if when:
                    schedule_unix = parse_hhmm_local_to_unix(when)
                    publish_now = False

                if mode == "text":
                    res = fb.create_feed_post(msg, link, publish_now, schedule_unix)
                elif mode == "photo":
                    res = fb.create_photo_post(
                        msg,
                        image_url=row.get("image_url"),
                        image_path=row.get("image_path"),
                        publish_now=publish_now,
                        schedule_time=schedule_unix,
                    )
                elif mode == "multi":
                    imgs = [
                        x.strip()
                        for x in (row.get("images") or "").split("|")
                        if x.strip()
                    ]
                    res = fb.create_multi_photo_post(msg, imgs)
                else:
                    raise ValueError(f"Unknown mode {mode}")
                print("OK:", res)


if __name__ == "__main__":
    main()
