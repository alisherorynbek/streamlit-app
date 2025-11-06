# app.py — Calculator + Mini Game Arcade (Streamlit)
import random
import re
import streamlit as st

# ---------------------------- app config ----------------------------
st.set_page_config(page_title="Calc + Games", page_icon="🎮", layout="centered")
st.title("🎮 Calc + Games")
st.caption("Made with Python + Streamlit")

# ---------------------------- utilities ----------------------------
def init_state(defaults: dict):
    """Initialize session_state keys once."""
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ---------------------------- PAGE: Calculator ----------------------------
def page_calculator():
    st.header("🧮 Web Calculator")

    init_state({"calc_history": []})

    # --- basic operation helper ---
    def calc(a: float, b: float, op: str):
        if op == "+":  return a + b
        if op == "-":  return a - b
        if op == "×":  return a * b
        if op == "÷":
            if b == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            return a / b
        if op == "^":  return a ** b
        raise ValueError("Unknown operation")

    with st.form("calc_form", clear_on_submit=False):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            a = st.number_input("First number (a)", value=0.0, format="%.6f")
        with c3:
            b = st.number_input("Second number (b)", value=0.0, format="%.6f")
        with c2:
            op = st.selectbox("Operation", ["+", "-", "×", "÷", "^"])
        prec = st.slider("Decimal places", 0, 10, 4)
        run = st.form_submit_button("Calculate", use_container_width=True)

    if run:
        try:
            result = calc(a, b, op)
            txt = f"{a} {op} {b} = {round(result, prec)}"
            st.success(f"Result: **{txt}**")
            st.session_state.calc_history.insert(0, txt)
        except ZeroDivisionError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("### Expression mode")
    expr = st.text_input("Enter expression (numbers + + - * / ( ) . only)", key="expr_input")
    if st.button("Evaluate expression"):
        if re.fullmatch(r"[0-9\.\+\-\*/\(\)\s]+", expr or ""):
            try:
                val = eval(expr, {"__builtins__": {}}, {})
                st.info(f"{expr} = **{val}**")
                st.session_state.calc_history.insert(0, f"{expr} = {val}")
            except Exception as e:
                st.error(f"Invalid expression: {e}")
        else:
            st.error("Only digits, + - * / ( ) and . are allowed.")

    st.markdown("### History")
    if st.session_state.calc_history:
        for i, line in enumerate(st.session_state.calc_history[:12], start=1):
            st.write(f"{i}. {line}")
        if st.button("Clear history"):
            st.session_state.calc_history.clear()
            st.rerun()
    else:
        st.caption("No calculations yet.")

# ---------------------------- PAGE: Guess the Number ----------------------------
def page_guess():
    st.header("🔢 Guess the Number (1–100)")

    init_state({"secret": random.randint(1, 100), "tries": 0, "hi_scores": []})

    guess = st.number_input("Your guess:", min_value=1, max_value=100, value=50, step=1)
    c1, c2 = st.columns(2)
    if c1.button("Check"):
        st.session_state.tries += 1
        if guess < st.session_state.secret:
            st.warning("Too low! 📉")
        elif guess > st.session_state.secret:
            st.warning("Too high! 📈")
        else:
            st.success(f"🎉 Correct! You needed {st.session_state.tries} tries.")
            st.session_state.hi_scores.append(st.session_state.tries)
            st.session_state.secret = random.randint(1, 100)
            st.session_state.tries = 0

    if c2.button("New secret"):
        st.session_state.secret = random.randint(1, 100)
        st.session_state.tries = 0
        st.info("New secret chosen!")

    col1, col2 = st.columns(2)
    col1.write(f"Tries in this round: **{st.session_state.tries}**")
    if st.session_state.hi_scores:
        best = ", ".join(map(str, sorted(st.session_state.hi_scores)[:5]))
        col2.write(f"Best scores (lower is better): **{best}**")
    else:
        col2.caption("No best scores yet.")

# ---------------------------- PAGE: Rock–Paper–Scissors ----------------------------
def page_rps():
    st.header("✊ ✋ ✌️ Rock–Paper–Scissors")

    init_state({"rps_score": {"You": 0, "Bot": 0, "Draws": 0}})

    choice = st.radio("Choose your move:", ["Rock", "Paper", "Scissors"], horizontal=True)
    if st.button("Play"):
        bot = random.choice(["Rock", "Paper", "Scissors"])
        beats = {"Rock": "Scissors", "Paper": "Rock", "Scissors": "Paper"}

        if choice == bot:
            st.info(f"Draw! You: **{choice}**  |  Bot: **{bot}**")
            st.session_state.rps_score["Draws"] += 1
        elif beats[choice] == bot:
            st.success(f"You win! **{choice}** beats **{bot}**")
            st.session_state.rps_score["You"] += 1
        else:
            st.error(f"You lose! **{bot}** beats **{choice}**")
            st.session_state.rps_score["Bot"] += 1

    st.write("**Scoreboard**")
    col1, col2, col3 = st.columns(3)
    col1.metric("You", st.session_state.rps_score["You"])
    col2.metric("Bot", st.session_state.rps_score["Bot"])
    col3.metric("Draws", st.session_state.rps_score["Draws"])

    if st.button("Reset RPS Score"):
        st.session_state.rps_score = {"You": 0, "Bot": 0, "Draws": 0}
        st.experimental_rerun()

