import React from 'react';

/**
 * Component FormattedText:
 * Tự động chuyển đổi các ký tự markdown như **in đậm**, bullet points, trích dẫn [Nguồn: ...]
 * thành HTML hiển thị chuẩn đẹp trên giao diện thay vì hiện raw dấu **.
 */
export function FormattedText({ text, className = '' }) {
  if (!text) return null;

  // Tách văn bản theo các khối phân cách bởi dấu gạch ngang --- hoặc 2 dấu xuống dòng
  const blocks = text.split(/\n\s*---\s*\n/);

  return (
    <div className={`formatted-text-root ${className}`}>
      {blocks.map((block, bIdx) => {
        const isRefusal = block.includes('TUYỆT ĐỐI TỪ CHỐI') || block.includes('CẢNH BÁO CẤP CỨU');
        return (
          <React.Fragment key={bIdx}>
            {bIdx > 0 && <hr style={{ margin: '14px 0', border: 'none', borderTop: '1px dashed #cbd5e1' }} />}
            <div
              className={isRefusal ? 'safety-callout-box' : 'content-block'}
              style={
                isRefusal
                  ? {
                      backgroundColor: '#fff1f2',
                      borderLeft: '4px solid #e11d48',
                      padding: '10px 14px',
                      borderRadius: '6px',
                      marginBottom: '12px',
                      color: '#9f1239',
                    }
                  : {}
              }
            >
              {renderParagraphs(block)}
            </div>
          </React.Fragment>
        );
      })}
    </div>
  );
}

function renderParagraphs(rawText) {
  const paragraphs = rawText.trim().split('\n\n');

  return paragraphs.map((para, pIdx) => {
    const lines = para.split('\n');

    // Nếu các dòng trong đoạn này đều là danh sách bullet points (* hoặc - hoặc •)
    const isBulletList = lines.every((line) => /^\s*([*\-•]|\d+\.)\s+/.test(line));

    if (isBulletList) {
      return (
        <ul key={pIdx} style={{ margin: '6px 0 10px 18px', paddingLeft: '8px' }}>
          {lines.map((line, lIdx) => {
            const cleanLine = line.replace(/^\s*([*\-•]|\d+\.)\s+/, '');
            return (
              <li key={lIdx} style={{ marginBottom: '4px' }}>
                {parseInlineFormatting(cleanLine)}
              </li>
            );
          })}
        </ul>
      );
    }

    return (
      <p key={pIdx} style={{ margin: '0 0 10px 0', lineHeight: '1.65' }}>
        {lines.map((line, lIdx) => (
          <React.Fragment key={lIdx}>
            {lIdx > 0 && <br />}
            {parseInlineFormatting(line)}
          </React.Fragment>
        ))}
      </p>
    );
  });
}

function parseInlineFormatting(str) {
  if (!str) return null;

  // Regex nhận diện:
  // 1. **in đậm**
  // 2. `code`
  // 3. [Nguồn: ...]
  const regex = /(\*\*.*?\*\*|`.*?`|\[Nguồn:.*?\])/g;
  const parts = [];
  let lastIndex = 0;
  let match;
  let keyIdx = 0;

  while ((match = regex.exec(str)) !== null) {
    if (match.index > lastIndex) {
      parts.push(str.substring(lastIndex, match.index));
    }

    const token = match[0];
    if (token.startsWith('**') && token.endsWith('**')) {
      const boldContent = token.slice(2, -2);
      parts.push(
        <strong key={`b-${keyIdx++}`} style={{ fontWeight: 700, color: 'inherit' }}>
          {boldContent}
        </strong>
      );
    } else if (token.startsWith('`') && token.endsWith('`')) {
      parts.push(
        <code
          key={`c-${keyIdx++}`}
          style={{
            background: '#f1f5f9',
            padding: '1px 5px',
            borderRadius: '4px',
            fontSize: '0.9em',
            fontFamily: 'monospace',
          }}
        >
          {token.slice(1, -1)}
        </code>
      );
    } else if (token.startsWith('[Nguồn:') && token.endsWith(']')) {
      parts.push(
        <span
          key={`src-${keyIdx++}`}
          style={{
            display: 'inline-block',
            fontSize: '0.82em',
            color: '#0369a1',
            backgroundColor: '#e0f2fe',
            border: '1px solid #bae6fd',
            padding: '1px 7px',
            borderRadius: '4px',
            margin: '2px 2px',
            fontWeight: 500,
          }}
        >
          {token}
        </span>
      );
    }

    lastIndex = regex.lastIndex;
  }

  if (lastIndex < str.length) {
    parts.push(str.substring(lastIndex));
  }

  return parts.length > 0 ? parts : str;
}
