import streamlit as st
import json
import os
from datetime import datetime, date, timedelta
import uuid

# ─────────────────────────────────────────────
# 상수
# ─────────────────────────────────────────────
TEAM_MEMBERS = ["서다경", "노은지", "고해일", "조세빈", "하민수", "유지민", "고창웅"]
TEAM_NAME = "마케팅10팀"
DATA_FILE = os.path.join(os.path.dirname(__file__), "todos.json")
MEMO_FILE = os.path.join(os.path.dirname(__file__), "memo.json")

STATUS_OPTIONS = ["대기중", "진행중", "완료"]
STATUS_EMOJI = {"대기중": "⏳", "진행중": "🔄", "완료": "✅"}
STATUS_LABEL = {"대기중": "⏳ 대기중", "진행중": "🔄 진행중", "완료": "✅ 완료"}

MEMBER_COLORS = {
    "서다경": "#FF6B6B", "노은지": "#4ECDC4", "고해일": "#45B7D1",
    "조세빈": "#96CEB4", "하민수": "#F0A500", "유지민": "#DDA0DD", "고창웅": "#98D8C8"
}

TODAY = date.today().isoformat()
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def get_display_name(member: str) -> str:
    return f"@{member} / {TEAM_NAME}"


# ─────────────────────────────────────────────
# 데이터 I/O
# ─────────────────────────────────────────────
def load_todos() -> list:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_todos(todos: list) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2, default=str)


def carryover_todos():
    """앱 시작 시 미완료 TODO를 오늘 날짜로 자동 이월"""
    changed = False
    for i, todo in enumerate(st.session_state.todos):
        # 하위 호환: 기존 todos에 target_date 없을 경우 created_at 기준으로 세팅
        if "target_date" not in todo:
            created = todo.get("created_at", TODAY)[:10]
            st.session_state.todos[i]["target_date"] = created
            st.session_state.todos[i]["created_date"] = created
            st.session_state.todos[i].setdefault("completed_date", None)
            st.session_state.todos[i].setdefault("carryover_from", None)
            changed = True

        target = st.session_state.todos[i]["target_date"]
        if target < TODAY and todo.get("status") != "완료":
            if not st.session_state.todos[i].get("carryover_from"):
                st.session_state.todos[i]["carryover_from"] = target
            st.session_state.todos[i]["target_date"] = TODAY
            changed = True

    if changed:
        save_todos(st.session_state.todos)


