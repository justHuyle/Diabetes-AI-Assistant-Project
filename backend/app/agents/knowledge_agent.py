import time
import os
from typing import Any, Dict, List, Optional

from backend.app.agents.base import BaseAgent, AgentResponse
from backend.app.core.config import settings
from backend.app.core.loaders import KnowledgeBaseArtifacts, load_knowledge_base


class Neo4jGraphRetriever:
    """Truy xuất tri thức đồ thị (Graph RAG) từ cơ sở dữ liệu Neo4j."""

    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self._driver = None
        self._is_available = None

    def _get_driver(self):
        if self._driver is None and self._is_available is not False:
            try:
                from neo4j import GraphDatabase
                self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
                with self._driver.session() as s:
                    s.run("RETURN 1").single()
                self._is_available = True
            except Exception:
                self._is_available = False
                self._driver = None
        return self._driver

    def search_graph(self, query: str) -> List[Dict[str, Any]]:
        """Tìm các nút và quan hệ thực thể tương ứng với câu hỏi trong Neo4j."""
        driver = self._get_driver()
        if not driver:
            return []

        facts = []
        q_lower = query.lower()
        try:
            with driver.session() as s:
                # 1. Tìm thực phẩm & chế độ ăn
                res_tp = s.run("""
                    MATCH (b:Benh)-[:CHE_DO_DINH_DUONG]->(tp:ThucPham)
                    RETURN tp.name AS name, tp.category AS category, tp.khuyen_nghi AS khuyen_nghi, tp.note AS note
                """)
                for r in res_tp:
                    name_clean = r["name"].lower().replace("(", " ").replace(")", " ").replace("/", " ")
                    words = [w for w in name_clean.split() if len(w) > 2]
                    if any(w in q_lower for w in words):
                        facts.append({
                            "type": "Thực phẩm",
                            "entity": r["name"],
                            "relationship": "CHE_DO_DINH_DUONG",
                            "fact": f"Thực phẩm: {r['name']} ({r['category']}) | Khuyến nghị: {r['khuyen_nghi']} | Lưu ý: {r['note']}"
                        })

                # 2. Tìm thuốc điều trị & tác dụng phụ
                res_th = s.run("""
                    MATCH (b:Benh)-[:DIEU_TRI_BANG]->(th:Thuoc)
                    OPTIONAL MATCH (th)-[:CO_TAC_DUNG_PHU]->(tdp:TacDungPhu)
                    RETURN th.name AS name, th.type AS type, collect(DISTINCT tdp.name) AS side_effects
                """)
                for r in res_th:
                    name_clean = r["name"].lower()
                    words = [w for w in name_clean.split() if len(w) > 2]
                    if any(w in q_lower for w in words):
                        se = ", ".join(r["side_effects"]) if r["side_effects"] else "Không ghi nhận"
                        facts.append({
                            "type": "Thuốc",
                            "entity": r["name"],
                            "relationship": "DIEU_TRI_BANG",
                            "fact": f"Thuốc: {r['name']} (Nhóm: {r['type']}) | Tác dụng phụ trên đồ thị: {se}"
                        })

                # 3. Tìm biến chứng bệnh đái tháo đường
                res_bc = s.run("""
                    MATCH (b:Benh)-[:CO_BIEN_CHUNG]->(bc:BienChung)
                    RETURN bc.name AS name, bc.mechanism AS mechanism
                """)
                for r in res_bc:
                    name_clean = r["name"].lower().replace("&", " ")
                    words = [w for w in name_clean.split() if len(w) > 2]
                    if any(w in q_lower for w in words):
                        facts.append({
                            "type": "Biến chứng",
                            "entity": r["name"],
                            "relationship": "CO_BIEN_CHUNG",
                            "fact": f"Biến chứng: {r['name']} | Cơ chế/Nguyên nhân: {r['mechanism']}"
                        })
        except Exception:
            pass
        return facts


