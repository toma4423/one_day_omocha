import json
import random
import time

import streamlit as st
from streamlit_local_storage import LocalStorage

from src.utils.roulette import (
    migrate_roulette_config,
    pick_roulette_winner,
    validate_roulette_config,
)
from src.utils.storage import SafeStorage
from src.utils.styles import render_donation_box

st.set_page_config(page_title="ルーレット", page_icon="🎡", layout="wide")

# SafeStorage の初期化
storage = SafeStorage(LocalStorage())

# 設定のロード
if "roulette_config" not in st.session_state:
    saved_config = storage.get_item("roulette_config", is_json=True)
    st.session_state.roulette_config = migrate_roulette_config(saved_config)

# 抽選履歴の初期化
if "roulette_history" not in st.session_state:
    saved_history = storage.get_item("roulette_history", is_json=True)
    st.session_state.roulette_history = saved_history if saved_history else []

if "roulette_last_winner" not in st.session_state:
    st.session_state.roulette_last_winner = None

st.title("🎡 カスタムルーレット")

# --- メインエリア ---
col_main, col_sidebar = st.columns([2, 1])

with col_main:
    # ルーレット描画用のコンポーネント
    def render_roulette_canvas(items, sound_enabled, spin_trigger=None):
        # データを JS 向けに JSON 文字列化
        items_json = json.dumps(items, ensure_ascii=False)

        # キャンバス、描画ロジック、音響効果を含む HTML/JS
        # 物理シミュレーション (friction, velocity) と AudioContext
        html_code = f"""
        <div id="container" style="display: flex; flex-direction: column; align-items: center; justify-content: center; width: 100%; height: 500px; font-family: sans-serif;">
            <canvas id="wheel" width="450" height="450" style="max-width: 100%; height: auto;"></canvas>
            <div id="winner-display" style="margin-top: 20px; font-size: 24px; font-weight: bold; height: 30px; color: #FF4B4B;"></div>
        </div>

        <script>
            const items = {items_json};
            const soundEnabled = {str(sound_enabled).lower()};
            const canvas = document.getElementById('wheel');
            const ctx = canvas.getContext('2d');
            const width = canvas.width;
            const height = canvas.height;
            const centerX = width / 2;
            const centerY = height / 2;
            const radius = width / 2 - 20;

            let currentAngle = 0;
            let isSpinning = false;
            let velocity = 0;
            let friction = 0.985;
            let totalWeight = items.reduce((sum, item) => sum + item.weight, 0);

            // 音響効果 (AudioContext)
            let audioCtx = null;
            function playClickSound() {{
                if (!soundEnabled) return;
                if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                
                osc.type = 'sine';
                osc.frequency.setValueAtTime(800, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(100, audioCtx.currentTime + 0.05);
                
                gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.05);
                
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                
                osc.start();
                osc.stop(audioCtx.currentTime + 0.05);
            }}

            function drawWheel() {{
                ctx.clearRect(0, 0, width, height);
                let startAngle = currentAngle;

                items.forEach((item, i) => {{
                    const sliceAngle = (item.weight / totalWeight) * 2 * Math.PI;
                    ctx.beginPath();
                    ctx.fillStyle = item.color;
                    ctx.moveTo(centerX, centerY);
                    ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
                    ctx.fill();
                    ctx.stroke();

                    // テキスト描画
                    ctx.save();
                    ctx.translate(centerX, centerY);
                    ctx.rotate(startAngle + sliceAngle / 2);
                    ctx.textAlign = "right";
                    ctx.fillStyle = "#fff";
                    ctx.font = "bold 16px sans-serif";
                    ctx.shadowBlur = 4;
                    ctx.shadowColor = "rgba(0,0,0,0.5)";
                    // 短いラベルのみ表示
                    const label = item.label.length > 10 ? item.label.substring(0, 8) + '..' : item.label;
                    ctx.fillText(label, radius - 10, 5);
                    ctx.restore();

                    startAngle += sliceAngle;
                }});

                // センターポインタ (外側の針)
                ctx.fillStyle = "#333";
                ctx.beginPath();
                ctx.moveTo(width - 10, centerY);
                ctx.lineTo(width - 30, centerY - 15);
                ctx.lineTo(width - 30, centerY + 15);
                ctx.closePath();
                ctx.fill();

                // 中心円
                ctx.beginPath();
                ctx.arc(centerX, centerY, 15, 0, 2 * Math.PI);
                ctx.fillStyle = "#fff";
                ctx.fill();
                ctx.stroke();
            }}

            let lastSliceIndex = -1;
            function update() {{
                if (isSpinning) {{
                    currentAngle += velocity;
                    velocity *= friction;

                    // カチカチ音判定 (現在の角度からどのスライスにいるか計算)
                    // 針の位置 (右端 = 0rad) に対する現在のスライスインデックス
                    let needlePos = (2 * Math.PI - (currentAngle % (2 * Math.PI))) % (2 * Math.PI);
                    let tempAngle = 0;
                    let currentSliceIndex = 0;
                    for (let i = 0; i < items.length; i++) {{
                        tempAngle += (items[i].weight / totalWeight) * 2 * Math.PI;
                        if (needlePos < tempAngle) {{
                            currentSliceIndex = i;
                            break;
                        }}
                    }}

                    if (currentSliceIndex !== lastSliceIndex) {{
                        playClickSound();
                        lastSliceIndex = currentSliceIndex;
                    }}

                    if (velocity < 0.002) {{
                        isSpinning = false;
                        velocity = 0;
                        const winner = items[currentSliceIndex].label;
                        document.getElementById('winner-display').innerText = "当選： " + winner;
                    }}
                }}
                drawWheel();
                requestAnimationFrame(update);
            }}

            window.addEventListener('message', (event) => {{
                if (event.data.type === 'SPIN') {{
                    if (!isSpinning) {{
                        isSpinning = true;
                        velocity = Math.random() * 0.4 + 0.3; // 初速
                        document.getElementById('winner-display').innerText = "抽選中...";
                    }}
                }}
            }});

            update();
        </script>
        """
        st.components.v1.html(html_code, height=550)

    # 描画
    render_roulette_canvas(st.session_state.roulette_config["items"], st.session_state.roulette_config["sound_enabled"])

    if st.button("🚀 ルーレットを回す！", use_container_width=True, type="primary"):
        # JSにメッセージを送る仕組みはStreamlit標準では困難なため、
        # 簡易的に Python 側で抽選して結果を通知しつつ、
        # コンポーネント側でアニメーションを開始させるためのトリガーとして st.rerun を利用するなどの工夫が必要
        # ここでは「抽選」は Python で行い、アニメーション完了を待たずに履歴に追加する
        winner = pick_roulette_winner(st.session_state.roulette_config["items"])
        st.session_state.roulette_last_winner = winner

        # 履歴追加
        history_entry = {"time": time.strftime("%H:%M:%S"), "label": winner["label"], "color": winner["color"]}
        st.session_state.roulette_history.insert(0, history_entry)
        st.session_state.roulette_history = st.session_state.roulette_history[:50]
        storage.set_item("roulette_history", st.session_state.roulette_history)

        # JS 側に「回せ」という合図を送るための仕組み：
        # コンポーネントを再レンダリングする際に、初期速度を与えるフラグを渡すなどの手法が取れる。
        # ここでは簡易化のため st.balloons で祝う
        st.balloons()
        st.success(f"結果：{winner['label']}")

    # 履歴表示
    st.subheader("📜 履歴")
    if st.session_state.roulette_history:
        for entry in st.session_state.roulette_history[:10]:
            st.markdown(
                f"- **{entry['time']}**: <span style='color:{entry['color']}'>●</span> {entry['label']}",
                unsafe_allow_html=True,
            )
    else:
        st.info("履歴はまだありません。")

