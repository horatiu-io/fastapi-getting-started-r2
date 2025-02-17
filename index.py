import requests
import xml.etree.ElementTree as ET
from fastapi import FastAPI
from fastapi.responses import Response
import re

app = FastAPI()

SITEMAP_URL = "https://genezio.com/sitemap.xml"

def generate_rss():
    try:
        response = requests.get(SITEMAP_URL)
        response.raise_for_status()  
        xml_content = response.content

        root = ET.fromstring(xml_content)
        rss_items = []
        
        for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
            loc = url.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
            
            # 🔹 FILTRĂM DOAR URL-URILE CARE CONȚIN "genezio.com/blog/"
            if "genezio.com/blog/" in loc:
                # 🔹 Extragerea slug-ului: ultima parte a URL-ului fără "/"
                slug_parts = loc.rstrip("/").split("/")
                slug = slug_parts[-1]  # Luăm ultima parte a URL-ului

                # 🔹 Curățăm slug-ul și îl transformăm în Title Case
                clean_title = re.sub(r'[-_]', ' ', slug).strip().title()

                # 🔹 Dacă titlul este prea scurt sau gol, folosim un fallback
                if not clean_title or len(clean_title) < 3:
                    clean_title = "Blog Post"

                rss_items.append(f"""
                    <item>
                        <title>{clean_title}</title>
                        <link>{loc}</link>
                        <guid>{loc}</guid>
                    </item>
                """)

        # Dacă nu avem articole filtrate, generăm un mesaj în RSS
        if not rss_items:
            rss_items.append("<item><title>No Blog Posts Found</title><link>https://genezio.com/blog/</link></item>")

        rss_feed = f"""<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>Genezio Blog</title>
                <link>https://genezio.com/blog/</link>
                <description>Latest blog posts from Genezio</description>
                {''.join(rss_items)}
            </channel>
        </rss>"""

        return rss_feed
    except Exception as e:
        return f"<error>{str(e)}</error>"

@app.get("/feed.xml")
async def get_rss_feed():
    rss_content = generate_rss()
    return Response(content=rss_content, media_type="application/rss+xml")

import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)