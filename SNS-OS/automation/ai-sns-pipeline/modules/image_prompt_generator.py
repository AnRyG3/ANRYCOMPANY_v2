def generate_image_prompts(idea, script_data):
    theme = idea.get("theme", "")
    return {
        "gemini_prompt": (
            f"Instagramリール用の医療系イラストを作成してください。テーマは「{theme}」。"
            "白背景、青・水色系、清潔感、一般人にも怖くない雰囲気、9:16、文字なし。"
        ),
        "image_generation_prompt": (
            f"Create a clean Japanese medical explainer visual for vertical short video. Theme: {theme}. "
            "White background, blue accents, friendly radiologic technologist, no text, 9:16."
        ),
        "thumbnail": f"{theme}｜実は？",
        "composition": "上部に大きなタイトル、中央に医療イラスト、下部に安心感のある補足。"
    }
