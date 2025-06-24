import pytesseract
from PIL import Image
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import gradio as gr

# Load flan-t5-small summarization model (CPU mode)
model_id = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=-1)

def ocr_and_summarize(image):
    if image is None:
        return "Please upload an image."

    # OCR step
    text = pytesseract.image_to_string(image)

    if len(text.strip()) == 0:
        return "No text detected in the image."

    # Summarization prompt (Flan-T5 expects raw text input)
    summary_list = summarizer(text, max_length=150, min_length=30, do_sample=False)
    summary = summary_list[0]['summary_text']

    return f"📝 Extracted Text:\n{text}\n\n📄 Summary:\n{summary}"

demo = gr.Interface(
    fn=ocr_and_summarize,
    inputs=gr.Image(type="pil", label="Upload an image (e.g., receipt, document, sign)"),
    outputs="text",
    title="OCR + Summarization (Flan-T5 Small, CPU)",
    description="Extract text from image and summarize using the open-source Flan-T5 Small model running on CPU."
)

if __name__ == "__main__":
    demo.launch()
