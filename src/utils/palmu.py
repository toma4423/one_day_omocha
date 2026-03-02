from datetime import date, timedelta


def _to_int(val: int | str) -> int:
    """値を数値に変換します（'SKIP'や非数値は0として扱います）。"""
    if isinstance(val, int):
        return val
    if isinstance(val, str) and val.isdigit():
        return int(val)
    return 0


def calculate_total_points(daily_points: list[int | str]) -> int:
    """日ごとのポイント合計を計算します（'SKIP'等は0として扱う）。"""
    return sum(_to_int(p) for p in daily_points)


def evaluate_rank_status(total_points: int) -> str:
    """現在の合計ポイントからランクのステータスを評価します。"""
    if total_points >= 18:
        return "ランクアップ"
    elif total_points >= 12:
        return "キープ"
    else:
        return "ランクダウン"


def points_needed_for_keep(total_points: int) -> int:
    """キープ（12ポイント）までに必要なポイントを計算します。"""
    return max(0, 12 - total_points)


def points_needed_for_rank_up(total_points: int) -> int:
    """ランクアップ（18ポイント）までに必要なポイントを計算します。"""
    return max(0, 18 - total_points)


def generate_point_presets(target: int) -> list[tuple[int, ...]]:
    """目標ポイント（12または18）を達成するための7日間のポイント構成例を生成します。"""
    options = [6, 4, 2, 1]
    results = []

    def backtrack(current_combination: list[int], current_sum: int, start_idx: int) -> None:
        if len(current_combination) == 7:
            if current_sum >= target:
                results.append(tuple(current_combination))
            return

        for i in range(start_idx, len(options)):
            # 枝刈り：残りのすべてを最大値(6)にしても目標に届かない場合はスキップ
            if current_sum + options[i] + 6 * (7 - len(current_combination) - 1) < target:
                continue

            current_combination.append(options[i])
            backtrack(current_combination, current_sum + options[i], i)
            current_combination.pop()

    backtrack([], 0, 0)

    # ピッタリのものを優先し、合計値でソート、その後高得点日の少なさでソート
    results.sort(key=lambda x: (sum(x), x.count(6), x.count(4), -x.count(1)))

    # 代表的なものをいくつかピックアップして返す
    # ユーザーが求めていた [6, 4, 4, 1, 1, 1, 1] などの直感的なものを優先
    # 少しフィルタリングして多様な選択肢を5つ程度返す

    filtered_results: list[tuple[int, ...]] = []
    for r in results:
        # 特徴的な構成を抽出
        if len(filtered_results) < 6:
            filtered_results.append(r)

    # 特定のパターン（ユーザー要望）が含まれていなければ追加
    if target == 18:
        user_req = (6, 4, 4, 1, 1, 1, 1)
        if user_req not in filtered_results:
            filtered_results.insert(0, user_req)
            filtered_results = filtered_results[:6]

    return sorted(list(set(filtered_results)), key=lambda x: (sum(x), x.count(6), x.count(4)), reverse=True)


def calculate_skip_card_balance(
    initial_balance: int, start_date: date, num_days: int, daily_values: list[int | str]
) -> list[int]:
    """
    日ごとのスキップカード残高を計算します。
    - 毎週月曜日に+2枚（上限10枚）
    - 'SKIP'を選択した日に-1枚
    """
    balances = []
    current = initial_balance

    for i in range(num_days):
        current_date = start_date + timedelta(days=i)

        # 月曜日になったら +2 枚 (所持上限 10 枚)
        if current_date.weekday() == 0:
            current = min(10, current + 2)

        # 当日の消費
        if daily_values[i] == "SKIP":
            current = max(0, current - 1)

        balances.append(current)

    return balances


def group_points_by_active_week(daily_values: list[int | str]) -> list[list[int]]:
    """
    'SKIP'を除いた有効な配信日を7日間ずつにまとめます。
    """
    active_points = [p for p in daily_values if p != "SKIP"]

    weeks = []
    for i in range(0, len(active_points), 7):
        week = active_points[i : i + 7]
        # キャスト
        weeks.append([_to_int(p) for p in week])

    return weeks


def get_day_period_assignments(daily_values: list[int | str]) -> list[int]:
    """
    各日付が「第何期（ランク判定周期）」に属するかを返します。
    - SKIPの日は 0
    - 配信日は 1, 1, 1... (7日間分), 2, 2, 2... と割り当て
    """
    assignments = []
    active_count = 0

    for val in daily_values:
        if val == "SKIP":
            assignments.append(0)
        else:
            period = (active_count // 7) + 1
            assignments.append(period)
            active_count += 1

    return assignments


def render_visual_editor(
    bg_bytes: bytes,
    fg_bytes: bytes,
    fg_w: int,
    fg_h: int,
    px: float,
    py: float,
    scale: float,
    anchor: str,
) -> None:
    """
    Fabric.jsを使用したビジュアルエディタをダイアログ内に表示します。
    """
    import base64
    from pathlib import Path

    import streamlit as st
    import streamlit.components.v1 as components

    # アセットの読み込み
    asset_dir = Path("src/assets/palmu")
    html_tmpl = (asset_dir / "editor.html").read_text(encoding="utf-8")
    css_text = (asset_dir / "editor.css").read_text(encoding="utf-8")
    js_text = (asset_dir / "editor.js").read_text(encoding="utf-8")

    bg_b64 = base64.b64encode(bg_bytes).decode()
    fg_b64 = base64.b64encode(fg_bytes).decode()

    # JS内のプレースホルダーを置換
    js_final = (
        js_text.replace("__BG_B64__", bg_b64)
        .replace("__FG_B64__", fg_b64)
        .replace("__ANCHOR__", anchor)
        .replace("__PX__", str(px))
        .replace("__PY__", str(py))
        .replace("__SCALE__", str(scale))
        .replace("__FG_W__", str(fg_w))
        .replace("__FG_H__", str(fg_h))
    )

    # HTML全体の組み立て
    html_final = html_tmpl.replace("__STYLE__", css_text).replace("__SCRIPT__", js_final)

    st.markdown("#### 📱 ビジュアルエディタ")
    st.caption("画像をドラッグして移動、角を引いてサイズ変更できます。")
    components.html(html_final, height=650, scrolling=True)
