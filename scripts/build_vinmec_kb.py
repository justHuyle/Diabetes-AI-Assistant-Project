import os
import sys
import json
import shutil
import pickle
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def backup_existing_kb(kb_dir: Path):
    backup_dir = kb_dir.parent / "kb_index_backup_ada"
    if not backup_dir.exists() and kb_dir.exists():
        print(f"[*] Sao lưu KB cũ sang: {backup_dir}")
        shutil.copytree(kb_dir, backup_dir)

def chunk_articles(articles, chunk_size=600, overlap=120):
    chunks = []
    chunk_counter = 1
    
    for art in articles:
        title = art.get("title", "Vinmec Diabetes Article")
        url = art.get("url", "https://www.vinmec.com")
        paragraphs = art.get("paragraphs", [])
        
        # Ghép các đoạn văn bản thành text hoàn chỉnh
        full_text = "\n\n".join(paragraphs) if paragraphs else art.get("content", "")
        
        start = 0
        doc_chunk_idx = 1
        while start < len(full_text):
            end = min(start + chunk_size, len(full_text))
            
            # Nếu đang cắt dở ở giữa từ, tìm khoảng trắng gần nhất
            if end < len(full_text):
                last_space = full_text.rfind(" ", start, end)
                if last_space > start + int(chunk_size * 0.7):
                    end = last_space
                    
            chunk_str = full_text[start:end].strip()
            
            if len(chunk_str) >= 80:  # Loại bỏ đoạn quá ngắn vô nghĩa
                chunks.append({
                    "chunk_id": f"VINMEC_C{chunk_counter:04d}",
                    "doc_id": f"VINMEC_{title[:30].replace(' ', '_').upper()}",
                    "source_file": f"{title} (Vinmec)",
                    "section_or_page": url,
                    "chunk_index": doc_chunk_idx,
                    "config_type": "Config_B_Balanced",
                    "text": chunk_str,
                    "char_length": len(chunk_str),
                    "word_count": len(chunk_str.split())
                })
                chunk_counter += 1
                doc_chunk_idx += 1
                
            if end >= len(full_text):
                break
            start = end - overlap
            
    return chunks

def main():
    print("=== BẮT ĐẦU XÂY DỰNG KNOWLEDGE BASE TỪ VINMEC ===")
    
    data_file = Path("data/vinmec_diabetes_articles.json")
    if not data_file.exists():
        print(f"[!] Không tìm thấy tệp {data_file}. Vui lòng chạy scripts/crawl_vinmec.py trước.")
        sys.exit(1)
        
    with open(data_file, "r", encoding="utf-8") as f:
        articles = json.load(f)
        
    print(f"[+] Đã đọc {len(articles)} bài viết từ Vinmec.")
    vinmec_chunks = chunk_articles(articles)
    print(f"[+] Đã tạo {len(vinmec_chunks)} chunks ngữ nghĩa từ các bài viết.")
    
    kb_dir = Path("models/kb_index")
    backup_existing_kb(kb_dir)
    
    # Đọc thêm 24 chunk ADA gốc (nếu có) để kết hợp thành KB toàn diện
    ada_chunks = []
    old_meta_file = kb_dir / "kb_chunks_metadata.json"
    if old_meta_file.exists():
        try:
            with open(old_meta_file, "r", encoding="utf-8") as f:
                existing_meta = json.load(f)
                ada_chunks = [c for c in existing_meta if not c.get("chunk_id", "").startswith("VINMEC")]
                print(f"[+] Tích hợp thêm {len(ada_chunks)} chunks chuẩn chẩn đoán ADA đã có.")
        except Exception as e:
            print(f"[!] Không thể đọc metadata cũ: {e}")
            
    all_chunks = ada_chunks + vinmec_chunks
    print(f"[+] Tổng số chunks trong Knowledge Base mới: {len(all_chunks)}")
    
    # Vector Embedding
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    print(f"[*] Đang nạp mô hình Embedding ({model_name})...")
    embedder = SentenceTransformer(model_name)
    
    print("[*] Đang mã hóa Vector (Encoding) cho toàn bộ chunks...")
    texts = [c["text"] for c in all_chunks]
    embeddings = embedder.encode(texts, batch_size=32, show_progress_bar=True, convert_to_numpy=True)
    
    # L2 Normalization cho Cosine Similarity
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1e-12
    normalized_embeddings = (embeddings / norms).astype(np.float32)
    
    # Kiểm tra FAISS
    use_faiss = False
    faiss_bytes = None
    try:
        import faiss
        index = faiss.IndexFlatIP(384)
        index.add(normalized_embeddings)
        faiss_bytes = faiss.serialize_index(index)
        use_faiss = True
        print("[+] Khởi tạo FAISS Index thành công!")
    except ImportError:
        print("[*] FAISS không khả dụng, sử dụng NumPy Cosine Similarity fallback.")
        
    # Ghi file pkl index
    payload = {
        "dimension": 384,
        "use_faiss": use_faiss,
        "vectors": normalized_embeddings,
        "metadata": all_chunks
    }
    if faiss_bytes:
        payload["faiss_bytes"] = faiss_bytes
        
    kb_dir.mkdir(parents=True, exist_ok=True)
    with open(kb_dir / "kb_production_index.pkl", "wb") as f:
        pickle.dump(payload, f)
        
    with open(kb_dir / "kb_chunks_metadata.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
        
    config = {
        "kb_name": "Vinmec_ADA_Diabetes_Knowledge_Base",
        "version": "2.0.0",
        "selected_chunk_config": "Config_B_Balanced",
        "chunk_size_chars": 600,
        "chunk_overlap_chars": 120,
        "total_chunks_indexed": len(all_chunks),
        "total_vinmec_chunks": len(vinmec_chunks),
        "total_ada_chunks": len(ada_chunks),
        "embedding_model": model_name,
        "embedding_dimension": 384,
        "similarity_metric": "Cosine Similarity (L2 Normalized)",
        "artifacts": {
            "index_binary": "kb_production_index.pkl",
            "chunks_metadata": "kb_chunks_metadata.json",
            "kb_config": "kb_config.json"
        }
    }
    with open(kb_dir / "kb_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        
    print(f"\n[THÀNH CÔNG] Đã lưu Knowledge Base mới vào: {kb_dir}")
    print(f" - Tổng chunks: {len(all_chunks)}")
    print(f" - Vector embeddings: {normalized_embeddings.shape}")

if __name__ == "__main__":
    main()
