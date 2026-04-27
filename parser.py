from __future__ import annotations

from dataclasses import dataclass

from ifp_ast import (
    CHARS,
    CHARS_DECODED,
    TBinOp,
    TBool,
    TIf,
    TInt,
    TLam,
    TString,
    TUnOp,
    TVar,
    Term,
)


@dataclass(frozen=True)
class ParseError(Exception):
    kind: str
    index: int | None = None
    ch: str | None = None

    def __str__(self) -> str:
        if self.kind == "UnexpectedChar":
            return f"UnexpectedChar({self.ch!r}, {self.index})"
        if self.kind == "UnusedInput":
            return f"UnusedInput({self.index})"
        return "UnexpectedEOF"


def p_term(inp: str) -> Term:
    # TODO
    return Term()

_DECODE_MAP = {src: dst for src, dst in zip(CHARS, CHARS_DECODED)}
def from_base94(s: str) -> int:
    """Hàm dịch ngược chuỗi Base-94 thành số nguyên."""
    result = 0
    for char in s:
        # Công thức: (Mã_ASCII - 33) và nhân dồn với trọng số 94
        result = result * 94 + (ord(char) - 33)
    return result

def decode_string(s: str) -> str:
    """Hàm giải mã chuỗi theo mật mã thay thế 1-1."""
    out = []
    for ch in s:
        if ch not in _DECODE_MAP:
            # Nếu gặp ký tự lạ không có trong bảng mã, ném lỗi theo spec
            raise ParseError(kind="UnexpectedChar", ch=ch)
        out.append(_DECODE_MAP[ch])
    return "".join(out)

def p_term(inp: str) -> Term:
    
    def _parse(index: int) -> tuple[Term, int]:
        # Bỏ qua khoảng trắng trước khi đọc
        while index < len(inp) and inp[index] == ' ':
            index += 1
            
        # Nếu đã duyệt hết chuỗi mà vẫn bị gọi, tức là chuỗi bị cụt
        if index >= len(inp):
            raise ParseError(kind="UnexpectedEOF", index=index)
            
        indicator = inp[index]
        
        # 1. BOOLEAN (T / F) - Không có body
        if indicator == 'T':
            return TBool(True), index + 1
        elif indicator == 'F':
            return TBool(False), index + 1
            
        # 2. SỐ NGUYÊN (I) - Có body là base-94
        elif indicator == 'I':
            start = index + 1
            curr = start
            # Đọc liên tục cho đến khi gặp khoảng trắng hoặc hết chuỗi
            while curr < len(inp) and inp[curr] != ' ':
                curr += 1
            body = inp[start:curr]
            
            # Spec yêu cầu body không được rỗng
            if not body:
                raise ParseError(kind="UnexpectedChar", index=index, ch=' ')
                
            value = from_base94(body)
            return TInt(value), curr
            
        # 3. CHUỖI (S) - Có body là mật mã
        elif indicator == 'S':
            start = index + 1
            curr = start
            while curr < len(inp) and inp[curr] != ' ':
                curr += 1
            body = inp[start:curr]
            
            value = decode_string(body)
            return TString(value), curr
            
        # TODO: Sẽ code tiếp phần U, B, ?, L, v ở đây...
        
        else:
            # Nếu gặp Indicator không nhận diện được
            raise ParseError(kind="UnexpectedChar", index=index, ch=indicator)

    # --- Bắt đầu phân tích từ vị trí 0 ---
    term, final_index = _parse(0)
    
    # --- Kiểm tra rác thừa ở cuối chuỗi ---
    while final_index < len(inp) and inp[final_index] == ' ':
        final_index += 1
    if final_index < len(inp):
        raise ParseError(kind="UnusedInput", index=final_index)
        
    return term