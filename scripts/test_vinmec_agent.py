import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.agents.knowledge_agent import KnowledgeAgent

def test_queries():
    print("=== KIỂM THỬ KNOWLEDGE AGENT VỚI VINMEC KB ===")
    agent = KnowledgeAgent()
    
    test_questions = [
        "Người bị tiểu đường có ăn được ngô luộc không?",
        "Tác dụng phụ của thuốc Mixtard 30 trong điều trị đái tháo đường là gì?",
        "Chỉ số đường huyết 2 giờ sau ăn bao nhiêu là bình thường?"
    ]
    
    for q in test_questions:
        print(f"\n" + "="*70)
        print(f"CÂU HỎI: {q}")
        print("="*70)
        res = agent.run({"query": q, "top_k": 2})
        print("KẾT QUẢ TỪ AGENT:")
        if isinstance(res.content, dict):
            print("Answer:", res.content.get("answer") or res.content.get("message"))
        else:
            print(res.content)
            
        print("\nTOP CÁC ĐOẠN ĐƯỢC RETRIEVE:")
        chunks = res.trace.get("retrieved_chunks", [])
        for c in chunks:
            print(f" -> Nguồn: {c.get('source_file')} | Độ tương đồng: {c.get('similarity_score', 0):.4f}")
            print(f"    URL: {c.get('section_or_page')}")
            print(f"    Trích đoạn: {c.get('text')[:180]}...\n")

if __name__ == "__main__":
    test_queries()
