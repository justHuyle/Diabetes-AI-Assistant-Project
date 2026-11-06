import sys
from neo4j import GraphDatabase

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "12345678"))
with driver.session() as session:
    print("=== DỮ LIỆU ĐANG CÓ TRONG NEO4J DESKTOP CỦA BẠN ===")
    counts = session.run("MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY count DESC")
    for r in counts:
        print(f" - Nhãn :{r['label']} -> {r['count']} nút")
        
    print("\n=== MỘT VÀI MỐI QUAN HỆ TIÊU BIỂU ===")
    rels = session.run("MATCH (a)-[r]->(b) RETURN labels(a)[0] AS from_node, a.name AS from_name, type(r) AS rel, labels(b)[0] AS to_node, b.name AS to_name LIMIT 6")
    for r in rels:
        print(f" -> ({r['from_node']}: {r['from_name']}) -[:{r['rel']}]-> ({r['to_node']}: {r['to_name']})")