# ---------------------------- helpers for Tic-Tac-Toe ----------------------------
def ttt_winner(board):
    wins = [(0,1,2),(3,4,5),(6,7,8),
            (0,3,6),(1,4,7),(2,5,8),
            (0,4,8),(2,4,6)]
    for a,b,c in wins:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if all(board):
        return "draw"
    return None

def ttt_ai_move(board, ai="O", human="X"):
    """Simple AI: win -> block -> center -> corner -> side."""
    empty = [i for i,v in enumerate(board) if v is None]
    # try to win
    for i in empty:
        b = board[:]; b[i] = ai
        if ttt_winner(b) == ai: return i
    # block human
    for i in empty:
        b = board[:]; b[i] = human
        if ttt_winner(b) == human: return i
    # center
    if 4 in empty: return 4
    # corners
    for i in [0,2,6,8]:
        if i in empty: return i
    # sides
    return empty[0] if empty else None

# ---------------------------- PAGE: Tic-Tac-Toe (glitch-free) ----------------------------
def page_ttt():
    st.header("⭕❌ Tic-Tac-Toe (You = X, AI = O)")

    init_state({
        "ttt_board": [None] * 9,
        "ttt_turn": "X",
        "ttt_score": {"You": 0, "AI": 0, "Draws": 0},
        "ttt_pending_ai": False,  # key fix: AI moves in the next rerun
    })

    board = st.session_state.ttt_board

    # --- user click handler ---
    def click_cell(idx: int):
        if st.session_state.ttt_turn != "X" or board[idx] is not None:
            return
        board[idx] = "X"
        st.session_state.ttt_turn = "O"
        st.session_state.ttt_pending_ai = True
        st.rerun()

    # --- draw grid ---
    for r in range(3):
        c1, c2, c3 = st.columns(3)
        for j, col in enumerate([c1, c2, c3]):
            with col:
                idx = r*3 + j
                label = board[idx] if board[idx] else " "
                disabled = (board[idx] is not None) or (st.session_state.ttt_turn != "X")
                st.button(
                    label, key=f"cell{idx}", disabled=disabled,
                    use_container_width=True,
                    on_click=click_cell, args=(idx,)
                )

    # --- if AI should move, do it on next run ---
    res = ttt_winner(board)
    if res is None and st.session_state.ttt_pending_ai and st.session_state.ttt_turn == "O":
        move = ttt_ai_move(board)
        if move is not None:
            board[move] = "O"
        st.session_state.ttt_turn = "X"
        st.session_state.ttt_pending_ai = False
        st.rerun()

    # --- evaluate result & reset round if finished ---
    res = ttt_winner(board)
    if res == "X":
        st.success("You win! 🎉")
        st.session_state.ttt_score["You"] += 1
        st.session_state.ttt_board = [None]*9
        st.session_state.ttt_turn = "X"
    elif res == "O":
        st.error("AI wins! 🤖")
        st.session_state.ttt_score["AI"] += 1
        st.session_state.ttt_board = [None]*9
        st.session_state.ttt_turn = "X"
    elif res == "draw":
        st.info("Draw 🤝")
        st.session_state.ttt_score["Draws"] += 1
        st.session_state.ttt_board = [None]*9
        st.session_state.ttt_turn = "X"

    # --- scoreboard + reset ---
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("You", st.session_state.ttt_score["You"])
    s2.metric("AI", st.session_state.ttt_score["AI"])
    s3.metric("Draws", st.session_state.ttt_score["Draws"])
    if s4.button("Reset scores"):
        st.session_state.ttt_score = {"You": 0, "AI": 0, "Draws": 0}
        st.experimental_rerun()

# ---------------------------- router (sidebar) ----------------------------
page = st.sidebar.selectbox(
    "Choose a page:",
    ["Calculator", "Tic-Tac-Toe", "Guess the Number", "Rock–Paper–Scissors"]
)
st.sidebar.caption("Tip: press **R** in the browser to rerun after edits.")

if page == "Calculator":
    page_calculator()
elif page == "Tic-Tac-Toe":
    page_ttt()
elif page == "Guess the Number":
    page_guess()
else:
    page_rps()
