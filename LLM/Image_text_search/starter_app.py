import gradio as gr
from transformers import BlipProcessor, BlipForConditionalGeneration, BlipForQuestionAnswering
from PIL import Image
import torch

# Load models and processor
caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
vqa_model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")

def process_image(img):
    """Generate a caption for the uploaded image."""
    inputs = processor(images=img, return_tensors="pt")
    out = caption_model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    return caption

def answer_question(img, question):
    """Answer a question about the image."""
    inputs = processor(images=img, text=question, return_tensors="pt")
    out = vqa_model.generate(**inputs)
    answer = processor.decode(out[0], skip_special_tokens=True)
    return answer

def full_pipeline(img, question):
    caption = process_image(img)
    answer = answer_question(img, question)
    return caption, answer

# Build Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("## 🖼️ Image Captioning + Visual Question Answering (BLIP)")
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(type="pil")
            question_input = gr.Textbox(label="Ask a question about the image")
            run_btn = gr.Button("Generate Caption + Answer")
        with gr.Column():
            caption_output = gr.Textbox(label="Generated Caption")
            answer_output = gr.Textbox(label="Answer to Question")

    run_btn.click(fn=full_pipeline, inputs=[image_input, question_input], outputs=[caption_output, answer_output])

demo.launch() #share=True)