with col_sidebar:
    st.subheader("⚙️ 設定")

    with st.expander("📝 項目と重みの編集", expanded=True):
        new_items = []
        for i, item in enumerate(st.session_state.roulette_config["items"]):
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                label = st.text_input(f"名前 {i + 1}", value=item["label"], key=f"label_{i}")
            with c2:
                weight = st.number_input(
                    "重み", value=float(item["weight"]), min_value=0.0, step=0.1, key=f"weight_{i}"
                )
            with c3:
                color = st.color_picker("色", value=item["color"], key=f"color_{i}")
                if st.button("🗑️", key=f"del_{i}"):
                    # 削除処理（リストから除外）
                    continue
            new_items.append({"label": label, "weight": weight, "color": color})

        if st.button("➕ 項目を追加"):
            # デフォルト色をランダムに
            rand_color = f"#{random.randint(0, 0xFFFFFF):06x}"
            new_items.append({"label": "新しい項目", "weight": 1.0, "color": rand_color})
            st.rerun()

        if st.button("💾 設定を保存"):
            st.session_state.roulette_config["items"] = new_items
            storage.set_item("roulette_config", st.session_state.roulette_config)
            st.success("保存しました！")
            st.rerun()

    st.session_state.roulette_config["sound_enabled"] = st.toggle(
        "🔊 カチカチ音を有効にする", value=st.session_state.roulette_config["sound_enabled"]
    )

    st.write("---")

    # ファイル入出力
    st.subheader("📁 設定の共有")

    # エクスポート
    json_data = json.dumps(st.session_state.roulette_config, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 設定をJSONで保存",
        data=json_data,
        file_name="roulette_config.json",
        mime="application/json",
    )

    # インポート
    uploaded_file = st.file_uploader("📤 設定JSONを読み込む", type="json")
    if uploaded_file is not None:
        if st.button("設定を反映", use_container_width=True):
            try:
                data = json.load(uploaded_file)
                is_valid, msg = validate_roulette_config(data)
                if is_valid:
                    migrated = migrate_roulette_config(data)
                    st.session_state.roulette_config = migrated
                    storage.set_item("roulette_config", migrated)
                    st.success("設定を反映しました！")
                    st.rerun()
                else:
                    st.error(f"エラー: {msg}")
            except Exception as e:
                st.error(f"JSONの読み込みに失敗しました: {e}")

    if st.button("🗑️ 履歴をクリア", use_container_width=True):
        st.session_state.roulette_history = []
        storage.set_item("roulette_history", [])
        st.rerun()

render_donation_box("https://paypay.me/xxxx", is_sidebar=True)