def add_todo(title: str, assignees: list) -> None:
    todo = {
        "id": str(uuid.uuid4()),
        "title": title,
        "assignees": assignees,
        "details": "",
        "status": "대기중",
        "created_date": TODAY,
        "target_date": TODAY,
        "completed_date": None,
        "carryover_from": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    st.session_state.todos.append(todo)
    save_todos(st.session_state.todos)


def update_todo(todo_id: str, updates: dict) -> None:
    for i, todo in enumerate(st.session_state.todos):
        if todo["id"] == todo_id:
            st.session_state.todos[i].update(updates)
            st.session_state.todos[i]["updated_at"] = datetime.now().isoformat()
            if updates.get("status") == "완료":
                st.session_state.todos[i]["completed_date"] = TODAY
            elif "status" in updates:
                st.session_state.todos[i]["completed_date"] = None
            save_todos(st.session_state.todos)
            break


def delete_todo(todo_id: str) -> None:
    st.session_state.todos = [t for t in st.session_state.todos if t["id"] != todo_id]
    save_todos(st.session_state.todos)


# ─────────────────────────────────────────────
# 메모 I/O
# ─────────────────────────────────────────────
def load_memo() -> list:
    if os.path.exists(MEMO_FILE):
        with open(MEMO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_memo_data(memos: list) -> None:
    with open(MEMO_FILE, "w", encoding="utf-8") as f:
        json.dump(memos, f, ensure_ascii=False, indent=2, default=str)


def get_today_todos(member: str = None) -> list:
    todos = [t for t in st.session_state.todos if t.get("target_date") == TODAY]
    if member:
        todos = [t for t in todos if member in t.get("assignees", [])]
    return todos


# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
    }
    section[data-testid="stSidebar"] * { color: #e8e8f0 !important; }
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.13);
        border-radius: 10px;
        color: #e8e8f0 !important;
        text-align: left;
        transition: all 0.2s;
        font-size: 0.88rem;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.16);
        transform: translateX(3px);
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        border: none !important;
        font-weight: 600;
    }

    /* 메트릭 */
    div[data-testid="metric-container"] {
        background: white;
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #f0f0f0;
    }

    /* 빠른 추가 영역 */
    .quick-add-box {
        background: #f5f7ff;
        border: 2px dashed #c7d2fe;
        border-radius: 14px;
        padding: 14px 18px 10px 18px;
        margin-bottom: 18px;
    }
    .quick-add-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #6366f1;
        margin-bottom: 6px;
    }

    /* TODO 행 */
    .todo-row {
        display: flex;
        align-items: center;
        background: white;
        border-radius: 10px;
        padding: 10px 14px;
        margin: 4px 0;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        border-left: 4px solid #667eea;
        transition: box-shadow 0.15s;
    }
    .todo-row:hover { box-shadow: 0 3px 12px rgba(0,0,0,0.1); }
    .todo-row.todo-done { border-left-color: #27AE60; background: #fafffe; }
    .todo-row.todo-progress { border-left-color: #4A90D9; }

    /* 칩 */
    .chip-assignee {
        display: inline-block;
        padding: 2px 9px;
        border-radius: 20px;
        font-size: 0.74rem;
        background: #EDE9FE;
        color: #5B21B6;
        margin: 1px 2px;
        font-weight: 500;
    }
    .chip-carryover {
        display: inline-block;
        padding: 1px 7px;
        border-radius: 10px;
        font-size: 0.7rem;
        background: #FEF3CD;
        color: #856404;
        margin-left: 5px;
        vertical-align: middle;
    }

    /* 섹션 헤더 */
    .sec-header {
        font-size: 0.95rem;
        font-weight: 700;
        color: #374151;
        padding: 5px 0 3px 0;
        border-bottom: 2px solid #e5e7eb;
        margin: 16px 0 8px 0;
    }

    /* 페이지 타이틀 */
    .page-title {
        font-size: 1.55rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 2px;
    }
    .page-sub {
        color: #6b7280;
        font-size: 0.88rem;
        margin-bottom: 18px;
    }

    /* 히스토리 */
    .hist-date-bar {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 10px;
        padding: 9px 16px;
        margin: 14px 0 8px 0;
        font-weight: 600;
        font-size: 0.95rem;
    }
    .hist-row-done {
        background: #f0fdf4;
        border-left: 3px solid #27AE60;
        border-radius: 6px;
        padding: 7px 12px;
        margin: 3px 0;
        font-size: 0.88rem;
    }
    .hist-row-undone {
        background: #fffbeb;
        border-left: 3px solid #F5A623;
        border-radius: 6px;
        padding: 7px 12px;
        margin: 3px 0;
        font-size: 0.88rem;
    }

    /* 빈 상태 */
    .empty-box {
        text-align: center;
        color: #9ca3af;
        padding: 32px;
        font-size: 0.92rem;
        background: #fafafa;
        border-radius: 12px;
    }

    /* 컬럼 헤더 */
    .col-head {
        font-size: 0.78rem;
        font-weight: 600;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding-bottom: 4px;
    }

    /* 메모 영역 */
    .memo-wrap {
        background: #fffde7;
        border: 1.5px solid #ffe082;
        border-radius: 14px;
        padding: 14px 18px 12px 18px;
        margin-bottom: 14px;
        position: relative;
    }
    .memo-label {
        font-size: 0.78rem;
        font-weight: 700;
        color: #b45309;
        margin-bottom: 6px;
        letter-spacing: 0.03em;
    }
    .memo-content {
        font-size: 0.92rem;
        color: #374151;
        white-space: pre-wrap;
        line-height: 1.65;
        min-height: 24px;
    }
    .memo-empty {
        font-size: 0.88rem;
        color: #d1b04a;
        font-style: italic;
    }
    .memo-item {
        background: white;
        border-radius: 10px;
        padding: 10px 14px;
        margin: 6px 0;
        border-left: 4px solid #fbbf24;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        font-size: 0.9rem;
        color: #374151;
        white-space: pre-wrap;
        line-height: 1.55;
        position: relative;
    }
    .memo-meta {
        font-size: 0.72rem;
        color: #9ca3af;
        margin-top: 4px;
    }
    </style>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 메모 컴포넌트
# ─────────────────────────────────────────────
def render_memo_section():
    """새 TODO 추가 위에 표시되는 공유 메모 게시판 (익명)"""
    if "memos" not in st.session_state:
        st.session_state.memos = load_memo()
    if "memo_edit_id" not in st.session_state:
        st.session_state.memo_edit_id = None

    memos = st.session_state.memos

    st.markdown('<div class="memo-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="memo-label">📝 팀 메모장</div>', unsafe_allow_html=True)

    # ── 새 메모 입력 폼 ──
    with st.form("memo_add_form", clear_on_submit=True):
        new_text = st.text_area(
            "메모 입력",
            placeholder="공유하고 싶은 내용을 자유롭게 적어보세요... (익명)",
            height=80,
            label_visibility="collapsed",
        )
        c1, c2 = st.columns([1, 5])
        with c1:
            add_btn = st.form_submit_button("📌 등록", type="primary", use_container_width=True)
        if add_btn and new_text.strip():
            memo_item = {
                "id": str(uuid.uuid4()),
                "content": new_text.strip(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
            st.session_state.memos.insert(0, memo_item)
            save_memo_data(st.session_state.memos)
            st.rerun()

    # ── 메모 목록 ──
    if not memos:
        st.markdown('<div class="memo-empty">아직 메모가 없어요. 위에서 자유롭게 남겨보세요!</div>', unsafe_allow_html=True)
    else:
        for memo in memos:
            mid = memo["id"]
            is_editing = st.session_state.memo_edit_id == mid

            if is_editing:
                # 수정 모드
                with st.form(f"memo_edit_{mid}", clear_on_submit=False):
                    edited = st.text_area(
                        "수정",
                        value=memo["content"],
                        height=80,
                        label_visibility="collapsed",
                        key=f"memo_edit_text_{mid}",
                    )
                    ea, eb, _ = st.columns([1, 1, 4])
                    with ea:
                        if st.form_submit_button("💾 저장", type="primary"):
                            for i, m in enumerate(st.session_state.memos):
                                if m["id"] == mid:
                                    st.session_state.memos[i]["content"] = edited.strip()
                                    st.session_state.memos[i]["updated_at"] = datetime.now().isoformat()
                                    break
                            save_memo_data(st.session_state.memos)
                            st.session_state.memo_edit_id = None
                            st.rerun()
                    with eb:
                        if st.form_submit_button("취소"):
                            st.session_state.memo_edit_id = None
                            st.rerun()
            else:
                # 표시 모드
                dt = memo.get("updated_at", memo.get("created_at", ""))[:16].replace("T", " ")
                updated_mark = " (수정됨)" if memo.get("updated_at") != memo.get("created_at") else ""

                col_txt, col_btn1, col_btn2 = st.columns([7, 0.7, 0.7])
                with col_txt:
                    st.markdown(
                        f'<div class="memo-item">{memo["content"]}'
                        f'<div class="memo-meta">익명 · {dt}{updated_mark}</div></div>',
                        unsafe_allow_html=True,
                    )
                with col_btn1:
                    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                    if st.button("✏️", key=f"memo_edit_btn_{mid}", help="수정"):
                        st.session_state.memo_edit_id = mid
                        st.rerun()
                with col_btn2:
                    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"memo_del_{mid}", help="삭제"):
                        st.session_state.memos = [m for m in st.session_state.memos if m["id"] != mid]
                        save_memo_data(st.session_state.memos)
                        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# 공통 컴포넌트
# ─────────────────────────────────────────────
def render_quick_add(context_member: str = None):
    """간소화된 빠른 TODO 추가: 업무상세 + 담당자만"""
    scope = context_member or "all"
    st.markdown('<div class="quick-add-label">➕ 새 TODO 추가</div>', unsafe_allow_html=True)

    with st.form(f"qaform_{scope}", clear_on_submit=True):
        c1, c2, c3 = st.columns([4, 3, 1])
        with c1:
            title = st.text_input(
                "업무 상세",
                placeholder="업무 내용을 입력하세요...",
                label_visibility="collapsed",
            )
        with c2:
            default_val = [context_member] if context_member else []
            assignees = st.multiselect(
                "담당자",
                TEAM_MEMBERS,
                default=default_val,
                format_func=lambda x: f"@{x}",
                label_visibility="collapsed",
            )
        with c3:
            submitted = st.form_submit_button("추가", type="primary", use_container_width=True)

        if submitted:
            if not title.strip():
                st.warning("업무 내용을 입력하세요.")
            elif not assignees:
                st.warning("담당자를 선택하세요.")
            else:
                add_todo(title.strip(), assignees)
                assignee_str = ", ".join(f"@{a}" for a in assignees)
                st.success(f"✅ 추가 완료! → {assignee_str}")
                st.rerun()


def format_slack_text(todo: dict) -> str:
    """슬랙 붙여넣기용 단건 포맷 텍스트"""
    assignees_str = "  ".join(f"@{a} / {TEAM_NAME}" for a in todo.get("assignees", []))
    status = todo.get("status", "대기중")
    lines = [
        f"📌 {todo['title']}",
        f"👤 {assignees_str}" if assignees_str else "",
        f"진행상태: {STATUS_EMOJI.get(status, '')} {status}",
    ]
    return "\n".join(line for line in lines if line)


def format_all_slack_text(todos: list, title: str = "마케팅10팀 TODO") -> str:
    """슬랙 붙여넣기용 전체 리스트 포맷 텍스트"""
    today_str = date.today().strftime("%Y/%m/%d")
    wd = WEEKDAYS[date.today().weekday()]
    lines = [f"📋 *{title}* — {today_str} ({wd}요일)", ""]

    for status in STATUS_OPTIONS:
        group = [t for t in todos if t.get("status") == status]
        if not group:
            continue
        lines.append(f"{STATUS_EMOJI[status]} *{status}* ({len(group)}건)")
        for todo in group:
            assignees_str = "  ".join(f"@{a} / {TEAM_NAME}" for a in todo.get("assignees", []))
            co = f" ↩ {todo['carryover_from']} 이월" if todo.get("carryover_from") else ""
            lines.append(f"  📌 {todo['title']}{co}")
            if assignees_str:
                lines.append(f"       👤 {assignees_str}")
        lines.append("")

    return "\n".join(lines).strip()


def render_todo_row(todo: dict, key_suffix: str = ""):
    """심플 리스트 TODO 행: 업무명 | 담당자 | 상태 셀렉트 | 복사 | 삭제"""
    status = todo.get("status", "대기중")
    is_done = status == "완료"
    carryover = todo.get("carryover_from")

    c_title, c_assign, c_status, c_copy, c_del = st.columns([4, 2.5, 2, 0.6, 0.5])

    with c_title:
        title_style = "text-decoration:line-through; color:#9ca3af;" if is_done else "color:#111827; font-weight:500;"
        carryover_html = f'<span class="chip-carryover">↩ {carryover} 이월</span>' if carryover else ""
        st.markdown(
            f'<div style="{title_style} font-size:0.93rem; padding:6px 0; line-height:1.4;">'
            f'{todo["title"]}{carryover_html}</div>',
            unsafe_allow_html=True,
        )

    with c_assign:
        chips = "".join(f'<span class="chip-assignee">@{a}</span>' for a in todo.get("assignees", []))
        st.markdown(f'<div style="padding:6px 0;">{chips}</div>', unsafe_allow_html=True)

    with c_status:
        new_status = st.selectbox(
            "상태",
            STATUS_OPTIONS,
            index=STATUS_OPTIONS.index(status),
            key=f"st_{todo['id']}_{key_suffix}",
            label_visibility="collapsed",
            format_func=lambda s: STATUS_LABEL[s],
        )
        if new_status != status:
            update_todo(todo["id"], {"status": new_status})
            st.rerun()

    with c_copy:
        with st.popover("📋", help="슬랙 복사"):
            slack_text = format_slack_text(todo)
            st.caption("아래 텍스트를 복사해서 슬랙에 붙여넣기 하세요.")
            st.code(slack_text, language=None)

    with c_del:
        if st.button("🗑️", key=f"del_{todo['id']}_{key_suffix}", help="삭제"):
            delete_todo(todo["id"])
            st.rerun()


def render_todo_list(todos: list, key_suffix: str = "", list_title: str = "마케팅10팀 TODO"):
    """상태별 그룹 리스트 출력"""
    if not todos:
        st.markdown('<div class="empty-box">📭 할일이 없습니다.<br>위에서 새 TODO를 추가해보세요!</div>', unsafe_allow_html=True)
        return

    # 전체 복사 버튼 + 컬럼 헤더
    head_left, head_right = st.columns([8, 2])
    with head_left:
        h1, h2, h3, h4, h5 = st.columns([4, 2.5, 2, 0.6, 0.5])
        h1.markdown('<div class="col-head">업무 상세</div>', unsafe_allow_html=True)
        h2.markdown('<div class="col-head">담당자</div>', unsafe_allow_html=True)
        h3.markdown('<div class="col-head">상태</div>', unsafe_allow_html=True)
        h4.markdown("")
        h5.markdown("")
    with head_right:
        with st.popover("📋 전체 복사", use_container_width=True):
            all_text = format_all_slack_text(todos, title=list_title)
            st.caption(f"총 {len(todos)}건 · 아래 텍스트를 복사해 슬랙에 붙여넣기 하세요.")
            st.code(all_text, language=None)

    for status in STATUS_OPTIONS:
        group = [t for t in todos if t.get("status") == status]
        if not group:
            continue
        st.markdown(
            f'<div class="sec-header">{STATUS_EMOJI[status]} {status} '
            f'<span style="color:#9ca3af;font-weight:400;font-size:0.85rem">({len(group)}건)</span></div>',
            unsafe_allow_html=True,
        )
        for todo in group:
            render_todo_row(todo, key_suffix=key_suffix)


# ─────────────────────────────────────────────
# 히스토리 탭
# ─────────────────────────────────────────────
def render_history_tab(member: str = None):
    scope = member or "all"
    st.markdown("날짜를 선택하면 그날의 할일 현황을 볼 수 있습니다.")

    col_d, _ = st.columns([2, 4])
    with col_d:
        sel_date = st.date_input(
            "날짜 선택",
            value=date.today(),
            key=f"hist_date_{scope}",
            format="YYYY/MM/DD",
        )
    sel_str = str(sel_date)
    wd = WEEKDAYS[sel_date.weekday()]

    # 해당 날짜의 todos: target_date가 그날이거나 completed_date가 그날인 것
    day_todos = [
        t for t in st.session_state.todos
        if (t.get("target_date") == sel_str or t.get("completed_date") == sel_str)
        and (member is None or member in t.get("assignees", []))
    ]

    if not day_todos:
        st.markdown(
            f'<div class="empty-box">📭 {sel_str} ({wd}요일) 에 기록된 할일이 없습니다.</div>',
            unsafe_allow_html=True,
        )
        return

    done_todos = [t for t in day_todos if t.get("status") == "완료"]
    undone_todos = [t for t in day_todos if t.get("status") != "완료"]
    ratio = len(done_todos) / len(day_todos) * 100 if day_todos else 0

    st.markdown(
        f'<div class="hist-date-bar">📅 {sel_str} ({wd}요일) &nbsp;·&nbsp; '
        f'총 {len(day_todos)}건 &nbsp;·&nbsp; 완료율 {ratio:.0f}%</div>',
        unsafe_allow_html=True,
    )
    st.progress(ratio / 100)

    if undone_todos:
        st.markdown(f"**⏳ 미완료 ({len(undone_todos)}건)**")
        for t in undone_todos:
            chips = "".join(f'<span class="chip-assignee">@{a}</span>' for a in t.get("assignees", []))
            co = '<span class="chip-carryover">이월</span>' if t.get("carryover_from") else ""
            status_lbl = STATUS_EMOJI.get(t.get("status", "대기중"), "⏳")
            st.markdown(
                f'<div class="hist-row-undone">{status_lbl} {t["title"]}{co} &nbsp;{chips}</div>',
                unsafe_allow_html=True,
            )

    if done_todos:
        st.markdown(f"**✅ 완료 ({len(done_todos)}건)**")
        for t in done_todos:
            chips = "".join(f'<span class="chip-assignee">@{a}</span>' for a in t.get("assignees", []))
            st.markdown(
                f'<div class="hist-row-done">✅ <span style="text-decoration:line-through;color:#6b7280;">{t["title"]}</span> &nbsp;{chips}</div>',
                unsafe_allow_html=True,
            )

    # 멤버별 요약 (전체 뷰에서만)
    if member is None and day_todos:
        st.markdown("---")
        st.markdown("**👥 팀원별 현황**")
        cols = st.columns(len(TEAM_MEMBERS))
        for i, m in enumerate(TEAM_MEMBERS):
            m_todos = [t for t in day_todos if m in t.get("assignees", [])]
            m_done = len([t for t in m_todos if t.get("status") == "완료"])
            color = MEMBER_COLORS.get(m, "#667eea")
            cols[i].markdown(
                f'<div style="text-align:center; background:white; border-radius:10px; '
                f'padding:10px 6px; border-top:4px solid {color}; box-shadow:0 1px 4px rgba(0,0,0,0.07);">'
                f'<div style="font-size:0.78rem; font-weight:600; color:#374151;">@{m}</div>'
                f'<div style="font-size:1.1rem; font-weight:700; color:{color};">{m_done}/{len(m_todos)}</div>'
                f'<div style="font-size:0.7rem; color:#9ca3af;">완료</div></div>',
                unsafe_allow_html=True,
            )


# ─────────────────────────────────────────────
# 페이지: 전체
# ─────────────────────────────────────────────
def show_all_view():
    today_todos = get_today_todos()
    total = len(today_todos)
    p_cnt = len([t for t in today_todos if t.get("status") == "대기중"])
    r_cnt = len([t for t in today_todos if t.get("status") == "진행중"])
    d_cnt = len([t for t in today_todos if t.get("status") == "완료"])

    st.markdown('<div class="page-title">👥 팀원 전체 TODO</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="page-sub">📅 오늘 {TODAY} ({WEEKDAYS[date.today().weekday()]}요일) &nbsp;·&nbsp; '
        f'미완료 항목은 매일 자동 이월됩니다.</div>',
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📋 오늘 전체", f"{total}개")
    m2.metric("⏳ 대기중", f"{p_cnt}개")
    m3.metric("🔄 진행중", f"{r_cnt}개")
    m4.metric("✅ 완료", f"{d_cnt}개")

    tab_today, tab_hist = st.tabs(["📋 오늘 할일", "📅 일정 기록"])

    with tab_today:
        render_memo_section()

        st.markdown('<div class="quick-add-box">', unsafe_allow_html=True)
        render_quick_add()
        st.markdown("</div>", unsafe_allow_html=True)

        # 필터
        fc1, fc2 = st.columns([3, 2])
        with fc1:
            f_member = st.selectbox(
                "담당자 필터",
                ["전체"] + TEAM_MEMBERS,
                format_func=lambda x: x if x == "전체" else f"@{x}",
                key="all_f_member",
            )
        with fc2:
            f_status = st.selectbox("상태 필터", ["전체"] + STATUS_OPTIONS, key="all_f_status")

        todos = today_todos[:]
        if f_member != "전체":
            todos = [t for t in todos if f_member in t.get("assignees", [])]
        if f_status != "전체":
            todos = [t for t in todos if t.get("status") == f_status]

        render_todo_list(todos, key_suffix="all", list_title="마케팅10팀 전체 TODO")

    with tab_hist:
        render_history_tab()


# ─────────────────────────────────────────────
# 페이지: 개인 워크스페이스
# ─────────────────────────────────────────────
def show_member_view(member: str):
    display = get_display_name(member)
    color = MEMBER_COLORS.get(member, "#667eea")
    today_todos = get_today_todos(member)

    total = len(today_todos)
    p_cnt = len([t for t in today_todos if t.get("status") == "대기중"])
    r_cnt = len([t for t in today_todos if t.get("status") == "진행중"])
    d_cnt = len([t for t in today_todos if t.get("status") == "완료"])

    st.markdown(
        f'<div class="page-title" style="border-left:5px solid {color}; padding-left:14px;">{display}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="page-sub">📅 오늘 {TODAY} ({WEEKDAYS[date.today().weekday()]}요일) &nbsp;·&nbsp; '
        f'미완료 항목은 내일 자동 이월됩니다.</div>',
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("📋 오늘 전체", f"{total}개")
    m2.metric("⏳ 대기중", f"{p_cnt}개")
    m3.metric("🔄 진행중", f"{r_cnt}개")
    m4.metric("✅ 완료", f"{d_cnt}개")

    tab_today, tab_hist = st.tabs(["📋 오늘 할일", "📅 일정 기록"])

    with tab_today:
        render_memo_section()

        st.markdown('<div class="quick-add-box">', unsafe_allow_html=True)
        render_quick_add(context_member=member)
        st.markdown("</div>", unsafe_allow_html=True)

        render_todo_list(today_todos, key_suffix=member, list_title=f"@{member} / {TEAM_NAME} TODO")

    with tab_hist:
        render_history_tab(member=member)


# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:18px 0 8px 0;">
            <div style="font-size:2rem;">📋</div>
            <div style="font-size:1.05rem; font-weight:700; color:#e8e8f0; margin-top:4px;">마케팅10팀</div>
            <div style="font-size:0.75rem; color:#a0aec0;">TODO Dashboard</div>
        </div>
        """, unsafe_allow_html=True)

        today_todos = get_today_todos()
        total = len(today_todos)
        done = len([t for t in today_todos if t.get("status") == "완료"])
        ratio = done / total if total > 0 else 0

        st.markdown(
            f"""
            <div style="padding:8px 12px; background:rgba(255,255,255,0.07); border-radius:10px; margin:8px 0 14px 0;">
                <div style="font-size:0.78rem; color:#a0aec0; margin-bottom:4px;">오늘 팀 진행률</div>
                <div style="background:rgba(255,255,255,0.14); border-radius:10px; height:7px; overflow:hidden;">
                    <div style="background:linear-gradient(90deg,#667eea,#764ba2);
                                width:{ratio*100:.0f}%; height:100%; border-radius:10px;"></div>
                </div>
                <div style="font-size:0.8rem; color:#e8e8f0; margin-top:4px; text-align:right;">{done}/{total} 완료</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        is_all = st.session_state.current_page == "전체"
        if st.button(
            "👥  팀원 전체",
            use_container_width=True,
            type="primary" if is_all else "secondary",
            key="nav_all",
        ):
            st.session_state.current_page = "전체"
            st.rerun()

        st.markdown(
            "<div style='font-size:0.72rem; color:#6b7280; margin:14px 0 5px 3px;'>🗂️ 개인 워크스페이스</div>",
            unsafe_allow_html=True,
        )

        for member in TEAM_MEMBERS:
            m_todos = get_today_todos(member)
            not_done = len([t for t in m_todos if t.get("status") != "완료"])
            badge = f"  🔴 {not_done}" if not_done > 0 else ""
            is_cur = st.session_state.current_page == member
            if st.button(
                f"@{member}{badge}",
                use_container_width=True,
                key=f"nav_{member}",
                type="primary" if is_cur else "secondary",
            ):
                st.session_state.current_page = member
                st.rerun()

        st.markdown(
            "<div style='margin-top:28px; font-size:0.7rem; color:#4a5568; text-align:center;'>© 마케팅10팀 2026</div>",
            unsafe_allow_html=True,
        )


# ─────────────────────────────────────────────
# 메인
# ─────────────────────────────────────────────
def main():
    st.set_page_config(
        page_title="마케팅10팀 TODO",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_css()

    if "todos" not in st.session_state:
        st.session_state.todos = load_todos()
    if "current_page" not in st.session_state:
        st.session_state.current_page = "전체"
    if "carryover_done" not in st.session_state:
        carryover_todos()
        st.session_state.carryover_done = True

    render_sidebar()

    if st.session_state.current_page == "전체":
        show_all_view()
    else:
        show_member_view(st.session_state.current_page)


if __name__ == "__main__":
    main()
