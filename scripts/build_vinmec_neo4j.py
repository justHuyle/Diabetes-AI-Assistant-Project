import os
import sys
import json
from pathlib import Path

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def populate_neo4j(uri="bolt://localhost:7687", user="neo4j", password=None):
    if not password:
        password = os.getenv("NEO4J_PASSWORD", "matkhau123")
        
    try:
        from neo4j import GraphDatabase
    except ImportError:
        print("[!] Thư viện neo4j chưa được cài đặt. Chạy: pip install neo4j")
        return False
        
    print(f"[*] Đang kết nối tới Neo4j tại: {uri} (User: {user})...")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            # Kiểm tra kết nối
            res = session.run("RETURN 1 AS test").single()
            if not res or res["test"] != 1:
                print("[!] Kết nối không thành công.")
                return False
            print("[+] Kết nối Neo4j thành công!")
            
            print("[*] Đang khởi tạo Schema và Nodes tri thức y khoa từ Vinmec...")
            
            # 1. Bệnh trung tâm
            session.run("""
                MERGE (b:Benh {name: 'Đái tháo đường (Diabetes Mellitus)', icd10: 'E11'})
                SET b.description = 'Rối loạn chuyển hóa đường huyết mạn tính'
            """)
            
            # 2. Thuốc & Tác dụng phụ
            meds = [
                {
                    "name": "Mixtard 30",
                    "type": "Insulin hỗn hợp (30% nhanh, 70% bán chậm)",
                    "side_effects": ["Hạ đường huyết (Hypoglycemia)", "Loạn dưỡng mỡ (Lipodystrophy)", "Phù nề dị ứng"],
                    "source": "Uses and side effects of Mixtard 30"
                },
                {
                    "name": "Metformin",
                    "type": "Biguanide - Giảm sản xuất glucose ở gan",
                    "side_effects": ["Rối loạn tiêu hóa", "Nguy cơ toan chuyển hóa axit lactic", "Tương tác với bưởi chùm"],
                    "source": "Can you eat grapefruit while taking metformin for diabetes"
                }
            ]
            for m in meds:
                session.run("""
                    MATCH (b:Benh {icd10: 'E11'})
                    MERGE (th:Thuoc {name: $name})
                    SET th.type = $type, th.source = $source
                    MERGE (b)-[:DIEU_TRI_BANG]->(th)
                    WITH th
                    UNWIND $side_effects AS se
                    MERGE (td:TacDungPhu {name: se})
                    MERGE (th)-[:CO_TAC_DUNG_PHU]->(td)
                """, name=m["name"], type=m["type"], side_effects=m["side_effects"], source=m["source"])
                
            # 3. Dinh dưỡng & Thực phẩm (Nên ăn / Hạn chế)
            foods = [
                {"name": "Táo tây (Apples)", "category": "Trái cây", "khuyen_nghi": "Nên ăn", "note": "Chỉ số GI thấp, giàu polyphenol chống oxy hóa"},
                {"name": "Bơ (Avocados)", "category": "Trái cây", "khuyen_nghi": "Nên ăn", "note": "Giàu chất béo không bão hòa đơn, ít đường"},
                {"name": "Đậu phộng / Lạc (Peanuts)", "category": "Hạt", "khuyen_nghi": "Nên ăn có kiểm soát", "note": "Giàu protein và chất béo tốt, hỗ trợ ổn định đường huyết"},
                {"name": "Cà tím (Eggplant)", "category": "Rau củ", "khuyen_nghi": "Nên ăn", "note": "Ít calo, nhiều chất xơ, hỗ trợ giảm béo phì"},
                {"name": "Ngô luộc (Boiled corn)", "category": "Ngũ cốc", "khuyen_nghi": "Ăn hạn chế / vừa phải", "note": "Chứa carb nhưng có chất chống oxy hóa, cần tính vào khẩu phần tinh bột"},
                {"name": "Nước dừa (Coconut water)", "category": "Đồ uống", "khuyen_nghi": "Uống có kiểm soát", "note": "Chứa điện giải, không thêm đường, tránh uống quá nhiều một lúc"}
            ]
            for f in foods:
                session.run("""
                    MATCH (b:Benh {icd10: 'E11'})
                    MERGE (tp:ThucPham {name: $name})
                    SET tp.category = $category, tp.khuyen_nghi = $khuyen_nghi, tp.note = $note
                    MERGE (b)-[:CHE_DO_DINH_DUONG]->(tp)
                """, name=f["name"], category=f["category"], khuyen_nghi=f["khuyen_nghi"], note=f["note"])
                
            # 4. Biến chứng y khoa
            complications = [
                {"name": "Ngứa & Tê bì tay chân", "mechanism": "Tổn thương thần kinh ngoại biên do tăng đường huyết mạn"},
                {"name": "Phù chân người cao tuổi", "mechanism": "Suy tim, suy thận hoặc suy giãn tĩnh mạch liên quan mạch máu đái tháo đường"},
                {"name": "Gai đen vùng nách (Acanthosis Nigricans)", "mechanism": "Dấu hiệu lâm sàng của tình trạng kháng insulin nặng"},
                {"name": "Hạ đường huyết cấp tính", "mechanism": "Nguy hiểm ở người già khi dùng quá liều thuốc hoặc bỏ bữa"},
                {"name": "Nhồi máu não (Đột quỵ)", "mechanism": "Xơ vữa động mạch và tổn thương mạch máu não ở bệnh nhân tiểu đường"}
            ]
            for c in complications:
                session.run("""
                    MATCH (b:Benh {icd10: 'E11'})
                    MERGE (bc:BienChung {name: $name})
                    SET bc.mechanism = $mechanism
                    MERGE (b)-[:CO_BIEN_CHUNG]->(bc)
                """, name=c["name"], mechanism=c["mechanism"])
                
            # Đếm số lượng
            cnt = session.run("""
                MATCH (n)
                RETURN count(n) AS total_nodes
            """).single()["total_nodes"]
            
            print(f"[THÀNH CÔNG] Đã nạp thành công Đồ thị tri thức Vinmec vào Neo4j! Tổng cộng: {cnt} nút.")
            return True
    except Exception as e:
        print(f"[!] Lỗi khi nạp vào Neo4j: {e}")
        return False

if __name__ == "__main__":
    pwd = sys.argv[1] if len(sys.argv) > 1 else None
    populate_neo4j(password=pwd)
