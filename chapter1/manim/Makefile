# 第1章の図解アニメーションを描画し、chapter1/web/media/ に MP4 とポスター画像を書き出す
#   make            : すべてのシーンを 1080p30 で描画
#   make ../web/media/ch1_xxx.mp4 : 1 本だけ描画
#   make preview    : 480p15 で素早く確認（web/media には書き出さない）
#   make MANIM=...  : manim コマンドのパスを指定（既定は PATH 上の manim）

MANIM  ?= manim
FFMPEG ?= $(dir $(shell command -v $(MANIM)))ffmpeg
BUILD  := build
OUT    := ../web/media

# 出力ファイル名:シーンファイル:シーンクラス
SCENES := \
	ch1_self_attention:self_attention.py:SelfAttentionScene \
	ch1_xor_relu:xor_relu.py:XorReluScene \
	ch1_gradient_descent:gradient_descent.py:GradientDescentScene \
	ch1_causal_mask:causal_mask.py:CausalMaskScene \
	ch1_rnn_vs_attention:rnn_vs_attention.py:RnnVsAttentionScene \
	ch1_embedding:embedding.py:EmbeddingScene \
	ch1_temperature:temperature.py:TemperatureScene \
	ch1_top_p:top_p.py:TopPScene

.PHONY: all preview clean
all: $(foreach s,$(SCENES),$(OUT)/$(word 1,$(subst :, ,$(s))).mp4)

define RULE
$(OUT)/$(1).mp4: scenes/$(2) scenes/theme.py
	cd scenes && $(MANIM) render -r 1920,1080 --fps 30 --media_dir ../$(BUILD) -o $(1) $(2) $(3)
	mkdir -p $(OUT)
	$(FFMPEG) -loglevel error -y -i $(BUILD)/videos/$(basename $(2))/1080p30/$(1).mp4 -c copy -movflags +faststart $$@
	$(FFMPEG) -loglevel error -y -sseof -0.5 -i $$@ -frames:v 1 -vf scale=1280:-1 $(OUT)/$(1).jpg
endef
$(foreach s,$(SCENES),$(eval $(call RULE,$(word 1,$(subst :, ,$(s))),$(word 2,$(subst :, ,$(s))),$(word 3,$(subst :, ,$(s))))))

preview:
	cd scenes && for s in $(SCENES); do f=$$(echo $$s | cut -d: -f2); c=$$(echo $$s | cut -d: -f3); \
		$(MANIM) render -ql --media_dir ../$(BUILD) $$f $$c || exit 1; done

clean:
	rm -rf $(BUILD)