class KnowledgeAgent(BaseAgent):
    """Agent Tri thức (KB + Hybrid RAG: Vector + Neo4j Graph) truy xuất hướng dẫn y tế chuẩn mực và giải đáp có dẫn nguồn."""

    def __init__(self, artifacts: Optional[KnowledgeBaseArtifacts] = None, similarity_threshold: float = 0.35):
        super().__init__(name="KnowledgeAgent")
        self.artifacts = artifacts or load_knowledge_base()
        self.similarity_threshold = similarity_threshold
        self.api_key = settings.GEMINI_API_KEY
        self.graph_retriever = Neo4jGraphRetriever(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD
        )

    def _call_gemini(self, query: str, chunks: List[dict], graph_facts: Optional[List[dict]] = None) -> Optional[str]:
        """Gọi Gemini API để tổng hợp câu trả lời neo chặt vào tài liệu nguồn và đồ thị tri thức Neo4j."""
        if not self.api_key:
            return None
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=self.api_key, http_options=types.HttpOptions(timeout=10000))

            context_snippets = []
            for idx, c in enumerate(chunks, start=1):
                context_snippets.append(
                    f"--- Đoạn {idx} [Nguồn: {c['source_file']}, {c['section_or_page']}] ---\n{c['text']}"
                )
            context_text = "\n\n".join(context_snippets)

            if graph_facts:
                graph_lines = [f"- [Đồ thị Neo4j] {g['fact']}" for g in graph_facts]
                context_text += "\n\n--- DỮ LIỆU ĐỒ THỊ TRI THỨC Y KHOA (NEO4J GRAPH) ---\n" + "\n".join(graph_lines)

            system_instruction = (
                "Bạn là trợ lý y khoa AI tư vấn về đái tháo đường cho người bệnh. "
                "NGUYÊN TẮC BẤT BIẾN: "
                "1. Chỉ trả lời dựa trên các đoạn văn bản nguồn và đồ thị tri thức Neo4j được cung cấp dưới đây. "
                "2. Tuyệt đối không kê đơn thuốc cụ thể hoặc chỉnh liều insulin. "
                "3. Bắt buộc ghi rõ trích dẫn nguồn ở cuối câu trả lời theo định dạng: [Nguồn: <tên tệp/bài viết>, <mục/đồ thị>]. "
                "4. Nếu thông tin không có trong tài liệu hoặc đồ thị, thông báo rõ ràng là tài liệu chưa đề cập."
            )

            prompt = f"{system_instruction}\n\nTÀI LIỆU NGUỒN & ĐỒ THỊ:\n{context_text}\n\nCÂU HỎI:\n{query}"

            models_to_try = ["gemini-3.5-flash-lite", "gemini-flash-lite-latest"]
            for model_id in models_to_try:
                try:
                    resp = client.models.generate_content(
                        model=model_id,
                        contents=prompt
                    )
                    if resp:
                        text_val = ""
                        if hasattr(resp, "text") and resp.text:
                            text_val = resp.text.strip()
                        elif hasattr(resp, "candidates") and resp.candidates:
                            for cand in resp.candidates:
                                if hasattr(cand, "content") and cand.content.parts:
                                    for part in cand.content.parts:
                                        if hasattr(part, "text") and part.text:
                                            text_val += part.text
                        if text_val:
                            return text_val.strip()
                except Exception:
                    continue
            return None
        except Exception:
            # Fallback sang chế độ extractive nếu lỗi kết nối mạng hoặc sai khóa API
            return None

    def _call_gemini_conversational(self, query: str) -> Optional[str]:
        """Gọi Gemini API để trò chuyện tự nhiên, lịch sự và hướng dẫn người dùng về bệnh đái tháo đường."""
        if not self.api_key:
            return None
        try:
            from google import genai
            from google.genai import types
            client = genai.Client(api_key=self.api_key, http_options=types.HttpOptions(timeout=10000))

            system_instruction = (
                "Bạn là Trợ lý AI y tế thông minh chuyên sâu về bệnh Đái tháo đường (Hệ thống Hội chẩn Đa Tác Tử - PTIT). "
                "Người dùng đang đặt câu hỏi xã giao hoặc câu hỏi nằm ngoài phạm vi tài liệu chuyên môn về đái tháo đường. "
                "HƯỚNG DẪN TRẢ LỜI: "
                "1. Chào hỏi và phản hồi câu hỏi của người dùng một cách tự nhiên, lịch sự, thân thiện và súc tích (1-3 câu). "
                "2. Sau đó, khéo léo giới thiệu rằng chuyên môn chính của bạn là hỗ trợ tư vấn chỉ số đường huyết, chế độ dinh dưỡng, vận động khoa học và đánh giá nguy cơ đái tháo đường theo chuẩn Bộ Y tế & ADA. "
                "3. Hướng dẫn người dùng có thể nhập các chỉ số xét nghiệm ở cột bên trái hoặc đặt các câu hỏi về tiểu đường để được hỗ trợ chuyên sâu."
            )

            prompt = f"{system_instruction}\n\nCÂU HỎI NGƯỜI DÙNG: {query}"

            models_to_try = ["gemini-3.5-flash-lite", "gemini-flash-lite-latest"]
            for model_id in models_to_try:
                try:
                    resp = client.models.generate_content(
                        model=model_id,
                        contents=prompt
                    )
                    if resp:
                        text_val = ""
                        if hasattr(resp, "text") and resp.text:
                            text_val = resp.text.strip()
                        elif hasattr(resp, "candidates") and resp.candidates:
                            for cand in resp.candidates:
                                if hasattr(cand, "content") and cand.content.parts:
                                    for part in cand.content.parts:
                                        if hasattr(part, "text") and part.text:
                                            text_val += part.text
                        if text_val:
                            return text_val.strip()
                except Exception:
                    continue
            return None
        except Exception:
            return None

    def _format_extractive_answer(self, chunks: List[dict], graph_facts: Optional[List[dict]] = None) -> str:
        """Định dạng câu trả lời trích xuất nguyên văn khi không có API key."""
        lines = [
            "Hệ thống đang hoạt động ở chế độ Trích xuất nguyên văn (Extractive Mode) từ Cơ sở tri thức chuẩn mực:",
            ""
        ]
        if graph_facts:
            lines.append("🌐 **Tri thức từ Đồ thị Neo4j (GraphRAG):**")
            for gf in graph_facts:
                lines.append(f"- {gf['fact']}")
            lines.append("")

        lines.append("📄 **Trích đoạn tài liệu liên quan:**")
        for idx, c in enumerate(chunks, start=1):
            lines.append(f"📌 **Trích dẫn {idx}** [Nguồn: `{c['source_file']}` | {c['section_or_page']}]:")
            lines.append(f"> \"{c['text']}\"")
            lines.append(f"*(Độ tương đồng ngữ nghĩa: {c['similarity_score']:.4f})*\n")
        return "\n".join(lines)

    def run(self, request: Dict[str, Any]) -> AgentResponse:
        start_time = time.perf_counter()
        query = str(request.get("query", "")).strip()

        # 1. Kiểm tra câu hỏi đầu vào
        if not query:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            return AgentResponse(
                agent=self.name,
                content={"error": "Câu hỏi truy vấn y khoa (query) không được để trống."},
                confidence=0.0,
                flags=["EMPTY_QUERY"],
                trace={"latency_ms": round(elapsed_ms, 2), "status": "error"}
            )

        # 2. Truy xuất top-k đoạn văn bản liên quan từ KB Index (Vector RAG)
        top_k = int(request.get("top_k", 3))
        retrieved_chunks = self.artifacts.retrieve(query=query, top_k=top_k)

        # 2b. Truy xuất Đồ thị tri thức (Graph RAG từ Neo4j)
        graph_facts = self.graph_retriever.search_graph(query=query)

        has_confident_vector = bool(retrieved_chunks and retrieved_chunks[0]["similarity_score"] >= self.similarity_threshold)
        has_confident_graph = bool(graph_facts)

        # 3. Kiểm định chất lượng căn cứ y khoa (Similarity Threshold Guardrail & Graph Evidence)
        if not has_confident_vector and not has_confident_graph:
            allow_chitchat = bool(request.get("allow_chitchat", False))
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            max_score = retrieved_chunks[0]["similarity_score"] if retrieved_chunks else 0.0

            # Nếu không bật chitchat -> từ chối an toàn để bảo đảm nguyên tắc RAG
            if not allow_chitchat:
                return AgentResponse(
                    agent=self.name,
                    content={
                        "message": "Không đủ căn cứ y khoa đáng tin cậy để giải đáp câu hỏi này.",
                        "explanation": "Câu hỏi nằm ngoài phạm vi kho tài liệu chuẩn mực và đồ thị tri thức đái tháo đường.",
                        "max_similarity_score": round(max_score, 4),
                        "threshold_required": self.similarity_threshold
                    },
                    confidence=round(max_score, 4),
                    evidence=[],
                    flags=["OUT_OF_SCOPE", "REFUSED_GROUNDING"],
                    trace={
                        "latency_ms": round(elapsed_ms, 2),
                        "top_score": round(max_score, 4),
                        "status": "refused_out_of_scope"
                    }
                )

            # Khi cho phép hội thoại xã giao (Chitchat): gọi Gemini trả lời tự nhiên
            chitchat_answer = self._call_gemini_conversational(query)
            if not chitchat_answer:
                chitchat_answer = (
                    "Xin chào! Tôi là Trợ lý AI y tế chuyên sâu về bệnh Đái tháo đường của PTIT. "
                    "Câu hỏi của bạn nằm ngoài tài liệu chuyên môn về tiểu đường. Bạn có thể hỏi tôi về tiêu chuẩn chẩn đoán, "
                    "đường huyết, chế độ dinh dưỡng, vận động hoặc nhập các chỉ số ở cột bên trái để nhận tư vấn lâm sàng nhé!"
                )

            return AgentResponse(
                agent=self.name,
                content={
                    "answer": chitchat_answer,
                    "mode": "conversational_chitchat",
                    "citations": [],
                    "graph_facts": [],
                    "message": chitchat_answer,
                    "explanation": "Phản hồi hội thoại tự nhiên của Trợ lý AI khi câu hỏi nằm ngoài tài liệu chuẩn về đái tháo đường."
                },
                confidence=round(max_score, 4),
                evidence=[],
                flags=["PASS", "CONVERSATIONAL_CHITCHAT"],
                trace={
                    "latency_ms": round(elapsed_ms, 2),
                    "generation_mode": "conversational_chitchat",
                    "status": "chitchat_handled"
                }
            )

        # 4. Hợp nhất bằng chứng: Tài liệu văn bản (Vector RAG) + Quan hệ thực thể (Neo4j Graph RAG)
        citations = [
            {
                "doc_id": c["doc_id"],
                "source_file": c["source_file"],
                "section_or_page": c["section_or_page"],
                "similarity_score": round(c["similarity_score"], 4),
                "excerpt": c["text"][:250] + ("..." if len(c["text"]) > 250 else "")
            }
            for c in retrieved_chunks
        ]

        all_evidence = list(citations)
        for gf in graph_facts:
            all_evidence.append({
                "doc_id": f"NEO4J_{gf['type']}_{gf['relationship']}",
                "source_file": "Neo4j Knowledge Graph",
                "section_or_page": gf["type"],
                "similarity_score": 1.0,
                "excerpt": gf["fact"]
            })

        llm_answer = self._call_gemini(query, retrieved_chunks, graph_facts=graph_facts)
        mode = "generative_grounded" if llm_answer else "extractive_verbatim"
        final_answer = llm_answer if llm_answer else self._format_extractive_answer(retrieved_chunks, graph_facts=graph_facts)

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        top_score = float(retrieved_chunks[0]["similarity_score"]) if retrieved_chunks else 0.85
        if has_confident_graph:
            top_score = max(top_score, 0.88)

        primary_source = retrieved_chunks[0]["source_file"] if retrieved_chunks else "Neo4j Knowledge Graph"
        primary_section = retrieved_chunks[0]["section_or_page"] if retrieved_chunks else "Graph Database"

        return AgentResponse(
            agent=self.name,
            content={
                "answer": final_answer,
                "mode": mode,
                "citations": citations,
                "graph_facts": graph_facts,
                "retrieval_mode": "hybrid_graph_rag" if graph_facts else "vector_rag",
                "primary_source": primary_source,
                "primary_section": primary_section
            },
            confidence=round(min(1.0, top_score), 4),
            evidence=all_evidence,
            flags=["PASS", "EVIDENCE_ATTACHED"],
            trace={
                "latency_ms": round(elapsed_ms, 2),
                "chunks_retrieved": len(retrieved_chunks),
                "graph_facts_retrieved": len(graph_facts),
                "top_similarity_score": round(top_score, 4),
                "generation_mode": mode
            }
        )
