/* Palmu Editor JS */
(function() {
    const canvas = new fabric.Canvas('canvas');
    const MAX_DISPLAY_WIDTH = window.innerWidth - 40; // スマホ対応
    let displayScale = 1.0;

    // Streamlitからの変数を注入するためのプレースホルダー
    // 実際にはHTML生成時に文字列置換されます
    const config = {
        bgB64: "__BG_B64__",
        fgB64: "__FG_B64__",
        anchor: "__ANCHOR__",
        px: __PX__,
        py: __PY__,
        scale: __SCALE__,
        fgW: __FG_W__,
        fgH: __FG_H__
    };

    function updateResultText(left, top, scale) {
        document.getElementById('res_x').innerText = Math.round(left);
        document.getElementById('res_y').innerText = Math.round(top);
        document.getElementById('res_scale').innerText = scale.toFixed(2);
    }

    fabric.Image.fromURL('data:image/png;base64,' + config.bgB64, function(bgImg) {
        displayScale = Math.min(1.0, MAX_DISPLAY_WIDTH / bgImg.width);
        const displayWidth = bgImg.width * displayScale;
        const displayHeight = bgImg.height * displayScale;

        canvas.setWidth(displayWidth);
        canvas.setHeight(displayHeight);
        
        bgImg.scale(displayScale);
        canvas.setBackgroundImage(bgImg, canvas.renderAll.bind(canvas));
        
        fabric.Image.fromURL('data:image/png;base64,' + config.fgB64, function(fgImg) {
            const fgOrigW = config.fgW * config.scale;
            const fgOrigH = config.fgH * config.scale;

            let origLeft = config.px;
            let origTop = config.py;

            if (config.anchor === "中央") {
                origLeft = (bgImg.width - fgOrigW) / 2 + config.px;
                origTop = (bgImg.height - fgOrigH) / 2 + config.py;
            } else if (config.anchor === "右上") {
                origLeft = (bgImg.width - fgOrigW) - config.px;
                origTop = config.py;
            } else if (config.anchor === "左下") {
                origLeft = config.px;
                origTop = (bgImg.height - fgOrigH) - config.py;
            } else if (config.anchor === "右下") {
                origLeft = (bgImg.width - fgOrigW) - config.px;
                origTop = (bgImg.height - fgOrigH) - config.py;
            } else if (config.anchor === "中央左") {
                origLeft = config.px;
                origTop = (bgImg.height - fgOrigH) / 2 + config.py;
            } else if (config.anchor === "中央右") {
                origLeft = (bgImg.width - fgOrigW) - config.px;
                origTop = (bgImg.height - fgOrigH) / 2 + config.py;
            } else if (config.anchor === "中央上") {
                origLeft = (bgImg.width - fgOrigW) / 2 + config.px;
                origTop = config.py;
            } else if (config.anchor === "中央下") {
                origLeft = (bgImg.width - fgOrigW) / 2 + config.px;
                origTop = (bgImg.height - fgOrigH) - config.py;
            }

            fgImg.set({
                left: origLeft * displayScale,
                top: origTop * displayScale,
                scaleX: config.scale * displayScale,
                scaleY: config.scale * displayScale,
                selectable: true,
                hasControls: true,
                cornerColor: 'rgba(0,0,255,0.8)',
                cornerSize: 20, // スマホで掴みやすく
                transparentCorners: false
            });

            canvas.add(fgImg);
            canvas.setActiveObject(fgImg);

            // 操作イベント
            const syncValues = () => {
                // 逆計算してオリジナル座標に戻す
                let curLeft = fgImg.left / displayScale;
                let curTop = fgImg.top / displayScale;
                let curScale = fgImg.scaleX / displayScale;

                let finalX = curLeft;
                let finalY = curTop;

                // 基準点に応じた逆算
                if (config.anchor === "中央") {
                    finalX = curLeft - (bgImg.width - fgImg.width * fgImg.scaleX / displayScale) / 2;
                    finalY = curTop - (bgImg.height - fgImg.height * fgImg.scaleY / displayScale) / 2;
                } else if (config.anchor === "右上") {
                    finalX = (bgImg.width - fgImg.width * fgImg.scaleX / displayScale) - curLeft;
                    finalY = curTop;
                } else if (config.anchor === "左下") {
                    finalX = curLeft;
                    finalY = (bgImg.height - fgImg.height * fgImg.scaleY / displayScale) - curTop;
                } else if (config.anchor === "右下") {
                    finalX = (bgImg.width - fgImg.width * fgImg.scaleX / displayScale) - curLeft;
                    finalY = (bgImg.height - fgImg.height * fgImg.scaleY / displayScale) - curTop;
                } else if (config.anchor === "中央左") {
                    finalX = curLeft;
                    finalY = curTop - (bgImg.height - fgImg.height * fgImg.scaleY / displayScale) / 2;
                } else if (config.anchor === "中央右") {
                    finalX = (bgImg.width - fgImg.width * fgImg.scaleX / displayScale) - curLeft;
                    finalY = curTop - (bgImg.height - fgImg.height * fgImg.scaleY / displayScale) / 2;
                } else if (config.anchor === "中央上") {
                    finalX = curLeft - (bgImg.width - fgImg.width * fgImg.scaleX / displayScale) / 2;
                    finalY = curTop;
                } else if (config.anchor === "中央下") {
                    finalX = curLeft - (bgImg.width - fgImg.width * fgImg.scaleX / displayScale) / 2;
                    finalY = (bgImg.height - fgImg.height * fgImg.scaleY / displayScale) - curTop;
                }

                updateResultText(finalX, finalY, curScale);
            };

            fgImg.on('moving', syncValues);
            fgImg.on('scaling', syncValues);
            syncValues();
        });
    });
})();
