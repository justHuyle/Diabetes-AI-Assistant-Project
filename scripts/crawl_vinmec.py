import sys
import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_URL = "https://www.vinmec.com"
TAG_URL = "https://www.vinmec.com/eng/tag/diabetes-58f4f3fb"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_all_article_links():
    article_links = set()
    for p in range(1, 4):
        page_url = TAG_URL if p == 1 else f"{TAG_URL}/page_{p}"
        print(f"[*] Đang quét danh sách link trang {p}: {page_url}")
        res = requests.get(page_url, headers=HEADERS, timeout=15)
        if res.status_code != 200:
            print(f"[!] Lỗi tải trang {page_url}: Status {res.status_code}")
            continue
        soup = BeautifulSoup(res.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/eng/blog/" in href and "policy" not in href:
                full_url = BASE_URL + href if href.startswith("/") else href
                article_links.add(full_url)
        time.sleep(1)
    return sorted(list(article_links))

def crawl_article_content(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=15)
        if res.status_code != 200:
            print(f"[!] Lỗi tải bài viết: {url} (Status {res.status_code})")
            return None
        soup = BeautifulSoup(res.text, "html.parser")
        
        # Tiêu đề bài viết
        title_tag = soup.find("h1")
        title = title_tag.text.strip() if title_tag else "No Title"
        
        # Nội dung chính nằm trong div.post-detail
        content_div = soup.find("div", class_="post-detail")
        if not content_div:
            return None
            
        # Xóa các thẻ script, style thừa
        for s in content_div(["script", "style"]):
            s.decompose()
            
        paragraphs = [p.text.strip() for p in content_div.find_all(["p", "h2", "h3", "li"]) if p.text.strip()]
        full_text = "\n\n".join(paragraphs)
        
        return {
            "title": title,
            "url": url,
            "content": full_text,
            "paragraphs": paragraphs
        }
    except Exception as e:
        print(f"[!] Lỗi khi cào {url}: {e}")
        return None

def main():
    print("=== BẮT ĐẦU CÀO DỮ LIỆU TỪ VINMEC (TAG DIABETES) ===")
    links = get_all_article_links()
    print(f"[+] Tìm thấy tổng cộng {len(links)} bài viết độc nhất.")
    
    articles = []
    for idx, link in enumerate(links, 1):
        print(f"[{idx}/{len(links)}] Đang cào: {link}")
        data = crawl_article_content(link)
        if data:
            articles.append(data)
        time.sleep(0.5)
        
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "vinmec_diabetes_articles.json"
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"\n[DONE] Đã lưu thành công {len(articles)} bài viết vào: {out_file}")

if __name__ == "__main__":
    main()
