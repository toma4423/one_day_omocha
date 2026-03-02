/* Palmu Editor JS */
(function() {
    const canvas = new fabric.Canvas('canvas');
    
    const MAX_DISPLAY_WIDTH = Math.min(500, window.innerWidth * 0.9);
    const MAX_DISPLAY_HEIGHT = 400; 
    let displayScale = 1.0;

    const config = {
        bgB64: "__BG_B64__",
        fgB64: "__FG_B64__",
        anchor: "__ANCHOR__",
        px: __PX__,
        py: __PY__,
        scale: __SCALE__,
        fgW: __FG_W__,
        fgH: __FG_H__,
        mode: "__MODE__"
    };

    function updateResultText(left, top, scale) {
        const x = Math.round(left);
        const y = Math.round(top);
        const s = parseFloat(scale.toFixed(2));

        document.getElementById('res_x').innerText = x;
        document.getElementById('res_y').innerText = y;
        document.getElementById('res_scale').innerText = s;

        // OKリンクの飛び先をリアルタイムで生成
        // 親画面のURLを取得してパラメータを付与
        try {
            const url = new URL(window.parent.location.href);
            url.searchParams.set('palmu_x', x);
            url.searchParams.set('palmu_y', y);
            url.searchParams.set('palmu_s', s);
            url.searchParams.set('palmu_sync', '1');
            document.getElementById('ok_link').href = url.href;
        } catch (e) {
            // 親のURLが取れない場合は、現在のURLベースで暫定作成 (Streamlitの仕様に合わせる)
            const url = new URL(window.location.href);
            url.searchParams.set('palmu_x', x);
            url.searchParams.set('palmu_y', y);
            url.searchParams.set('palmu_s', s);
            url.searchParams.set('palmu_sync', '1');
            document.getElementById('ok_link').href = url.href;
        }
    }

    fabric.Image.fromURL('data:image/png;base64,' + config.bgB64, function(bgImg) {
        const scaleW = MAX_DISPLAY_WIDTH / bgImg.width;
        const scaleH = MAX_DISPLAY_HEIGHT / bgImg.height;
        displayScale = Math.min(scaleW, scaleH, 1.0); 
        
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
                cornerSize: 24,
                transparentCorners: false
            });

            canvas.add(fgImg);
            canvas.setActiveObject(fgImg);

            const syncValues = () => {
                let curLeft = fgImg.left / displayScale;
                let curTop = fgImg.top / displayScale;
                let curScale = fgImg.scaleX / displayScale;

                let finalX = curLeft;
                let finalY = curTop;

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
